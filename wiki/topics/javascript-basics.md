---
id: topic-javascript-basics
title: JavaScript 기본 개념 요약
summary: 변수·스코프, 클로저, this, 프로토타입, Promise, async/await, 이벤트 루프 등 JavaScript 기본 개념 20개를 핵심 설명과 짧은 예제로 정리한다.
aliases:
  - 자바스크립트 기초
  - JS 기본 지식
  - JavaScript 핵심 개념
  - 클로저와 프로미스 기초
tags:
  - 자바스크립트
  - 기초
  - 스코프
  - 클로저
  - 비동기
  - 이벤트 루프
type: topic
status: active
created: 2026-10-17
updated: 2026-10-17
index: true
related:
  - topic-event-loop-rendering-timing
  - topic-frontend-web-mobile-core-concepts
---

# JavaScript 기본 개념 요약

## 1. 변수와 스코프

- `const`: 재할당할 수 없는 변수. 객체의 속성이나 배열의 내용은 변경할 수 있다.
- `let`: 재할당할 수 있는 변수.
- `var`: 함수 스코프를 가지며 같은 스코프에서 재선언할 수 있다.
- `let`, `const`는 블록(`{}`) 스코프를 가진다. 기본적으로 `const`를 쓰고, 재할당이 필요하면 `let`을 쓴다.

## 2. 자료형과 타입 변환

- 원시 타입: `string`, `number`, `bigint`, `boolean`, `undefined`, `symbol`, `null`.
- 객체 타입: 객체, 배열, 함수 등.
- `Number("10")`처럼 명시적으로 변환할 수 있고, 연산 과정에서 암묵적으로 변환되기도 한다.
- `===`는 타입 변환 없이 비교하므로 일반적으로 `==`보다 예측하기 쉽다.

```js
"1" + 2;     // "12"
Number("1") + 2; // 3
0 === false; // false
```

## 3. 호이스팅과 TDZ

- 호이스팅은 선언이 코드 실행 전에 처리되는 동작을 설명하는 표현이다. 코드가 실제로 위로 이동하는 것은 아니다.
- `var`는 선언 전에 접근하면 `undefined`이고, 함수 선언문은 선언 전에도 호출할 수 있다.
- `let`, `const`는 스코프 진입부터 선언이 실행되기 전까지 TDZ(Temporal Dead Zone)에 있어 접근하면 `ReferenceError`가 발생한다.

## 4. 함수와 화살표 함수

- 함수는 값을 받아 작업을 수행하고 결과를 반환한다. 변수에 저장하거나 다른 함수에 전달할 수 있다.
- 화살표 함수는 문법이 간결하며 자신만의 `this`를 만들지 않는다.
- 일반 함수는 호출 방식에 따라 `this`가 결정되며, 생성자로 사용할 수 있는 함수도 있다. 화살표 함수는 생성자로 사용할 수 없다.

```js
function add(a, b) { return a + b; }
const double = n => n * 2;
```

## 5. 클로저

함수가 자신이 선언된 외부 스코프의 변수에 계속 접근할 수 있는 성질이다. 외부 함수의 실행이 끝난 뒤에도 상태를 유지하는 데 활용한다.

```js
function createCounter() {
  let count = 0;
  return () => ++count;
}
const next = createCounter();
next(); // 1
next(); // 2
```

## 6. this와 바인딩

- 일반 함수의 `this`는 함수를 어떻게 호출했는지에 따라 달라진다. `obj.method()`에서는 보통 `obj`다.
- 메서드를 별도 변수에 꺼내 호출하면 원래 객체와의 연결이 유지되지 않는다.
- `call`, `apply`는 `this`를 지정해 호출하고, `bind`는 `this`가 고정된 새 함수를 만든다.
- 화살표 함수의 `this`는 선언된 위치의 외부 `this`를 따른다.

## 7. 객체와 프로토타입

- 객체는 키와 값으로 이루어진 속성들의 집합이다.
- 속성을 찾을 때 객체 자체에 없으면 프로토타입을 따라 탐색한다. 이를 프로토타입 체인이라고 한다.
- 여러 객체가 프로토타입의 메서드를 공유할 수 있다.

## 8. 클래스와 상속

`class`는 프로토타입 기반 객체 생성을 표현하는 문법이다. `constructor`로 초기화하고, `extends`로 상속하며, `super`로 부모 생성자나 메서드에 접근한다.

```js
class Animal {
  constructor(name) { this.name = name; }
  speak() { return this.name; }
}
class Dog extends Animal {
  speak() { return `${super.speak()}: 멍멍`; }
}
```

## 9. 참조와 얕은 복사·깊은 복사

- 객체를 다른 변수에 할당하면 같은 객체를 가리킨다.
- `{ ...obj }`, `[...arr]`는 얕은 복사다. 중첩된 객체는 여전히 공유한다.
- `structuredClone()`은 지원하는 타입의 값을 깊게 복사한다. 함수 등 일부 값은 복사할 수 없다.
- `JSON.parse(JSON.stringify(obj))`는 타입과 값이 손실될 수 있어 범용 깊은 복사로 쓰기 어렵다.

## 10. 구조 분해와 스프레드 문법

- 구조 분해는 배열의 요소나 객체의 속성을 변수로 꺼내는 문법이다.
- 스프레드(`...`)는 배열·객체 등을 펼친다. 나머지 요소를 모을 때는 같은 기호를 rest 문법으로 사용한다.

```js
const { name } = { name: "민수", age: 20 };
const [first, ...rest] = [1, 2, 3];
const copy = [...rest, 4]; // [2, 3, 4]
```

## 11. 배열 메서드

- `map`: 각 요소를 변환한 새 배열.
- `filter`: 조건에 맞는 요소들로 만든 새 배열.
- `reduce`: 요소들을 누적해 하나의 결과로 계산.
- `find`: 조건을 만족하는 첫 요소. 없으면 `undefined`.
- `some` / `every`: 일부 / 모든 요소가 조건을 만족하는지 검사.
- `forEach`: 각 요소에 작업을 수행하며, 반환값은 `undefined`.
- `sort`, `reverse`, `splice` 등은 원본 배열을 변경하므로 주의한다.

## 12. 실행 컨텍스트와 콜 스택

- 실행 컨텍스트는 코드를 실행할 때 필요한 변수, 스코프, `this` 등의 정보를 담는 실행 환경이다.
- 콜 스택은 현재 실행 중인 함수 호출들을 관리한다. 함수를 호출하면 쌓이고, 종료하면 제거된다.
- 동기 코드가 오래 실행되면 같은 스레드의 다른 작업도 기다린다.

## 13. 콜백과 비동기 처리

- 콜백은 다른 함수에 인자로 전달해 호출하도록 하는 함수다. 콜백이 항상 비동기인 것은 아니다.
- 비동기 처리는 타이머나 네트워크 요청 등의 완료를 기다리는 동안 다른 코드를 진행하게 한다.
- 비동기 작업이 완료되었다고 실행 중인 동기 코드를 즉시 중단하는 것은 아니다.

```js
[1, 2].map(n => n * 2); // 동기 콜백
setTimeout(() => console.log("나중에 실행"), 0); // 비동기 콜백
```

## 14. Promise

- 비동기 작업의 결과를 표현하는 객체다. `pending`에서 `fulfilled` 또는 `rejected` 상태가 된다.
- `then`은 성공, `catch`는 실패, `finally`는 성공·실패에 관계없이 실행할 후속 처리를 연결한다.
- `then`은 새 Promise를 반환하므로 체이닝할 수 있다.
- `Promise.all`은 모두 성공하면 결과를 모으고 하나라도 실패하면 거부된다. `Promise.allSettled`는 모두 끝난 뒤 각각의 성공·실패 결과를 모은다.
- Promise 생성자에 전달한 함수는 즉시 실행되지만, 등록한 `then` 등의 핸들러는 비동기로 실행된다.

## 15. async / await

- `async` 함수는 항상 Promise를 반환한다.
- `await`는 값이 처리될 때까지 현재 `async` 함수의 진행을 잠시 멈춘다. 스레드 전체를 멈추지는 않는다.
- 서로 독립적인 작업은 먼저 시작한 뒤 `Promise.all`로 함께 기다릴 수 있다.

```js
async function loadBoth() {
  const [a, b] = await Promise.all([loadA(), loadB()]);
  return { a, b };
}
// loadA, loadB는 Promise를 반환하는 함수라고 가정한다.
```

## 16. 이벤트 루프와 태스크·마이크로태스크

- 이벤트 루프는 실행할 작업을 스케줄링한다. 브라우저에서는 타이머 콜백 등이 태스크로, Promise 후속 처리와 `queueMicrotask` 등이 마이크로태스크로 실행된다.
- 현재 태스크의 동기 코드가 끝나면 마이크로태스크를 모두 처리하고, 이후 다음 태스크로 넘어간다. 마이크로태스크가 추가한 마이크로태스크도 함께 처리한다.
- `setTimeout(fn, 0)`은 즉시 실행을 보장하지 않는다. 렌더링은 브라우저의 렌더링 기회에 이루어진다.
- Node.js는 별도의 이벤트 루프 단계가 있으므로 브라우저의 설명을 모든 상황에 그대로 적용하면 안 된다.

```js
console.log("A");
setTimeout(() => console.log("B"), 0);
Promise.resolve().then(() => console.log("C"));
console.log("D");
// 출력 순서: A → D → C → B
```

## 17. 에러 처리

- `throw`로 에러를 발생시키고, `try` / `catch`로 처리한다.
- `finally`는 성공·실패에 관계없이 정리 작업을 수행한다.
- `await`한 Promise의 거부는 `try` / `catch`로 잡을 수 있다.
- 나중에 실행되는 타이머 콜백의 에러는 타이머를 등록한 바깥쪽 `try` / `catch`로 잡을 수 없다.

```js
async function load() {
  try {
    return await fetchData();
  } catch (error) {
    console.error(error);
    throw error; // 호출자에게 실패를 전달
  }
}
```

## 18. 모듈

- `export`로 기능을 내보내고 `import`로 가져온다.
- 모듈은 자체 스코프를 가지며 strict mode로 실행된다.
- 이름 있는 내보내기와 기본 내보내기(`default`)가 있다. `import()`로 동적 로딩도 가능하다.

```js
// math.js
export const add = (a, b) => a + b;

// main.js
import { add } from "./math.js";
```

## 19. 가비지 컬렉션과 메모리 관리

- 엔진은 더 이상 도달할 수 없는 객체의 메모리를 자동으로 회수한다. 회수 시점은 보장되지 않는다.
- 불필요한 이벤트 리스너, 타이머, 전역 변수, 계속 커지는 캐시가 객체를 붙잡으면 메모리 누수가 생길 수 있다.
- 사용이 끝난 구독·타이머는 해제하고, 필요 없는 참조는 제거한다.

## 20. DOM과 이벤트 전파

- DOM은 브라우저가 HTML 문서를 객체 트리로 표현한 것이다. JavaScript로 요소를 조회하거나 변경할 수 있다.
- 이벤트는 보통 캡처링 → 타깃 → 버블링 순으로 전달되며, 모든 이벤트가 버블링하는 것은 아니다.
- `event.target`은 이벤트가 발생한 대상이고, `event.currentTarget`은 현재 리스너가 연결된 대상이다.
- `preventDefault()`는 취소 가능한 기본 동작을 막고, `stopPropagation()`은 이벤트 전파를 막는다.
- 이벤트 위임은 부모 요소의 리스너에서 자식들의 이벤트를 처리하는 방식이다.

---

**권장 학습 순서:** 변수·자료형 → 함수·스코프 → 클로저·this → 객체·프로토타입 → 배열·복사 → 콜 스택 → 비동기·Promise·async/await → 이벤트 루프 → 모듈·에러·메모리 → DOM·이벤트.

## 관련 문서

- [이벤트 루프와 브라우저 렌더링 타이밍](event-loop-rendering-timing.md): 태스크·마이크로태스크와 화면 갱신의 관계를 더 자세히 설명한다.
- [웹·모바일 프론트엔드 업무를 위한 핵심 개념](frontend-web-mobile-core-concepts.md): 프론트엔드 실무 개념으로 학습 범위를 확장한다.
