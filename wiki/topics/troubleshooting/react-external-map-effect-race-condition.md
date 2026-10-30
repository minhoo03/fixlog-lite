---
id: topic-react-external-map-effect-race-condition
title: React Effect 재구독과 비동기 응답으로 발생하는 외부 지도 상태 불일치
summary: React Effect가 외부 지도 이벤트 리스너를 재구독하는 순간 동기 이벤트가 유실되고, 늦은 위치 응답이 최신 사용자 선택을 덮어쓴 문제를 render·commit·Effect lifecycle·state snapshot 관점에서 분석한다.
aliases:
  - React 지도 center changed 이벤트 유실
  - useEffect 이벤트 리스너 재구독 경쟁 조건
  - 외부 지도 React 상태 불일치
  - stale closure 위치 요청 덮어쓰기
tags:
  - react
  - use-effect
  - use-ref
  - google-maps
  - race-condition
  - stale-closure
  - external-state
  - debugging
type: topic
status: active
created: 2026-10-30
updated: 2026-10-30
index: true
related:
  - topic-frontend-web-mobile-core-concepts
---

# React Effect 재구독과 비동기 응답으로 발생하는 외부 지도 상태 불일치

## 핵심 요약

- 단순한 리렌더링 지연이 아니라, React Effect의 이벤트 재구독 시점과 외부 지도 API의 동기 이벤트가 충돌한 문제다.
- 지도는 새 중심으로 이동했지만 중심 변경 이벤트를 받을 리스너가 잠시 없어, React가 관리하는 핀·주소·관련 데이터는 이전 위치에 남았다.
- 위치 요청이 기다리는 동안 사용자가 지도를 움직이거나 다음 작업을 진행하면, 늦게 도착한 응답이 최신 선택을 덮어쓰는 별도의 race condition도 발생할 수 있다.
- 프로그램이 이미 알고 있는 좌표는 이벤트로 되돌려 받지 않고 직접 반영하며, 비동기 결과는 완료 시점에도 유효한지 확인한 뒤 적용한다.

## 증상

현재 위치로 이동하는 동작 이후 다음과 같은 불일치가 발생했다.

```text
외부 지도의 중심: 새 위치
React가 관리하는 핀·주소·관련 데이터: 이전 위치
```

지도 중심 변경 이벤트가 발생하지 않은 것이 아니다. 이벤트 발생 시점에 이를 처리할 리스너가 없었다.

## 원인 1: Effect 재구독 구간의 동기 이벤트 유실

외부 지도 래퍼는 일반적으로 Effect로 이벤트 리스너를 관리한다.

```ts
useEffect(() => {
  const listener = map.addListener("center_changed", onCenterChanged);

  return () => listener.remove();
}, [map, onCenterChanged]);
```

React 공식 문서에 따르면 state update는 render를 요청하고, React는 계산한 결과를 commit한 뒤 Effect로 외부 시스템과 동기화한다. dependency가 변경된 Effect는 이전 값으로 cleanup을 실행한 다음 새 값으로 setup을 실행한다.

또한 dependency는 `Object.is`로 비교된다. 컴포넌트 본문에서 만든 인라인 함수는 렌더마다 새로운 객체이므로, 내용이 같아도 변경된 dependency로 판단된다.

```ts
const first = () => updateLocation();
const second = () => updateLocation();

Object.is(first, second); // false
```

문제가 발생한 순서는 다음과 같다.

```text
현재 위치 이동 요청
→ React state의 지도 중심 변경
→ 새로운 이벤트 핸들러를 가진 렌더 생성
→ 기존 이벤트 리스너 cleanup
→ 외부 지도에 setCenter 실행
→ center_changed 이벤트 동기 발생
→ 아직 새 리스너가 없어 이벤트 유실
→ 새 이벤트 리스너 setup
```

이 현상을 React의 보편적인 Effect 문제로 일반화하면 안 된다. 다음 조건이 함께 존재했기 때문에 발생했다.

- 외부 래퍼의 Effect 선언과 실행 순서
- callback을 Effect dependency로 사용하는 구독 방식
- 렌더마다 달라지는 callback 참조
- 외부 API가 상태 변경 이벤트를 동기적으로 발생시키는 동작

Effect 간 세부 실행 순서에 비즈니스 로직이 의존하는 구조는 취약하다. 외부 라이브러리의 현재 동작은 회귀 테스트로 고정하되, 애플리케이션 로직은 해당 순서에 의존하지 않는 편이 안전하다.

## 원인 2: 늦은 비동기 응답과 State Snapshot

React에서 각 렌더는 고유한 state snapshot을 가진다. 해당 렌더에서 생성된 이벤트 핸들러와 비동기 함수는 이후 state가 변경돼도 당시 값을 closure로 기억할 수 있다.

```text
위치 요청 시작
→ await
→ 사용자가 지도를 이동하거나 다음 작업을 진행
→ 새로운 state로 리렌더링
→ 과거 요청 완료
→ 과거 결과가 최신 사용자 선택을 덮어씀
```

따라서 비동기 결과는 도착했다는 이유만으로 적용하지 않는다. 완료 시점에도 요청이 유효한지 다시 확인해야 한다.

## 해결 원칙

### 알고 있는 값은 직접 반영한다

프로그램이 이미 새 좌표를 알고 있다면 외부 지도가 같은 값을 이벤트로 다시 알려주기를 기다리지 않는다.

```ts
const point = await locateCurrentPosition(isStillValid);

if (point) {
  applySelectedPoint(point);
}
```

- 사용자 드래그처럼 외부 시스템이 변경의 출발점이면 이벤트를 사용한다.
- 프로그램이 시작한 변경이면 이미 알고 있는 값을 지도와 React 상태에 함께 반영한다.
- 핀과 관련 데이터는 하나의 함수에서 갱신해 서로 다른 위치를 가리키지 않도록 한다.

### 비동기 결과의 최신 유효성을 확인한다

다음 정보는 ref에 보관해 비동기 작업 완료 시 최신 상태를 확인할 수 있다.

- 사용자의 선택이 이미 확정됐는지
- 요청 이후 사용자가 핀을 이동했는지
- 현재 결과가 여전히 적용 가능한지

```ts
if (!isStillValid()) {
  return null;
}

setMapCenter(point);
return point;
```

검사는 관련 데이터를 갱신하기 전뿐 아니라 외부 지도 중심을 변경하기 전에도 수행한다. 그렇지 않으면 데이터 변경은 막더라도 지도 화면만 이동하는 불일치가 남을 수 있다.

`useRef`는 렌더 사이에서 값을 유지하지만 값 변경만으로 리렌더링을 일으키지 않는다. 화면 출력용 state를 대체하는 것이 아니라, 오래 실행되는 이벤트 핸들러나 비동기 작업이 최신 유효성을 확인하는 용도로 제한한다.

## `useCallback`만으로 부족한 이유

`useCallback`은 callback 참조 변경과 불필요한 리스너 재구독을 줄일 수 있지만 다음 문제까지 해결하지는 않는다.

- dependency가 변경되면 callback 참조도 다시 변경된다.
- 이미 시작된 비동기 함수는 과거 렌더의 state를 볼 수 있다.
- 외부 래퍼의 Effect 실행 순서에는 여전히 의존한다.
- 늦게 도착한 요청이 현재도 유효한지 판단할 수 없다.

따라서 `useCallback`은 보조적인 최적화 수단일 수 있지만, 이 문제의 핵심 해결책은 이벤트 왕복 의존성 제거와 완료 시점의 유효성 검사다.

## 검증 방법

- 가짜 지도 객체가 `setCenter()` 안에서 중심 변경 이벤트를 동기적으로 발생시키도록 만든다.
- 지도 중심은 이동했지만 callback은 호출되지 않는 외부 래퍼의 현재 동작을 characterization test로 고정한다.
- 현재 위치 이동 시 새 좌표로 관련 데이터가 갱신되는지 검증한다.
- 위치 요청을 지연시킨 뒤 사용자가 핀을 이동하거나 선택을 확정했을 때 늦은 응답이 버려지는지 검증한다.
- 같은 좌표의 이벤트가 뒤늦게 도착하더라도 debounce 또는 멱등 처리로 중복 요청이 발생하지 않는지 확인한다.

## 핵심 원칙

> React state와 외부 라이브러리의 내부 state는 별개의 시스템이므로 동기화 경로와 책임을 명시적으로 설계한다.

> 프로그램이 이미 알고 있는 변경값을 외부 이벤트로 다시 전달받는 구조에 의존하지 않는다.

> 비동기 결과는 시작 순서나 도착 순서가 아니라 완료 시점의 유효성을 기준으로 적용한다.

## 참고 자료

- [React: Render and Commit](https://react.dev/learn/render-and-commit)
- [React: useEffect](https://react.dev/reference/react/useEffect)
- [React: State as a Snapshot](https://react.dev/learn/state-as-a-snapshot)
- [React: useRef](https://react.dev/reference/react/useRef)
- [React: Synchronizing with Effects](https://react.dev/learn/synchronizing-with-effects)
