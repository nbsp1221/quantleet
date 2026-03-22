# Quantcraft 거래 커널 계약 초안 v1 (한국어)

## 상태

- 상태: `draft`
- 목적: `trading` 커널의 공통 의미론과 전략/이벤트 계약을 한국어로 정리하는 작업 문서
- 범위: backtest, paper, live가 공유해야 하는 거래 의미론과 MVP 제약

## 왜 별도 문서로 분리하는가

최상위 아키텍처와 거래 커널 계약은 다르다.

- 아키텍처 문서는 경계와 책임을 다룬다.
- 이 문서는 전략 API, 이벤트 shape, 백테스트와 엔진의 연결 방식처럼 `trading`에 특화된 계약을 다룬다.

이 둘을 한 문서에 계속 쌓아두면 에이전트가 최상위 구조와 거래 세부 계약을 같은 수준의 규칙으로 오해하기 쉽다.

## 공통 거래 의미론에 대한 핵심 원칙

### 1. 세 환경은 같은 거래 커널을 공유해야 한다

백테스트, 페이퍼 트레이딩, 실매매는 서로 다른 거래 엔진이 아니라 같은 거래 커널을 다른 입력 환경에서 돌리는 구조를 지향한다.

공유되어야 하는 것:

- 주문 의사결정 해석
- 체결 의미론
- 포지션/잔고/포트폴리오 상태 전이
- 리스크 판단의 핵심 규칙
- 이벤트 처리 순서

### 2. `portfolio`와 `risk`는 `trading` 커널에 속한다

이 둘은 `execution`의 부속물이 아니라 공통 거래 의미론의 일부로 본다.

이유:

- 백테스트 결과와 실매매 결과가 최대한 같은 의미론 위에 있어야 한다.
- 포트폴리오와 리스크 해석이 환경마다 달라지면 이 요구를 만족시킬 수 없다.

### 3. 엔진 내부는 `tick/event-driven`이다

전략이 `on_bar`를 지원하더라도 내부 엔진은 봉 기반 엔진이 아니라 이벤트 기반 엔진이어야 한다.

즉:

- 내부 엔진: `tick/event-driven`
- 사용자 전략 인터페이스: `on_tick`, `on_bar`

## 전략 계약

### 전략의 출력은 `OrderIntent`다

전략은 너무 추상적인 `Signal`만 내는 것이 아니라 주문 의도 수준까지는 책임진다.

즉 전략은 최소한 다음을 표현할 수 있어야 한다.

- 진입 / 청산 의도
- 방향
- 수량 의도
- 주문 관련 의도 표현

하지만 실제 주문 상태 전이, 체결 반영, 잔고/포지션 반영은 여전히 `trading` 커널이 맡는다.

현재 backtest MVP의 좁은 기본값은 다음 필드를 사용한다.

- `symbol`
- `side`
- `quantity`
- `order_type`
- `limit_price?`
- `tag?`

### 전략 인터페이스는 `self` 기반으로 간다

사용자-facing API는 `ctx`보다 `self` 기반으로 간다.

예상 감각:

- `self.trade.entry(...)`
- `self.trade.exit(...)`

내부적으로는 실행 컨텍스트와 엔진 상태가 별도 객체에 있을 수 있지만, 사용자 계약은 `self` 기반으로 유지한다.

### 전략 훅은 `on_tick`, `on_bar`를 제공할 수 있다

전략은 다음 두 훅을 가질 수 있다.

- `on_tick`
- `on_bar`

다시 강조하면, 이것은 사용자-facing 콜백 모델이며 내부 엔진 실행 모델은 계속 `tick/event-driven`이다.

## 초기 canonical event set

현재 합의된 `v1` canonical event set은 다음 최소 집합이다.

- `TickEvent`
- `BarEvent`
- `OrderEvent`
- `FillEvent`
- `TimerEvent`

현재 backtest MVP의 좁은 기본값에서 `FillEvent`는 다음 최소 필드를 가진다.

- `symbol`
- `side`
- `quantity`
- `price`
- `timestamp`
- `fee`

파생 회계 값(예: closing PnL)은 `FillEvent`가 아니라 포지션 반영/리포트 계층에서 계산한다.

현재 승인된 한국어 MVP 기준선에서 `BarEvent`는 TimeBar 전용 이벤트가 아니라, 완성된 일반 bar aggregation 이벤트로 본다.

현재 승인된 MVP 기본 필드는 다음과 같다.

- `bar_type`
- `bar_spec`
- `symbol`
- `timestamp`
- `open`
- `high`
- `low`
- `close`
- `volume`
- `is_closed`

지금은 다음 이벤트를 정식 표준으로 확정하지 않는다.

- `SignalEvent`
- `RiskEvent`
- `PortfolioEvent`
- `PositionEvent`

## `TickEvent`의 canonical shape

`v1`에서 `TickEvent`는 `L2 snapshot`을 canonical shape로 사용한다.

최소 표현 대상:

- `timestamp`
- `symbol`
- `bids[]`
- `asks[]`
- `last`
- `last_size?`

이렇게 두는 이유:

- 실시간 거래소 오더북을 자연스럽게 표현할 수 있다.
- 페이퍼 트레이딩에서 실제 호가 기반 체결 모델링이 가능하다.
- 백테스트에서는 `bids/asks` 길이를 1로 둔 단순 book으로 축소할 수 있다.

## 백테스트와 엔진의 연결 방식

백테스트는 별도 거래 엔진을 만드는 방식이 아니라, 같은 엔진에 다른 입력 이벤트를 넣는 방식으로 본다.

즉:

- `live / paper`
  - 실시간 시장 이벤트와 실제/가상 execution event를 넣는다.
- `backtest`
  - 과거 데이터 기반으로 synthetic tick/event를 생성해서 넣는다.

OHLCV는 백테스트 입력 원천이 될 수는 있지만, 엔진의 최종 실행 단위는 여전히 event/tick이어야 한다.

## 백테스트 MVP에 대한 현재 합의

초기 구현 슬라이스는 `백테스트 MVP`로 잡는다. 다만 이 MVP는 봉 기반 장난감 엔진이 아니라, 공통 거래 커널을 검증하는 첫 수직 슬라이스여야 한다.

현재 합의:

- 외부 저장 포맷은 일단 `OHLCV`만 지원한다.
- 백테스트 어댑터가 `OHLCV -> synthetic L2 tick stream`으로 변환해서 엔진에 넣는다.
- 엔진 내부는 처음부터 `tick/L2 event-driven`을 유지한다.
- 초기 단순화는 기능 범위를 줄이는 것이지 엔진 의미론을 bar 기반으로 낮추는 것이 아니다.

## 경계 스키마와 core object

canonical book/event object는 `in-memory core contract`로 본다.

- 입력/저장/직렬화 포맷은 `boundary schema`
- boundary에서 정규화한 뒤 core object로 변환
- core 내부에서는 단순한 수학 표현을 허용할 수 있다.

이 원칙은 이후 file, DB, network, notebook 경계를 늘릴 때도 동일하게 적용한다.

## 초기 백테스트 book 단순화

초기 백테스트는 `배열 기반 L2 엔진`을 유지하되, 입력 book을 단순화해서 시작한다.

현재 방향:

- `bids`, `asks`는 계속 배열이다.
- 초기 synthetic book은 각 side 길이가 1인 배열일 수 있다.
- 초기에는 개념적으로 무한 유동성을 가진 단순 book을 허용한다.
- 하지만 엔진 로직 자체는 배열과 수량을 일반적으로 처리할 수 있어야 한다.

즉, 나중에 partial fill이나 다중 레벨 depth를 넣더라도 엔진 코드를 갈아엎지 않도록 추상화를 먼저 맞춘다.

## 현재 MVP 경로/갭 기본값

현재 backtest MVP의 좁은 기본값은 다음을 사용한다.

- bullish bar: `open -> low -> high -> close`
- bearish bar: `open -> high -> low -> close`
- `prev_close -> open`은 별도 gap 세그먼트로 본다
- gap 내부의 중간 가격 체결은 허용하지 않고, `open`을 첫 실행 가능 가격으로 본다
- same-bar에서 새로 활성화된 자식 주문은 bar 전체가 아니라 부모 fill 이후의 tail만 평가한다

## 이 문서에서 아직 확정하지 않는 것

다음은 장기 거래 커널 canonical contract로는 아직 확정하지 않는다.

- `OrderIntent`의 정확한 canonical schema
- `OrderEvent`, `FillEvent`의 정확한 장기 canonical payload
- `BarEvent`의 장기 canonical payload와 `bar_spec`의 정확한 타입 구조
- 콜백 안에서 생성된 `OrderIntent`가 정확히 언제부터 효력을 갖는지
- synthetic tick generator의 시간 순서와 보수성 규칙
- limit / market fill의 세부 가격 결정 규칙
- 무한 유동성의 정확한 in-memory 표현 방식

단, 첫 구현 슬라이스에 대해서는 product spec에서 더 좁은 기본값을 둘 수 있다.

현재 backtest MVP용 좁은 기본값은 다음 문서에서 추적한다.

- [`../product-specs/backtest-mvp.md`](../product-specs/backtest-mvp.md)

## 한 줄 요약

`trading`은 backtest, paper, live가 공유하는 공통 거래 커널이며, 내부 엔진은 `tick/event-driven`, 전략 계약은 `self` 기반 `on_tick / on_bar`와 `OrderIntent`, canonical 입력은 `L2 snapshot`이라는 점을 먼저 고정한다.
