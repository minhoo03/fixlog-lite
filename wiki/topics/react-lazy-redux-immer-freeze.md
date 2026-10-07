---
id: topic-react-lazy-redux-immer-freeze
title: React.lazy 객체를 Redux에 저장할 때 발생하는 Immer freeze 오류
summary: React.lazy 객체가 Redux 상태에 포함되면 개발 모드의 Immer auto-freeze가 React 내부 객체까지 동결할 수 있다. 컴포넌트 객체는 Redux에서 제외하고 정적 라우팅 설정에만 보관해야 한다.
aliases:
  - React lazy read only property end 오류
  - lazyInitializer _ioInfo 오류
  - Redux Immer React 컴포넌트 freeze
tags:
  - react
  - react-lazy
  - redux
  - redux-toolkit
  - immer
  - routing
  - debugging
type: topic
status: active
created: 2026-10-07
updated: 2026-10-07
index: true
related: []
---

# React.lazy 객체를 Redux에 저장할 때 발생하는 Immer freeze 오류

## 핵심 요약

- `React.lazy()`의 반환값은 단순 데이터가 아니라 React가 로딩 상태를 갱신하는 내부 객체다.
- 이 객체를 Redux 상태에 넣으면 Redux Toolkit의 Immer auto-freeze가 객체를 재귀적으로 동결할 수 있다.
- React가 최초 로딩 시 내부 `_ioInfo.start/end`를 수정하려 하면 읽기 전용 오류가 발생하므로, `component`는 Redux에서 제외하고 정적 라우팅 설정에만 둬야 한다.

## 증상과 영향 범위

- 페이지 진입 시 React의 `lazyInitializer` 내부에서 `TypeError: Cannot assign to read only property 'end'`가 발생한다.
- 별도 `route.ts`가 먼저 매칭되는 페이지는 정상 동작했다.
- 별도 라우트 없이 `_nav.ts`의 `component: React.lazy(...)`를 사용하는 페이지에서 문제가 드러났다.

## 원인 흐름

1. 메뉴 설정인 `nav.items`에는 `React.lazy()`로 만든 `component` 객체가 들어 있다.
2. 메뉴 순서와 열림 상태를 Redux에 저장하면서 얕은 복사만 수행해 `component` 참조가 그대로 유지됐다.
3. Immer가 Redux 상태 트리를 재귀적으로 동결하면서 원본 `_nav.ts`가 참조하는 lazy 객체까지 동결됐다.
4. React가 lazy 컴포넌트를 처음 불러오며 로딩 추적 정보인 `_ioInfo.start/end`를 기록하려 했지만, 객체가 이미 동결되어 초기화가 중단됐다.
5. `_ioInfo`는 표시할 컴포넌트를 결정하는 값이 아니라 React 내부의 디버깅·로딩 시간 추적 정보다. 이 기록 단계에서 예외가 발생해 결과적으로 렌더링도 실패했다.

## 해결 원칙

- Redux에는 메뉴 이름, 순서, 열림 여부처럼 직렬화 가능한 데이터만 저장한다.
- React 컴포넌트와 `React.lazy()` 객체는 Redux에 넣지 않고 정적 `nav.items`를 라우팅의 기준으로 유지한다.
- Redux용 메뉴 객체를 만들 때 최상위와 자식 항목 모두에서 `component`를 구조 분해로 제거한다.
- 저장된 메뉴 스냅샷이 없는 fallback 경로도 원본 `nav.items`를 바로 Redux에 넣지 말고 동일한 정제 함수를 거치게 한다.

```ts
const { component, ...serializableMenuData } = navItem;
return serializableMenuData;
```

## 주의점

- 얕은 복사는 중첩 객체의 참조를 끊지 않으므로 이 문제를 해결하지 못한다.
- `section -> children` 두 단계만 정제하면 더 깊은 `children`에 있는 `component`는 남는다. 메뉴가 다단계라면 재귀적으로 제거해야 한다.
- 일반 원칙은 Redux 상태를 데이터 전용으로 유지하고, React 컴포넌트·프레임워크 내부 객체·함수는 별도의 정적 레지스트리에 두는 것이다.

## 관련 문서

- 없음
