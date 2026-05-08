from __future__ import annotations

import math
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType, NoneType, UnionType
from typing import TypeAlias, Union, cast, get_args, get_origin, get_type_hints

JSONConfigScalar: TypeAlias = str | int | float | bool | None
_SupportedType: TypeAlias = type[str] | type[int] | type[float] | type[bool]


class StrategyConfigError(Exception):
    """Base error for strategy configuration contract failures."""


class StrategyConfigDeclarationError(StrategyConfigError):
    """Raised when a strategy config class or strategy declaration is invalid."""


class StrategyConfigValidationError(StrategyConfigError):
    """Raised when config values do not fit a declared strategy config schema."""


class StrategyConfigMutationError(StrategyConfigError):
    """Raised when a materialized config snapshot is mutated."""


@dataclass(frozen=True, slots=True)
class _ConfigField:
    name: str
    annotation: object
    value_type: _SupportedType
    optional: bool
    default: JSONConfigScalar


class StrategyConfig:
    __config_fields__: tuple[_ConfigField, ...] = ()
    __config_field_names__: frozenset[str] = frozenset()

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        inherited_fields: dict[str, _ConfigField] = {}
        inherited_order: list[str] = []
        for base in reversed(cls.__mro__[1:]):
            for field in getattr(base, "__config_fields__", ()):
                if field.name not in inherited_fields:
                    inherited_order.append(field.name)
                inherited_fields[field.name] = field

        annotations = cls.__dict__.get("__annotations__", {})
        public_annotation_names = tuple(name for name in annotations if not name.startswith("_"))
        type_hints = _public_type_hints(cls, public_annotation_names)
        fields = dict(inherited_fields)
        order = list(inherited_order)
        for name in public_annotation_names:
            if name not in cls.__dict__:
                raise StrategyConfigDeclarationError(
                    f"{cls.__name__}.{name} requires a default value"
                )
            value_type, optional = _resolve_supported_annotation(type_hints[name], cls, name)
            default = cls.__dict__[name]
            _validate_config_value(
                field_name=name,
                value=default,
                value_type=value_type,
                optional=optional,
                error_type=StrategyConfigDeclarationError,
            )
            if name not in fields:
                order.append(name)
            fields[name] = _ConfigField(
                name=name,
                annotation=type_hints[name],
                value_type=value_type,
                optional=optional,
                default=default,
            )

        ordered_fields = tuple(fields[name] for name in order if name in fields)
        cls.__config_fields__ = ordered_fields
        cls.__config_field_names__ = frozenset(field.name for field in ordered_fields)

    def __init__(self, **overrides: JSONConfigScalar) -> None:
        values: dict[str, JSONConfigScalar] = {
            field.name: field.default for field in self.__config_fields__
        }
        for name, value in overrides.items():
            field = self._field_for_override(name)
            _validate_config_value(
                field_name=name,
                value=value,
                value_type=field.value_type,
                optional=field.optional,
                error_type=StrategyConfigValidationError,
            )
            values[name] = value

        object.__setattr__(self, "_values", MappingProxyType(values))
        object.__setattr__(self, "_frozen", True)

    def __getattribute__(self, name: str) -> object:
        if not name.startswith("_"):
            try:
                field_names = object.__getattribute__(self, "__config_field_names__")
                values = object.__getattribute__(self, "_values")
            except AttributeError:
                pass
            else:
                if name in field_names:
                    return values[name]
        return object.__getattribute__(self, name)

    def __setattr__(self, name: str, value: object) -> None:
        if object.__getattribute__(self, "__dict__").get("_frozen", False):
            raise StrategyConfigMutationError(
                f"StrategyConfig snapshots are immutable; cannot assign {name!r}"
            )
        object.__setattr__(self, name, value)

    def __delattr__(self, name: str) -> None:
        if object.__getattribute__(self, "__dict__").get("_frozen", False):
            raise StrategyConfigMutationError(
                f"StrategyConfig snapshots are immutable; cannot delete {name!r}"
            )
        object.__delattr__(self, name)

    def to_mapping(self) -> dict[str, JSONConfigScalar]:
        values: Mapping[str, JSONConfigScalar] = object.__getattribute__(self, "_values")
        return dict(values)

    @classmethod
    def _field_for_override(cls, name: str) -> _ConfigField:
        for field in cls.__config_fields__:
            if field.name == name:
                return field
        raise StrategyConfigValidationError(f"unknown strategy config field: {name}")


def _resolve_supported_annotation(
    annotation: object,
    cls: type[StrategyConfig],
    field_name: str,
) -> tuple[_SupportedType, bool]:
    origin = get_origin(annotation)
    args = get_args(annotation)
    optional = False
    candidate = annotation
    if origin in {Union, UnionType}:
        non_none_args = tuple(arg for arg in args if arg is not NoneType)
        if len(non_none_args) != 1 or len(non_none_args) == len(args):
            raise StrategyConfigDeclarationError(
                f"{cls.__name__}.{field_name} uses an unsupported annotation"
            )
        optional = True
        candidate = non_none_args[0]

    if candidate not in {str, int, float, bool}:
        raise StrategyConfigDeclarationError(
            f"{cls.__name__}.{field_name} uses an unsupported annotation"
        )
    return cast(_SupportedType, candidate), optional


def _public_type_hints(cls: type[StrategyConfig], names: tuple[str, ...]) -> dict[str, object]:
    if not names:
        return {}
    module_globals = vars(sys.modules[cls.__module__])
    public_annotations = {name: cls.__annotations__[name] for name in names}
    namespace = dict(vars(cls))
    namespace["__annotations__"] = public_annotations
    public_only_cls = type(f"_{cls.__name__}PublicAnnotations", (), namespace)
    return get_type_hints(public_only_cls, globalns=module_globals, localns=namespace)


def _validate_config_value(
    *,
    field_name: str,
    value: object,
    value_type: _SupportedType,
    optional: bool,
    error_type: type[StrategyConfigDeclarationError] | type[StrategyConfigValidationError],
) -> None:
    if value is None:
        if optional:
            return
        raise error_type(f"{field_name} does not allow None")

    if value_type is bool:
        if type(value) is bool:
            return
        raise error_type(f"{field_name} expects bool")

    if value_type is int:
        if type(value) is int:
            return
        raise error_type(f"{field_name} expects int")

    if value_type is float:
        if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value):
            return
        raise error_type(f"{field_name} expects finite float")

    if value_type is str:
        if type(value) is str:
            return
        raise error_type(f"{field_name} expects str")
