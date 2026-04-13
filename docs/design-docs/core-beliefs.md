# Core Beliefs

`quantcraft` follows these agent-first repository beliefs:

- repository docs are the system of record
- the repo entry contract must be self-contained and executable without knowing
  any host-specific command surface
- a short `AGENTS.md` should point to structured docs instead of duplicating
  them
- planner, generator, and evaluator responsibilities should stay distinct even
  when one operator performs more than one role
- active plans and trial records are structured artifacts, not chat residue
- repeated review findings should be promoted into the right governing doc or a
  narrow mechanical check when they prove durable
- architecture rules should be mechanically checkable
- evaluation governance lives in [architecture-governance.md](architecture-governance.md)
- evaluator artifacts should surface failure modes rather than simulate final
  approval
- legacy scorecards, promotion logs, and archived plan indexes are not workflow
  authority; if retained, they must be clearly marked historical or advisory
- financial high-scrutiny domains need stronger human gate
- remove control-plane complexity only after proving it is non-load-bearing
