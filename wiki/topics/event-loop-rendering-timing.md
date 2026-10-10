---
id: topic-event-loop-rendering-timing
title: 이벤트 루프와 브라우저 렌더링 타이밍
summary: Task·microtask·Promise·requestAnimationFrame의 실행 시점과 화면 갱신의 관계를 설명하고, 로딩 표시가 보이지 않는 원인과 흔한 오해를 코드 및 꼬리질문으로 정리한다.
aliases:
  - 이벤트 루프
  - Promise와 렌더링
  - 마이크로태스크
  - 로딩 화면이 안 보이는 이유
tags:
  - 자바스크립트
  - 이벤트 루프
  - 비동기
  - Promise
  - 렌더링
type: topic
status: active
created: 2026-10-10
updated: 2026-10-10
index: true
related:
  - topic-rendering-pipeline-performance
  - topic-frontend-web-mobile-core-concepts
---

# 이벤트 루프와 브라우저 렌더링 타이밍

**핵심: JavaScript 실행이 끝났다는 것과 화면에 변경이 보인다는 것은 다른 시점이다.**

## 먼저 알아둘 개념

| 개념 | 필요한 만큼만 이해하기 |
|---|---|
| 메인 스레드 | 일반적인 페이지의 JavaScript, 이벤트 처리, 스타일·레이아웃 등 주요 작업이 실행되는 곳. 긴 작업은 입력 처리와 화면 갱신을 지연시킨다. |
| 콜 스택 | 현재 실행 중인 함수들의 호출 기록. 일반적인 동기 코드 실행 중 다른 콜백이 끼어들어 코드를 중단시키지는 않는다. |
| 비동기 | 작업 완료 후 이어서 실행할 코드를 예약하는 방식. 코드를 자동으로 별도 스레드에서 실행한다는 뜻은 아니다. |
| 렌더링 기회 | 브라우저가 화면 갱신을 진행할 수 있는 시점. 이벤트 루프가 한 번 돌 때마다 반드시 화면을 그리지는 않는다. |

## 실행 순서를 이해하는 흐름

1. **Task 실행**: 클릭 이벤트, 타이머 콜백 등 하나의 작업을 처리한다.
2. **Microtask 처리**: 처리 시점에 큐를 비울 때까지 실행한다. 실행 중 추가된 microtask도 포함한다.
3. **렌더링 기회가 있으면 화면 갱신 진행**: `requestAnimationFrame` 콜백은 이 갱신 과정에서 다음 repaint 전에 실행된다.

이것은 대표적인 흐름을 단순화한 모델이다. 실제로는 microtask checkpoint가 다른 지점에도 있고, task queue도 하나만 있는 것이 아니다. **전체 콜백을 하나의 FIFO 큐로 생각하면 안 된다.** [MDN: Microtask](https://developer.mozilla.org/en-US/docs/Web/API/HTML_DOM_API/Microtask_guide)

| 예약 방식 | 실행 의미 | 주의점 |
|---|---|---|
| `setTimeout(fn, 0)` | 지연 조건이 충족되면 타이머 task로 실행 가능해진다. | 즉시 실행이나 정확한 실행 시간을 보장하지 않는다. |
| `promise.then(fn)` | Promise가 이행되면 반응 콜백을 microtask로 실행한다. | 이미 이행된 Promise여도 콜백은 동기 실행되지 않는다. |
| `queueMicrotask(fn)` | microtask를 직접 예약한다. | 반복 예약하면 입력·렌더링이 밀릴 수 있다. |
| `requestAnimationFrame(fn)` | 다음 repaint 전에 시각적 변경을 수행하도록 예약한다. | 페인트 완료 콜백이 아니며, 매번 다시 예약해야 한다. |

`requestAnimationFrame`의 빈도는 화면 갱신 주기 등에 영향을 받는다. 60Hz 고정 타이머가 아니고, 백그라운드 탭에서는 대개 멈춘다. [MDN: requestAnimationFrame](https://developer.mozilla.org/en-US/docs/Web/API/Window/requestAnimationFrame)

## Promise에서 동기인 부분과 비동기인 부분

```js
console.log('A');

new Promise((resolve) => {
  console.log('B');
  resolve();
}).then(() => console.log('D'));

console.log('C');
// A → B → C → D
```

`new Promise`에 전달한 **executor는 즉시 동기 실행**된다. 비동기로 예약되는 것은 `.then` 등의 반응 콜백이다. 따라서 executor 안의 무거운 연산도 메인 스레드를 막는다. [MDN: Promise 생성자](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/Promise)

## 실무 사례: 로딩 표시가 보이지 않는 이유

```js
async function handleClick() {
  loadingElement.hidden = false;
  await Promise.resolve();
  heavyCalculation();
  loadingElement.hidden = true;
}
```

DOM은 바뀌었지만, `await` 이후 코드는 microtask로 이어진다. 화면 갱신 전에 무거운 연산과 숨김 처리가 끝나면 사용자는 중간의 로딩 표시를 볼 수 없다.

**해결 방향은 연산량에 따라 고른다.** 짧게 쪼갤 수 있는 작업은 여러 task로 나눠 브라우저에 제어권을 돌려준다. CPU 연산이 크다면 Web Worker로 옮기는 방식을 검토한다. Worker는 DOM에 직접 접근할 수 없으므로 결과만 전달한다.

`setTimeout`으로 다음 task에 넘기면 렌더링할 기회가 생길 수 있지만, 그 사이 페인트를 보장하지 않는다. `await new Promise(requestAnimationFrame)`도 페인트 완료를 기다리는 코드가 아니다. 이어지는 무거운 연산이 다음 페인트를 막을 수 있다.

## 헷갈리기 쉬운 설명 바로잡기

| 흔한 설명 | 정확한 이해 |
|---|---|
| “Promise는 비동기니까 연산이 화면을 안 막는다.” | Promise는 실행 스레드를 바꾸지 않는다. |
| “`await`하면 브라우저가 한 프레임 그린다.” | 현재 async 함수 실행을 중단할 뿐, 화면 갱신을 보장하지 않는다. |
| “Microtask가 task보다 항상 먼저다.” | 현재 동기 실행을 선점하지 않는다. checkpoint에서 대기 중인 microtask를 처리한다. |
| “rAF 안에 넣으면 무거운 작업도 안전하다.” | rAF 콜백도 실행 비용이 있다. 길면 해당 프레임을 지연시킨다. |

## 스스로 검토할 꼬리질문

**Q. `resolve()`를 호출하면 `.then`이 그 자리에서 실행되는가?**

A. 아니다. 현재 동기 코드가 계속 실행되고, 반응 콜백은 microtask로 처리된다.

**Q. microtask에서 microtask를 계속 추가하면?**

A. 큐를 비우지 못해 다음 task와 렌더링 진행이 지연될 수 있다.

**Q. 프레임워크의 DOM 반영을 기다렸으면 화면 표시도 완료됐는가?**

A. 아니다. 프레임워크의 업데이트 완료와 브라우저의 페인트·화면 표시는 구분해야 한다.

**Q. 5년 차라면 무엇까지 설명할 수 있어야 하는가?**

A. 실행 순서뿐 아니라, 어떤 코드가 메인 스레드를 오래 점유하고 왜 입력이나 화면 갱신을 지연시키는지 설명해야 한다.

## 관련 문서

- [렌더링 파이프라인과 성능 병목 진단](rendering-pipeline-performance.md)
- [웹·모바일 프론트엔드 업무를 위한 핵심 개념](frontend-web-mobile-core-concepts.md)
