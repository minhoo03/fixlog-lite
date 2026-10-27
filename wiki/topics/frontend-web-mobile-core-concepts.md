---
id: topic-frontend-web-mobile-core-concepts
title: 웹·모바일 프론트엔드 업무를 위한 핵심 개념
summary: 브라우저와 JavaScript 실행 모델에서 출발해 TypeScript, React, 상태·API·데이터·Next.js 경계, 분석·그로스·통계·실험, 품질·모바일·운영·검증·개발 문화·제출까지 하나의 기능이 만들어지고 측정·운영되는 흐름으로 연결한다.
aliases:
  - 프론트엔드 핵심 개념
  - 웹 모바일 프론트엔드 학습 로드맵
  - 프론트엔드 실무 개념 지도
  - 프론트엔드 면접 핵심 개념
  - 웹 모바일 공용 코드
  - 프론트엔드 기술 도입 이유
  - 모노레포와 마이크로 프론트엔드
tags:
  - 프론트엔드
  - javascript
  - typescript
  - react
  - 상태 관리
  - 서버 상태
  - 렌더링
  - nextjs
  - api
  - 제품 분석
  - 사용자 분석
  - 실험
  - 통계
  - 그로스
  - 웹뷰
  - 디자인 시스템
  - 모노레포
  - 품질
  - 테스트
  - 개발 문화
type: topic
status: active
created: 2026-10-09
updated: 2026-10-27
index: true
related:
  - topic-javascript-basics
  - topic-event-loop-rendering-timing
  - topic-rendering-pipeline-performance
  - topic-webview-native-bridge-communication
  - topic-playwright-react-component-screenshot-pr-review
---

# 웹·모바일 프론트엔드 업무를 위한 핵심 개념

> 목표: 개별 기술의 사용법을 외우는 데서 그치지 않고, 하나의 기능이 실행되고 데이터를 주고받으며 측정·검증·운영되는 전체 흐름을 이해한다.

## 핵심 요약

- 프론트엔드 기능은 **실행 환경, 타입, UI, 상태, 서버, 측정, 운영**의 경계를 차례로 지난다. 한 경계에서 생긴 오해가 다른 층의 버그로 나타난다.
- Promise는 작업의 완료를 표현할 뿐 순서·취소·서버 일관성을 자동으로 보장하지 않는다. TypeScript 타입도 런타임의 외부 데이터를 자동 검증하지 않는다.
- React는 화면을 입력의 순수한 결과로 계산하고, Effect는 외부 시스템과 동기화하는 탈출구로 사용한다. 상태는 소유자와 수명에 따라 서버·URL·폼·지역·영속 상태로 나눈다.
- TanStack Query와 Next.js 캐시는 원본 데이터가 아니다. 각 캐시의 키, 신선도, 무효화 조건과 사용자에게 허용할 오래된 정도를 정해야 한다.
- 이벤트를 신뢰할 수 있어야 실험과 그로스 지표도 신뢰할 수 있다. 실험에서는 효과 크기보다 먼저 배정, 노출, 중복, SRM과 가드레일을 확인한다.
- 접근성·성능·SEO·보안·개인정보·테스트·배포·문서화는 기능이 완성된 뒤 붙이는 장식이 아니라 완료 조건이다.

## 전체 지도: 하나의 기능은 어떤 경계를 지나는가

예를 들어 사용자가 상품 페이지에서 수량을 바꾸고 구매한다고 하자.

```text
브라우저에서 입력 발생
→ JavaScript가 작업을 예약하고 Promise로 결과를 기다림
→ TypeScript가 내부 계약을 표현하고 외부 입력은 런타임에 검증
→ React가 현재 상태로 화면을 계산
→ 상태의 소유자에 따라 URL·폼·지역 상태 또는 서버 상태를 구분
→ API 계약 위에서 서버 원본을 읽거나 변경하고 Query cache를 동기화
→ Next.js가 서버·클라이언트 실행과 route rendering을 조합
→ 분석 이벤트로 노출·클릭·구매를 관측
→ 퍼널·리텐션으로 현상을 보고 통계와 실험으로 변경 효과를 판단
→ 접근성·성능·보안·테스트·배포 기준을 통과
→ 운영 도구와 로그로 이후의 변경까지 추적
```

이 흐름을 관통하는 질문은 다음과 같다.

| 경계 | 먼저 물을 질문 |
|---|---|
| 실행 | 이 코드는 브라우저, 서버, 네이티브 앱 중 어디서 언제 실행되는가? |
| 소유권 | 이 데이터의 원본은 누구이며, 누가 변경할 수 있는가? |
| 신뢰 | 타입만 믿어도 되는 내부 값인가, 검증해야 하는 외부 입력인가? |
| 시간 | 늦은 응답, 재시도, 중복 요청, 동시 수정이 생기면 어떤 결과가 맞는가? |
| 캐시 | 어떤 키로 구분하며, 얼마 동안 오래된 값을 보여줘도 되는가? |
| 측정 | 무엇을 언제 한 번 기록해야 제품의 실제 행동을 대표하는가? |
| 배포 | 웹·서버·앱 버전이 서로 달라도 계약이 유지되는가? |

---

> **Part 1 — 실행과 UI:** 브라우저의 시간 모델에서 출발해 안전한 값과 화면, 상태 소유권으로 올라간다.

## 1. 기반: JavaScript와 브라우저는 일을 어떻게 실행하는가

### 실행 모델부터 이해한다

일반적인 웹 페이지에서 JavaScript는 메인 스레드의 콜 스택에서 한 번에 하나의 코드를 실행한다. 네트워크, 타이머, 사용자 입력은 브라우저 기능이 처리하고, 완료된 콜백은 큐를 거쳐 다시 JavaScript가 실행한다. `new Promise(executor)`의 executor는 즉시 동기 실행되고, `then`·`catch`·`finally` 같은 후속 처리는 microtask로 예약된다. 현재 실행과 microtask가 오래 걸리면 입력 처리와 화면 갱신도 늦어진다.

`fetch`, timer, DOM, storage, `AbortController`는 JavaScript 문법 자체가 아니라 브라우저 같은 실행 환경이 제공하는 API다. Node.js, Server Component, 일반 브라우저와 WebView는 사용할 수 있는 API와 생명주기가 다르므로 “JavaScript 코드니까 어디서나 같다”고 가정하지 않는다.

따라서 **비동기는 자동 병렬 실행이 아니다.** Promise는 미래의 성공 또는 실패를 나타내는 객체이지 별도 스레드를 만드는 장치가 아니다. `Promise.all`이나 `Promise.race`가 완료돼도 나머지 작업이 자동으로 취소되지는 않는다. 자세한 순서는 [이벤트 루프와 브라우저 렌더링 타이밍](event-loop-rendering-timing.md)에서 다룬다.

### Race condition은 “먼저 요청한 것이 먼저 끝난다”는 가정이 깨질 때 생긴다

검색어 `a` 요청 뒤에 `ab` 요청을 보냈는데 `a`의 응답이 더 늦게 도착하면, 단순한 코드는 최신 화면을 과거 결과로 덮어쓴다. 이것이 시간 순서에 따라 결과가 달라지는 race condition이다.

해결 방법은 제품 의미에 따라 고른다.

- **최신 결과만 유효:** 요청 번호나 현재 검색어를 확인해 오래된 응답을 무시한다.
- **불필요한 작업 중단:** `fetch`에 `controller.signal`을 전달하고, 새 요청을 시작할 때 이전 controller의 `abort()`를 호출한다.
- **한 번에 하나씩 처리:** 저장 순서가 중요하면 직렬화하거나 큐를 둔다.
- **같은 작업 합치기:** 동일한 키의 조회를 공유하거나 중복 요청을 제거한다.
- **서버 변경 보호:** 멱등성 키와 버전 검사를 사용한다. 클라이언트의 취소만으로 이미 처리된 서버 작업이 되돌아가지는 않는다.

```ts
let latestRequest = 0;

async function search(keyword: string) {
  const request = ++latestRequest;
  const result = await fetchProducts(keyword);

  if (request !== latestRequest) return; // 오래된 완료 결과는 폐기
  render(result);
}
```

**핵심:** 취소는 이를 지원하고 signal을 전달받은 작업에만 효력이 있는 협력적인 제어다. 취소는 불필요한 작업을 줄이고, 요청 식별자 검사는 오래된 결과가 최신 화면을 덮는 것을 막는다. 클라이언트가 응답을 더 이상 쓰지 않는 것, 전송을 중단하는 것, 서버의 업무 처리를 취소하는 것은 서로 다른 문제다.

## 2. 타입: TypeScript 계약과 런타임 현실을 연결한다

TypeScript는 JavaScript 코드가 실행되기 전에 가능한 실수를 찾는 정적 타입 시스템이다. 빌드 후 타입 정보 대부분은 사라지므로 API 응답, URL, 저장소, 분석 payload, WebView 메시지가 선언한 타입과 실제로 일치하는지는 별도로 확인해야 한다.

### Union, narrowing, generic의 역할

- **Union**은 값이 가질 수 있는 여러 경우를 표현한다.
- **Narrowing**은 `typeof`, `in`, 판별 필드, 사용자 정의 가드 등 실제 조건을 검사해 가능한 경우를 좁힌다.
- **Generic**은 구체적인 타입을 나중에 받으면서도 입력과 출력의 관계를 보존한다.

```ts
type LoadState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; message: string };

function renderProduct(state: LoadState<Product>) {
  switch (state.status) {
    case 'success':
      return state.data.name; // 판별 필드로 Product까지 narrowing
    case 'error':
      return state.message;
    default:
      return '불러오는 중';
  }
}
```

판별 union은 불가능한 상태 조합을 줄인다. 예를 들어 `isLoading`, `data`, `error`를 서로 독립된 boolean과 optional 값으로 두면 “로딩 중인데 성공 데이터와 오류가 모두 있음” 같은 상태도 타입상 가능해진다.

### 외부 경계에서는 `unknown`에서 시작해 검증한다

`as Product`는 검증이 아니라 컴파일러에 대한 주장이다. 신뢰할 수 없는 값은 `unknown`으로 받고 스키마 또는 명시적인 가드로 구조, 범위, 형식을 검사한 다음 도메인 타입으로 바꾼다.

검증이 필요한 대표 경계는 다음과 같다.

- 서버 요청·응답
- URL parameter와 query string
- `localStorage`·IndexedDB에서 복원한 값
- WebView 브리지 메시지
- 폼 입력과 파일
- 분석 이벤트 payload

**핵심:** TypeScript는 내부 코드의 계약을 강화하고, 런타임 검증은 신뢰 경계에서 실제 값을 증명한다. 둘 중 하나가 다른 하나를 대신하지 않는다. 이렇게 검증한 값을 이제 React 화면의 입력으로 사용한다.

## 3. React: 화면 계산과 외부 동기화를 분리한다

### 렌더링은 순수한 계산이다

React 컴포넌트는 현재의 props, state, context를 받아 JSX를 계산한다. 같은 입력이면 같은 결과를 내야 하며, 렌더링 중 네트워크 요청, 전역 값 변경, 분석 이벤트 전송 같은 부수 효과를 만들면 안 된다. React는 렌더 결과를 계산한 뒤 실제 DOM에 반영하는 commit 단계를 거친다.

다른 값으로부터 계산할 수 있는 값은 별도 state와 Effect로 복제하지 않고 렌더 중 계산하는 것이 기본이다. 중복된 state는 어느 값이 원본인지 모호하게 만든다.

### Event와 Effect는 목적이 다르다

- **Event handler:** 사용자가 버튼을 눌렀다는 특정 상호작용 때문에 실행한다.
- **Effect:** 연결, 구독, 타이머, 브라우저 API처럼 React 밖의 시스템과 현재 UI 상태를 동기화한다.

외부 시스템이 없다면 Effect가 필요하지 않은 경우가 많다. Effect는 setup을 수행하고 cleanup을 반환한다. dependency가 달라진 렌더가 commit되면 React는 새 setup 전에 이전 값으로 cleanup을 실행하고, 컴포넌트가 사라질 때도 cleanup을 실행한다.

```ts
useEffect(() => {
  const controller = new AbortController();

  loadProduct(productId, controller.signal).then(setProduct, handleError);

  return () => controller.abort();
}, [productId]);
```

실제 코드에서는 abort 오류를 일반 실패와 구분하고, 취소가 불가능하거나 이미 완료된 작업에는 요청 식별자 검사도 함께 사용한다.

### Strict Mode는 중복 실행을 만드는 기능이 아니라 결함을 드러내는 검사다

개발 환경의 Strict Mode는 순수하지 않은 렌더와 빠진 cleanup을 찾기 위해 일부 렌더를 한 번 더 호출한다. 앱 root에 적용한 일반적인 경우 Effect에도 추가 setup → cleanup → setup 주기를 수행한다. subtree에만 적용하면 초기 Effect 재실행에는 예외가 있을 수 있다. 이를 `useRef`로 억지로 한 번만 실행하게 만들기보다, cleanup과 작업의 멱등성을 고쳐야 한다. 프로덕션에서도 재마운트, 뒤로 가기, 네트워크 재시도는 일어날 수 있다.

### Hydration은 서버 HTML과 클라이언트 React를 연결한다

서버가 만든 첫 HTML과 클라이언트의 첫 렌더 결과는 일치해야 한다. 렌더 중 시간·난수·`window`·브라우저 저장소를 읽거나 서버와 클라이언트의 초기 데이터가 다르면 hydration 불일치가 생긴다. 브라우저 전용 값은 적절한 클라이언트 경계와 Effect에서 다루고, 불일치를 숨기는 옵션은 예외적으로만 사용한다.

React가 어떤 state로 화면을 계산하는지 이해했다면 다음 질문은 그 state의 원본을 어디에 둘 것인가다.

## 4. 상태 관리: 상태 이름보다 소유자와 수명을 먼저 구분한다

모든 값을 하나의 전역 store에 넣는 것이 상태 관리가 아니다. 먼저 원본의 소유자, 공유 범위, URL 재현 필요성, 새로고침 이후 생존 여부를 묻는다.

| 상태 종류 | 원본과 수명 | 예 | 보통의 위치 |
|---|---|---|---|
| 서버 상태 | 서버가 원본이며 다른 사용자·프로세스가 바꿀 수 있음 | 상품, 재고, 주문 | 서버 + 클라이언트 조회 캐시 |
| URL 상태 | 탐색 기록과 공유 가능한 화면 위치를 표현 | 검색어, 필터, 페이지, 선택 탭 | path·search params |
| 폼 상태 | 제출 전 사용자의 작업 초안 | 입력값, touched, validation error | 폼 컴포넌트·폼 라이브러리 |
| 지역 UI 상태 | 한 화면 트리의 일시적 상호작용 | 모달 열림, hover, 아코디언 | 가까운 컴포넌트 state |
| 영속 클라이언트 상태 | 새로고침 뒤에도 남길 기기별 값 | 테마, 임시 초안, 최근 항목 | storage·IndexedDB + 버전·마이그레이션 |

추가 원칙은 다음과 같다.

- 계산 가능한 파생 값은 별도 원본 상태로 저장하지 않는다.
- 여러 컴포넌트가 값을 공유하거나 함께 조정해야 할 때 상태를 공통 조상이나 외부 store로 올린다.
- URL에 있어야 할 값을 store에만 두면 새로고침, 뒤로 가기, 링크 공유가 깨진다.
- 영속 저장은 편리하지만 오래된 schema, 용량, 동기화, 개인정보와 로그아웃 정리 정책이 필요하다.
- 서버 데이터의 사본을 전역 store에 직접 복제하면 캐시 신선도와 무효화 책임도 함께 떠안는다.
- Context나 Redux 같은 전역 store는 상태의 종류가 아니라 값을 전달하고 구독하는 방식이다. 같은 의미를 URL, store, Query cache에 중복해 원본을 여러 개 만들지 않는다.

이 분류를 하고 나면 서버 상태는 먼저 API 계약으로 읽고, 그 계약 위의 클라이언트 사본을 TanStack Query로 관리할 수 있다.

---

> **Part 2 — 서버와 데이터:** 원격 원본의 계약을 세운 뒤 그 사본과 렌더링 위치를 관리한다.

## 5. API: 실패, 재시도, 중복과 동시 수정을 계약으로 만든다

### HTTP 상태 코드는 UI 분기와 운영 판단의 공용 언어다

| 범주 | 대표 의미와 처리 |
|---|---|
| `200`·`201`·`204` | 조회/처리 성공, 리소스 생성, 본문 없는 성공을 구분한다. |
| `400`·`422` | 요청 형식 또는 의미 검증 실패. 필드 오류를 사용자가 고칠 수 있게 구조화한다. |
| `401`·`403` | 인증 필요와 권한 부족을 구분한다. UI 숨김만으로 권한을 보호하지 않는다. |
| `404` | 해당 리소스가 없음. 권한 정보 노출을 줄이기 위해 정책상 404를 쓸 때는 일관되게 정한다. |
| `409`·`412` | 현재 상태와의 충돌 또는 버전 precondition 실패. 재조회·병합·사용자 확인이 필요할 수 있다. |
| `429` | 요청 제한. `Retry-After`와 클라이언트 backoff 정책을 고려한다. |
| `5xx` | 서버 측 실패. 관측과 제한된 재시도, 대체 UI가 필요하다. |

상태 코드만으로 충분하지 않다. 안정적인 오류 코드, 사용자용 메시지와 내부 진단 정보의 분리, request/correlation ID를 함께 설계한다.

### 멱등성과 재시도

멱등성은 같은 의도의 요청을 여러 번 적용해도 서버의 의도된 최종 효과가 한 번 적용한 것과 같다는 뜻이다. 응답 코드까지 항상 같다는 뜻은 아니다. HTTP 의미상 GET·PUT·DELETE 등은 멱등성을 기대하지만, 실제 서버 구현도 그 계약을 지켜야 한다.

결제·주문 생성처럼 POST를 안전하게 재시도해야 하면 클라이언트가 idempotency key를 보내고 서버가 같은 작업 범위와 payload에 대한 처리 결과를 재사용한다. 같은 키를 다른 payload에 사용하면 거부하고, 키의 범위·만료·동시 도착 정책을 정한다. 버튼 비활성화는 사용자 경험을 돕지만, 더블 클릭·탭 복원·프록시·SDK 재시도까지 막는 무결성 장치는 아니다. `Idempotency-Key` HTTP header는 2026년 10월 현재 IETF 초안이므로 지원 방식은 API 계약에 명시한다.

자동 재시도는 멱등 메서드이거나 idempotency key 등으로 애플리케이션 멱등성이 보장된 요청에만 적용한다. timeout과 연결 실패는 서버가 처리했는지 알 수 없는 결과일 수 있다. 재시도할 수 있는 일부 `5xx`·`429`에는 지수 backoff, jitter, 최대 횟수와 전체 시간 예산을 두고 `Retry-After`를 존중한다. 검증 오류나 권한 오류를 같은 입력으로 반복하지 않는다.

### 버전 충돌과 lost update

두 관리자가 같은 상품을 열고 차례로 저장하면 나중 저장이 앞선 변경을 조용히 덮을 수 있다. 응답의 ETag를 다음 수정의 `If-Match` precondition으로 보냈는데 현재 ETag와 다르면 서버는 원칙적으로 `412 Precondition Failed`로 거부한다. 요청 body의 자체 version처럼 도메인 수준의 현재 상태 충돌에는 `409 Conflict`를 사용할 수 있다. 클라이언트는 최신 값을 다시 받아 차이를 보여주고 재적용·병합·취소를 선택하게 한다.

**핵심:** 요청 취소, 멱등성, 중복 제거, 동시성 제어는 각각 다른 실패를 해결한다. 하나로 나머지를 대신할 수 없다. 이 서버 계약 위에서 이제 클라이언트 사본의 수명과 신선도를 관리한다.

## 6. 데이터: TanStack Query는 서버 상태의 캐시와 동기화를 맡는다

TanStack Query는 조회의 로딩·오류·재시도·중복 작업·재조회와 변경 상태를 공통화한다. 그러나 서버 데이터의 최종 원본이나 업무 규칙을 소유하지는 않는다.

### Query와 cache

- `queryKey`는 캐시의 정체성이다. 결과를 바꾸는 사용자, 필터, 페이지 같은 입력이 키에 포함돼야 한다.
- `staleTime`은 캐시를 신선하다고 보는 시간이고, `gcTime`은 사용되지 않는 캐시를 메모리에서 정리하기까지의 시간이다.
- stale 데이터는 즉시 화면에 보이면서 백그라운드에서 다시 조회될 수 있다. “캐시에 있음”과 “최신임”은 다르다.
- 계정 전환 시 사용자별 캐시가 섞이지 않도록 키와 정리 정책을 설계한다.

Query는 서버의 다른 변경을 스스로 알아내지 못한다. 최신성 요구에 따라 mount·focus·reconnect 시 재조회, polling, 사용자 refresh, WebSocket·SSE 알림 뒤 invalidation 같은 전략을 선택한다.

기본 `fetch`는 `404`나 `500` 응답에도 Promise를 이행하므로 query function에서 `response.ok` 또는 상태 코드를 확인하고, body를 런타임 검증한 뒤 오류를 던져야 한다. 반대로 재시도 정책이 모든 `4xx`까지 반복하지 않도록 상태·업무 오류별 조건을 정한다.

### Mutation, invalidation, optimistic update

Mutation은 생성·수정·삭제처럼 서버에 부수 효과를 요청한다. 성공 후에는 다음 중 하나를 선택한다.

1. 서버가 반환한 확정 데이터로 해당 캐시를 직접 갱신한다.
2. 관련 query를 invalidate해 오래된 것으로 표시한다. 기본적으로 현재 active query는 background에서 다시 조회되며, 삭제나 즉시 cache 비우기와는 다르다.
3. 목록·집계 등 영향을 받는 여러 키를 함께 갱신한다.

낙관적 업데이트는 서버 성공 전에 UI를 먼저 바꿔 빠르게 느끼게 한다. 대신 이전 값 snapshot, 실패 rollback 또는 refetch, 동시에 진행된 mutation의 순서, 서버가 보정한 최종 값을 다뤄야 한다. 오래된 mutation의 rollback이 더 새로운 성공 결과를 덮지 않도록 작업 식별자나 서버 버전을 고려한다.

**핵심:** Query는 네트워크와 캐시 상태를 관리하지만 재고 차감, 중복 결제 방지, 버전 충돌 같은 업무 일관성은 API와 서버가 보장해야 한다.

서버 상태를 브라우저에서 관리하는 방법을 이해했다면, Next.js에서는 서버 렌더링과 route cache까지 실행 위치를 넓혀 본다.

## 7. Next.js: 실행 위치, 라우팅, 캐시를 하나의 모델로 본다

### App Router는 URL을 컴포넌트 트리와 연결한다

`app` 디렉터리의 폴더는 route segment가 되고 `page`, `layout`, `loading`, `error`, `not-found` 같은 특별한 파일이 각 상태의 UI와 경계를 정의한다. 중첩 layout은 공통 UI와 상태 보존 범위를 만든다.

SSR은 요청 시 서버에서 HTML을 만들고, 정적 렌더링은 빌드나 재검증 시점에 미리 만들며, CSR은 브라우저 JavaScript가 화면을 구성하는 전략이다. 이것은 Server/Client Component 구분과 같은 축이 아니다. 전자는 HTML을 언제 준비하는지, 후자는 어떤 module graph가 어느 환경의 기능을 쓰는지를 설명한다.

### Server Component와 Client Component는 실행·번들 경계다

App Router의 page와 layout은 기본적으로 Server Component다. 데이터 접근, 서버 전용 비밀 사용, 브라우저로 보낼 JavaScript 감소에는 Server Component가 유리하다. 다만 비밀을 Client Component의 props나 직렬화 결과에 넣으면 결국 노출된다. state, event handler, Effect, 브라우저 API가 필요한 작은 상호작용 경계에는 `'use client'`를 둔다.

Client Component라는 이름이 “첫 화면 HTML을 서버에서 만들 수 없다”는 뜻은 아니다. 초기 방문에서는 HTML 생성에 참여할 수 있지만 브라우저용 JavaScript에 포함되고 hydration된다. `'use client'` 경계를 높게 두면 그 아래 import graph가 클라이언트 번들로 넓어지므로 필요한 곳 가까이에 둔다. 서버에서 클라이언트로 넘기는 props는 직렬화 가능한 값이어야 한다.

### Metadata, cache, 404는 서로 다른 웹 계약이다

- **Metadata:** Server Component에서 정적 `metadata` 또는 동적 `generateMetadata`를 사용하고, OG image·sitemap·robots 같은 파일 규칙으로 검색과 공유 정보를 제공한다.
- **Cache:** 브라우저·CDN·Next.js의 데이터/렌더 캐시·App Router 탐색 캐시·React 메모화·TanStack Query 브라우저 캐시는 서로 다른 층이다. 키, 수명, 재검증 계기, 사용자별 분리를 각각 정한다. `revalidateTag`와 `invalidateQueries`처럼 한 층의 무효화가 다른 층에 자동 전파되지는 않는다.
- **404:** URL에 해당하는 리소스가 존재하지 않으면 `notFound()`와 `not-found` UI를 사용한다. 검색 결과가 0개인 정상 화면이나 일시적 서버 장애를 404로 바꾸지 않는다. 현재 App Router에서는 streamed `not-found` 응답이 HTTP `200`일 수 있고 non-streamed 응답은 `404`이며, `notFound()`는 `noindex` metadata를 추가한다. 전송 상태 자체가 중요하면 streaming 전에 존재 여부를 확정한다.

Next.js의 구체적인 cache 기본값과 API는 버전 및 설정에 따라 달라진다. 2026년의 Next.js 16에서는 `cacheComponents: true`로 새 모델을 켜고 `'use cache'`, `cacheLife`, `cacheTag`로 cache 범위·수명·tag를 선언하며 `updateTag`, `revalidateTag`, `revalidatePath`로 갱신할 수 있다. 이를 켜지 않으면 previous caching model의 규칙을 따른다. 어느 모델이든 “이 데이터는 요청마다 최신이어야 하는가, 일정 시간 오래돼도 되는가, 변경 후 무엇을 무효화할 것인가”를 먼저 정하고 설치된 버전의 문서를 확인한다.

### React hydration과 Query hydration을 구분한다

- React hydration: 서버 HTML에 클라이언트 동작을 연결한다.
- Query hydration: 서버에서 미리 조회한 캐시를 클라이언트 Query cache에 복원한다.

이름은 같지만 대상이 다르다. 서버 요청마다 QueryClient를 분리하고, 브라우저로 직렬화하는 cache에 서버 전용 비밀이 포함되지 않게 한다.

기능이 기술적으로 맞게 동작하는 것과 제품에 실제 가치를 만드는 것은 다르다. 다음 단계에서는 사용자 행동을 신뢰할 수 있는 데이터로 관측한다.

---

> **Part 3 — 측정과 의사결정:** 신뢰할 수 있는 관측값을 만들고 불확실성과 인과 효과를 판단한다.

## 8. 제품 분석: 행동을 재사용 가능한 데이터 계약으로 만든다

분석 도구를 설치했다고 신뢰할 수 있는 데이터가 생기지는 않는다. 이벤트는 프론트엔드, 서버, 데이터 팀과 제품이 함께 사용하는 API 계약처럼 설계한다.

### 이벤트 schema에 포함할 것

| 항목 | 질문 |
|---|---|
| 이름과 의미 | 어떤 행동을 나타내며 비슷한 이벤트와 무엇이 다른가? |
| 발생 조건 | 렌더, 실제 노출, 클릭, 서버 확정 중 정확히 언제 한 번 보내는가? |
| 주체와 대상 | anonymous/user/session ID와 product/order ID는 무엇인가? |
| 속성 | 타입, 단위, 허용값, 필수 여부는 무엇인가? |
| 시간과 출처 | client/server timestamp와 web/app/server 중 어느 출처인가? |
| 품질 | `event_id`, `schema_version`, 중복 제거 기준과 소유자는 무엇인가? |
| 개인정보 | 목적에 필요한 최소 정보인가? 동의·보존·삭제 정책은 무엇인가? |

### 노출, 클릭, 전환을 섞지 않는다

- **노출:** 사용자가 실제로 변경 UI를 볼 기회가 있었음.
- **클릭:** 사용자가 의도를 표현함.
- **전환:** 주문 완료처럼 제품이 정의한 결과가 확정됨.

컴포넌트가 렌더됐다는 이유만으로 실제 viewport 노출로 보거나, 결제 버튼 클릭을 구매 성공으로 보면 지표가 왜곡된다. 중요한 전환은 가능하면 서버의 확정 결과를 기준으로 기록하고 `event_id`·`order_id` 등으로 중복을 제거한다. 전송은 유실과 중복이 모두 가능하므로 “정확히 한 번”이라고 가정하지 않는다.

### UTM과 유입 attribution

`utm_source`, `utm_medium`, `utm_campaign`, `utm_content` 등은 어떤 캠페인 링크가 유입을 만들었는지 설명한다. 이름 규칙, 대소문자, landing 시점 보존, 내부 링크에서 덮어쓰지 않는 정책, attribution window와 시간대를 통일해야 한다. UTM에 개인 식별 정보를 넣지 않는다.

Mixpanel 같은 분석 도구는 이벤트를 탐색하고 퍼널·리텐션을 계산하며, GTM은 tag·trigger·variable과 `dataLayer` 접점을 관리한다. Hackle 같은 실험 플랫폼은 배정과 노출·결과 분석을 돕는다. 그러나 앱이 의미 있는 이벤트와 속성을 제공해야 하며, 어떤 도구도 잘못된 schema·식별자·중복을 자동으로 올바른 제품 사실로 바꾸지는 못한다.

**핵심:** 대시보드보다 먼저 이벤트 명세, 예시 payload, 검증 방법, 변경 이력을 만든다. 신뢰할 수 있는 관측값을 얻었으면 사용자 여정의 어떤 문제를 설명할 지표인지 정한다.

## 9. 그로스: 퍼널·리텐션·CRM·광고 지표를 같은 사용자 여정에 놓는다

### 퍼널과 전환율

퍼널은 `상품 노출 → 상세 조회 → 구매 시작 → 결제 성공`처럼 선후 관계가 있는 단계를 본다. 전환율은 항상 분자와 분모, 대상 cohort, 기간, 단계 완료 시간 창, 중복 사용자 처리 기준을 함께 써야 한다. 단계 정의가 바뀌면 전환율도 다른 지표가 된다.

### 리텐션

리텐션은 가입일·첫 구매일 같은 시작 시점으로 cohort를 만들고 N일·N주 뒤에 “활성” 기준을 다시 만족한 비율을 본다. 정확히 N번째 기간에 돌아온 classic retention과 N번째 이후 한 번이라도 돌아온 rolling retention을 구분하고, 캘린더 기준인지 경과 시간 기준인지와 어떤 행동을 활성으로 볼지 명시한다. 전체 사용자를 섞은 평균은 제품 변화와 유입 mix 변화를 혼동하게 만들 수 있다.

### CRM과 광고

- CRM: 발송·도달, 클릭, 전환, 수신 거부, spam complaint, 증분 효과를 본다. 열람은 플랫폼의 개인정보 보호 기능에 영향을 받을 수 있어 핵심 결과와 함께 본다.
- 광고: impression, reach, CTR, CPC, CPM, CPA, CAC, ROAS를 목적에 맞춰 본다. CPA는 정의한 행동·획득당 비용이고 CAC는 보통 더 넓은 영업·마케팅 비용을 신규 고객 수로 나눈다. ROAS는 귀속 매출 대비 광고비이지 이익률이 아니다. 플랫폼별 attribution window와 view-through 포함 여부가 다르면 숫자를 직접 비교할 수 없다.

제품 분석, CRM, 광고 플랫폼의 숫자가 다를 때 어느 하나를 무조건 정답으로 고르지 않는다. 식별자, 시간대, 중복 제거, attribution model, 환불 반영 시점을 맞추고 질문별 권위 원본을 정한다. Attribution은 전환을 어느 채널에 배분했는지 설명할 뿐 그 채널이 전환을 추가로 만들었다는 인과 증거가 아니다. 증분 효과는 holdout이나 무작위 실험으로 확인한다.

**핵심:** 클릭률 같은 국소 지표를 높이는 것이 장기 리텐션이나 이익을 높인다는 보장은 없다. 사용자 여정과 사업 결과를 연결한 뒤 관측 차이의 불확실성을 해석한다.

## 10. 통계: 차이가 있는지와 가치가 있는지를 나눠 묻는다

| 개념 | 정확히 답하는 질문 | 흔한 오해 |
|---|---|---|
| 점추정치 | 관측된 효과 크기는 얼마인가? | 표본의 차이가 참값과 정확히 같다고 봄 |
| 신뢰구간 | 반복 표집 절차에서 참값을 포함하도록 만든 효과 범위는 어디인가? | 관측 후 참값이 이 구간에 있을 확률이 95%라고 단정함 |
| p-value | 귀무가설과 모델이 맞을 때 지금만큼 극단적인 결과가 나올 확률은? | 귀무가설이 참일 확률 또는 우연일 확률로 해석함 |
| 유의수준 `α` | 참된 귀무가설을 기각할 장기 오류율을 얼마로 제한할까? | 결과를 본 뒤 편한 기준으로 바꿈 |
| 검정력 `1-β` | 정한 크기의 실제 효과가 있을 때 이를 발견할 확률은? | 유의하지 않으면 효과가 없다고 확정함 |
| MDE | 이 설계가 목표 검정력으로 감지하도록 만든 최소 효과는? | 제품에 의미 있는 최소 효과와 자동으로 같다고 봄 |

표본이 작으면 신뢰구간이 넓고, 유의하지 않은 결과도 큰 개선과 악화를 모두 포함할 수 있다. 반대로 표본이 매우 크면 제품 가치가 거의 없는 작은 차이도 통계적으로 유의할 수 있다.

예를 들어 전환율이 `10.0%`에서 `10.5%`가 되면 절대 변화는 `+0.5%p`, 상대 변화는 `+5%`다. 둘 중 유리한 표현만 고르지 말고 기준값, 절대·상대 효과와 신뢰구간을 함께 보고한다.

따라서 의사결정은 다음을 함께 본다.

- 효과의 방향과 크기
- 신뢰구간이 포함하는 최선·최악의 시나리오
- 개발·운영·기회비용을 넘는 실질적 유의성
- guardrail의 악화 가능성
- 세그먼트 분석과 다중 검정이 사전에 계획됐는지

**핵심:** p-value 하나는 의사결정 규칙이 아니다. 추정치, 불확실성, 비용과 위험을 함께 설명한다. 이 언어를 무작위 배정과 표본 설계에 적용하면 실험이 된다.

## 11. 실험: 무작위 배정에서 의사결정까지 신뢰 사슬을 지킨다

### 안정적인 실험군 배정

렌더할 때마다 `Math.random()`으로 군을 고르면 같은 사용자가 A와 B를 오가며 비교가 깨진다. `experiment_id + assignment_unit_id`와 고정된 namespace·salt를 균등하게 hashing해 bucket을 정하고, 동일한 실험과 사용자에게 같은 군을 반환한다. 트래픽 비율을 바꿀 때 기존 사용자가 불필요하게 재배정되지 않는 정책과 배정 로그도 필요하다. 여기서 assignment unit이 사용자, 계정, 기기, 세션 중 무엇인지 제품 효과와 간섭 가능성에 맞춰 먼저 정한다.

로그인 전후 ID 연결, 여러 기기, bot·직원 제외, 실험 간 상호작용도 정책이 필요하다. **배정**은 군을 정한 것, **trigger**는 실험 참여 조건 충족, **served/rendered**는 변경 전달, **viewable**은 실제 볼 수 있었던 상태다. 필요에 맞게 구분해 기록하되 처리 방식이 노출 자체에 영향을 줄 때 “실제로 본 사람”만 사후 선택해 비교하면 편향이 생긴다. 기본 분석은 배정 기준의 ITT를 지키고, trigger 기반 분석은 trigger가 처리군의 영향을 받지 않을 때 사용한다.

### 시작 전에 정할 것

1. 가설과 기대하는 인과 경로
2. primary metric과 계산 단위·분모
3. 오류율·취소율·지연·불만 같은 guardrail
4. 유의수준, 검정력, 기준 전환율, MDE와 필요한 표본 수
5. 최소 실행 기간, 종료 규칙, 제외 기준과 분석 방법

표본 수는 “며칠 돌릴지”를 감으로 정하는 값이 아니다. 기준 비율, 변동성, 감지할 최소 효과, 유의수준과 검정력의 함수다. 사용자 단위로 배정하고 클릭 각각을 독립 표본처럼 계산하면 정밀도를 과장하므로 지표를 배정 단위로 집계하거나 군집 구조를 반영한다. 필요한 표본을 채워도 요일 주기와 지연 전환을 포함할 최소 기간이 필요하다. 중간 결과를 반복 확인해 유리한 순간에 멈추려면 그에 맞는 순차 검정 방법을 사전에 사용해야 한다.

### SRM을 효과보다 먼저 본다

Sample Ratio Mismatch는 실제 군별 표본 비율이 계획한 비율과 통계적으로 맞지 않는 현상이다. 특정 군의 로깅 누락, 배정 버그, 필터링 차이, 성능 장애 같은 신뢰성 문제의 증상일 수 있다. 원인을 해결하기 전에는 전환율 차이를 해석하지 않는다.

그다음 instrumentation과 invariant metric, 군별 사용자 특성, guardrail을 확인한 뒤 primary metric 효과를 본다. Guardrail에는 허용 가능한 악화 한계와 중단 규칙, 이를 판별할 검정력이 필요하다. `p > 0.05`만으로 안전함이 증명되는 것은 아니다. “B가 숫자로 더 큼”만으로 승자를 정하지 않는다.

---

> **Part 4 — 출시와 운영:** 기능이 실제 환경에서 사용 가능하고 안전하며 복구 가능한지 확인한다.

## 12. 품질: 사용 가능하고 빠르며 안전하고 발견 가능한가

### 접근성

의미에 맞는 HTML, 접근 가능한 이름, 키보드 조작, 보이는 focus, 충분한 대비, 오류와 상태 변화 안내를 기본으로 설계한다. 컴포넌트 라이브러리가 지원하더라도 조합 과정에서 label·focus 순서·heading 구조가 깨질 수 있다. 자동 검사는 일부 문제만 찾으므로 키보드와 스크린 리더를 포함한 수동 검증이 필요하다.

### Web Vitals와 성능

Core Web Vitals는 로딩의 LCP, 상호작용 반응성의 INP, 시각적 안정성의 CLS를 서로 다른 관점에서 본다. 개발 장비의 lab 측정은 원인 분석에 유용하고 실제 사용자 field data는 다양한 기기·네트워크의 경험을 보여준다. 둘을 함께 사용하며 bundle, 이미지, 서버 응답, main-thread long task와 렌더링 병목을 원인별로 측정한다.

### SEO

검색 엔진이 URL을 발견하고, 접근하고, 올바른 상태 코드와 canonical을 이해하며, 핵심 콘텐츠를 렌더하고 색인할 수 있어야 한다. title·description·OG metadata만이 아니라 내부 링크, sitemap, robots, 중복 URL, structured data, 404/redirect와 콘텐츠 품질까지 확인한다. `robots.txt`는 crawl을 제어하며 확실한 색인 제외 수단이 아니고, sitemap 제출도 색인을 보장하지 않는다.

### 보안

- 인증과 인가를 구분하고, 모든 보호 대상 요청의 권한을 서버에서 기본 거부 원칙으로 확인한다.
- 외부 입력은 검증하고 출력 맥락에 맞게 인코딩해 XSS를 막는다. SQL·명령·template injection에는 문자열 결합 대신 매개변수화된 query와 안전한 API를 사용한다.
- cookie 기반 변경 요청은 SameSite 정책과 CSRF 방어를 검토한다.
- CSP는 피해를 줄이는 방어층이지 안전한 코드의 대체물이 아니다.
- 비밀 키는 브라우저 bundle에 넣지 않으며, CORS는 인증이나 권한 제어가 아니다.
- 의존성, 업로드, redirect, URL scheme 같은 경계도 공격 표면으로 본다.

### 개인정보

필요한 정보만 수집하고 목적, 관할 법률에 맞는 법적 근거, 필요한 경우 유효한 동의, 보존 기간, 접근 권한, 삭제와 제3자 전송을 설계한다. 분석 이벤트·URL·로그에 토큰이나 불필요한 개인 식별 정보를 넣지 않는다. 익명 ID도 다른 데이터와 결합해 개인을 식별할 수 있는지 검토한다.

## 13. 모바일: WebView Bridge를 버전 있는 비동기 API로 설계한다

WebView의 JavaScript와 iOS·Android 네이티브 코드는 서로 다른 실행 환경이며 배포 속도도 다르다. 브리지는 단순 함수 호출처럼 보여도 실제로는 직렬화, 권한, 시간 지연과 버전 차이가 있는 RPC 경계다.

메시지에는 보통 다음 계약이 필요하다.

```ts
type BridgeRequest = {
  id: string;
  method: string;
  protocolVersion: number;
  payload: unknown;
};
```

- 요청 ID로 동시에 진행된 응답을 올바른 Promise에 연결한다.
- 성공, 업무 오류, 사용자 취소, timeout, WebView 종료를 구분한다.
- 늦게 도착한 응답과 중복 응답은 이미 끝난 요청을 다시 완료시키지 않게 폐기한다.
- 앱 버전 문자열만 비교하기보다 지원 method·capability를 협상하고 fallback을 제공한다.
- origin을 식별할 수 있는 message API에서는 허용 origin과 main frame 여부를 검사하고 method를 제한하며 payload를 양쪽에서 검증한다. Android `addJavascriptInterface`는 모든 frame에 노출되고 호출 frame의 origin을 식별할 수 없으므로 신뢰한 navigation만 허용하고 외부 콘텐츠에는 직접 bridge를 노출하지 않는다. iOS의 content world 분리도 origin 인가를 대신하지 않는다.
- 새로고침·navigation 때 session을 바꾸고 이전의 대기 요청을 정리한다.

timeout은 호출자가 정한 시간 안에 결과를 받지 못했다는 뜻이지, 네이티브나 서버 작업이 실패하거나 취소됐다는 증명은 아니다. 결제 같은 작업은 멱등성 키와 상태 조회를 함께 사용해야 한다.

브리지 밖에서도 소프트 키보드, Safe Area, 뒤로 가기, cookie·로그인 상태, 외부 링크, 파일 처리와 앱 background/foreground 생명주기를 확인한다. 일반 브라우저에서 정상인 화면이 WebView에서도 동일하게 동작한다는 보장은 없다.

자세한 구현 방식과 보안 차이는 [WebView와 네이티브 앱의 브리지 통신 설계](webview-native-bridge-communication.md)에서 다룬다.

## 14. 운영 도구: 상태 전이, 권한, 감사 가능성이 UI보다 먼저다

관리자 화면은 소수만 사용하더라도 한 번의 실수가 많은 사용자와 데이터에 영향을 줄 수 있다.

### 상태 머신

주문이 `결제 대기 → 결제 완료 → 배송 중 → 완료`로 이동한다면 허용된 전이와 금지된 전이, 전이 조건과 부수 효과를 명시한다. 버튼 노출뿐 아니라 서버가 현재 상태와 권한을 다시 검사한다. boolean 여러 개보다 판별 상태와 전이 표가 불가능한 조합을 줄인다.

### 권한

역할 기반 권한만으로 부족하면 리소스 소유 조직, 금액, 현재 상태 같은 속성까지 검사한다. 목록 조회, 상세 조회, 변경, export를 별도 권한으로 볼 수 있다. UI에서 버튼을 숨기는 것은 편의 기능이지 보안 경계가 아니다.

### Audit log

누가, 언제, 어떤 대상에, 어떤 행동을, 왜 수행했고 결과가 무엇인지 추적한다. 중요한 변경은 이전/이후 값, request ID, 승인자와 사유를 남기되 비밀과 불필요한 개인정보는 마스킹한다. 상태 변경과 감사 기록은 가능한 한 같은 transaction으로 묶고, append-only 또는 tamper-evident 저장, 접근 통제와 보존 정책을 둔다. 결제·알림 같은 외부 부수 효과는 outbox, 멱등성, 재조정 절차로 복구 가능하게 만든다.

### 동시 수정과 위험 작업

version/ETag로 조용한 덮어쓰기를 막고 충돌 내용을 보여준다. 장시간 편집에는 임시 저장이나 lock이 필요할 수 있지만 만료와 복구 정책도 필요하다. 대량 변경·삭제에는 영향 범위 preview, 명시적 확인, dry run, 단계적 실행, 취소 또는 보상 작업을 설계한다.

이 권한·전이·충돌 규칙은 문서에만 두지 않고 재현 가능한 테스트 시나리오로 바꾼다.

## 15. 검증: 테스트 종류를 사용자 위험에 맞게 겹친다

| 층 | 잘 찾는 문제 | 원칙 |
|---|---|---|
| 정적 검사 | 타입 불일치, lint 규칙, 잘못된 import | 빠르게 모든 변경에 실행한다. |
| 단위 테스트 | 계산, reducer, validator, state transition | 순수 로직의 경계값을 촘촘히 본다. |
| 컴포넌트/통합 테스트 | 폼, 로딩·오류, 접근 가능한 상호작용, API 연동 | Testing Library로 role·label 등 사용자 관점에서 찾는다. |
| E2E | 로그인·구매·권한처럼 실제 시스템 경계의 핵심 여정 | Playwright로 가치가 큰 흐름을 적게, 독립적으로 유지한다. |
| 비기능 검증 | 접근성, 시각 회귀, 성능, 보안 | 자동 검사와 수동·운영 관측을 조합한다. |

구현 세부 함수나 CSS class보다 사용자가 보고 조작하는 결과를 검증한다. 모든 조합을 E2E로 만들기보다 빠른 하위 테스트로 경우의 수를 다루고, E2E는 경계가 실제로 연결되는지 확인한다.

Playwright 테스트는 각자 독립된 상태에서 실행하고 role·label 같은 사용자 중심 locator와 자동 대기를 사용한다. 고정 sleep은 실제 완료 조건을 표현하지 못해 느리고 불안정하다. 재시도로 계속 통과시키기보다 flaky 원인과 격리 실패를 고친다.

비동기 기능에는 정상 응답뿐 아니라 다음 시나리오를 의도적으로 만든다.

- 응답 순서를 뒤집어 오래된 결과가 화면을 덮는지 확인
- 빠른 중복 클릭과 같은 idempotency key 재전송
- timeout, offline, `429`·`5xx` 뒤 제한된 재시도
- 컴포넌트 unmount와 route 이동 중 완료
- 낙관적 업데이트 실패와 동시에 진행된 mutation
- 서버 version 충돌과 재조회·병합 UI
- 분석 이벤트 schema와 동의 상태, 중복·누락
- 실험 배정의 결정성·분포·상호 배타성과 노출 기록

접근성 자동 검사는 누락된 label과 일부 대비 문제를 찾지만 모든 WCAG 문제를 판단하지 못한다. 키보드, focus 이동, 스크린 리더 표현과 실제 과업 완료도 확인한다.

---

> **Part 5 — 협업과 설명:** 개인의 올바른 판단을 팀의 반복 가능한 절차와 증거로 만든다.

## 16. 개발 문화: 반복되는 결정을 시스템으로 만든다

### 디자인 시스템

색상·간격·타이포 같은 token, Button·Dialog 같은 component, 폼 오류·확인 흐름 같은 pattern, 접근성 기준과 기여·버전 정책을 함께 관리한다. Mantine 같은 라이브러리는 구현 기반이 될 수 있지만 제품의 사용 원칙까지 대신하지 않는다. 웹과 네이티브는 token과 원칙을 공유하되 실제 컴포넌트 구현은 달라질 수 있다.

### 모노레포와 선택적 분리

모노레포는 여러 앱과 패키지를 한 저장소에서 관리해 타입·검증·디자인 token·도구 설정을 공유하고 변경을 함께 검증하는 방식이다. pnpm workspace는 패키지 연결을, Turborepo 같은 도구는 작업 graph와 cache를 도울 수 있다. 같은 저장소라고 모든 코드를 공유하거나 함께 배포해야 하는 것은 아니다. 공개 API, 의존 방향, package owner와 변경 영향 범위를 관리한다.

공용 코드는 플랫폼 경계를 감춘 척하지 않는다. 예를 들어 인증 서비스가 `localStorage`를 직접 읽는 대신 `getAccessToken()` 같은 interface를 받고 웹·앱 adapter가 구현하면 정책과 타입은 공유하면서 실행 환경 차이는 분리할 수 있다.

팀별 독립 배포가 실제 병목이면 Micro Frontend와 Module Federation 같은 런타임 조합을 검토할 수 있다. 대신 네트워크 실패, React·디자인 시스템 버전, routing·auth·event 계약, CSS 격리와 rollback 비용이 생긴다. 조직 문제가 작다면 이 복잡성이 이득보다 클 수 있다.

### CI/CD

CI는 format·lint·typecheck·test·build·보안 검사를 재현 가능하게 실행한다. CD는 artifact를 환경에 전달하고 migration 순서, 환경별 설정, health check, 관측, 점진 배포와 rollback을 관리한다. 같은 commit에서 만든 불변 artifact를 승격하면 환경별 차이를 줄일 수 있다.

Feature flag는 배포와 공개를 분리하지만 오래된 flag 정리, 기본값, 서버·클라이언트 일관성, 장애 시 안전한 값이 필요하다. DB와 API 변경은 구버전과 신버전이 함께 실행되는 배포 구간을 견디도록 하위 호환 순서로 진행한다. Continuous Delivery는 운영 배포가 언제든 가능한 상태를 유지하고, Continuous Deployment는 검증을 통과한 변경을 운영까지 자동 배포하는 관행이다.

### Git과 코드 리뷰

작고 목적이 분명한 commit과 PR은 원인 추적과 rollback을 쉽게 한다. PR에는 문제, 변경 이유, 대안, 영향 범위, 테스트 증거, 배포·관측·rollback 계획을 남긴다. 코드 리뷰는 취향 경쟁이 아니라 정확성, 상태·동시성, 보안·개인정보, 접근성, 운영 가능성과 이해 가능성을 확인하는 과정이다. format처럼 자동화 가능한 논쟁은 도구에 맡긴다.

## 17. 제출과 인터뷰: 구현을 검증 가능한 이야기로 바꾼다

### README

좋은 README는 다음 질문에 짧게 답한다.

1. 어떤 사용자 문제를 해결하는가?
2. 어떻게 실행하고 필수 환경 변수를 설정하는가?
3. 주요 구조와 데이터 흐름은 무엇인가?
4. 어떤 명령으로 검사·테스트·빌드하는가?
5. 핵심 기술 결정과 trade-off는 무엇인가?
6. 알려진 한계, 보안 고려사항과 다음 단계는 무엇인가?
7. 데모·배포 주소와 검증 가능한 결과는 어디에 있는가?

### 기술 결정 기록

“TanStack Query를 사용했다”보다 **맥락 → 제약 → 검토한 대안 → 선택 → 감수한 단점 → 결과**를 남긴다. 결정 당시의 정보와 날짜를 보존하고, 나중에 뒤집으면 기존 기록을 지우지 말고 대체 결정을 연결한다.

### AI 사용 기록

제출 규칙이 요구하거나 재현성에 도움이 된다면 AI가 도운 작업 범위, 중요한 제안, 사람이 채택·수정·거절한 내용, 사실·코드·보안·생성물 출처와 license를 검증한 방법, 남은 위험을 기록한다. 비밀·개인정보·타인의 비공개 코드를 prompt나 기록에 포함하지 않는다. “AI가 작성함”보다 **무엇을 어떻게 검증했는지**가 중요하다.

### 인터뷰 답변 구조

기술 이름을 나열하지 말고 다음 순서로 설명한다.

```text
문제와 사용자 영향
→ 제약과 실패 조건
→ 검토한 대안
→ 선택과 trade-off
→ 구현에서 지킨 경계
→ 테스트·지표·운영 결과
→ 다시 한다면 바꿀 점
```

예를 들어 “race condition을 AbortController로 해결했다”에서 끝내지 않는다. 어떤 오래된 응답이 어떤 사용자 문제를 만들었는지, 응답 무시와 취소 중 왜 그 방법을 골랐는지, 서버 작업은 취소되지 않을 수 있음을 어떻게 처리했는지, 응답 순서를 뒤집은 테스트로 무엇을 검증했는지까지 말한다.

실제 출시·측정하지 않은 결과는 기대 효과나 가설로 표시하고, 관측한 성과처럼 말하지 않는다.

---

## 전체 연결 예시: 상품 구매 기능을 출시한다면

1. **실행:** 검색·재고 조회의 늦은 응답이 최신 화면을 덮지 않게 요청 수명과 취소를 설계한다.
2. **타입:** API·URL·storage 입력은 런타임 검증 후 `Product`와 `Order` 타입으로 변환한다.
3. **React:** 렌더는 순수하게 유지하고 구독·요청은 cleanup 가능한 Effect 또는 데이터 계층에 둔다.
4. **상태:** 상품은 서버 상태, 검색어와 필터는 URL, 수량은 폼, 모달은 지역 상태로 둔다.
5. **API:** 주문 생성에 idempotency key를 사용하고 재고 version 충돌은 서버에서 거부한다.
6. **데이터:** 상품 query key와 신선도를 정하고 주문 mutation 뒤 관련 재고·주문 query를 갱신한다.
7. **Next.js:** 공개 상품은 Server Component에서 가져오고 수량·구매 상호작용만 Client Component 경계로 둔다. 없는 상품은 404 의미로 처리한다.
8. **분석:** 상품 노출, 구매 클릭, 서버의 결제 성공을 다른 이벤트로 기록하고 주문 ID로 중복을 제거한다.
9. **그로스:** 유입 UTM부터 구매와 재구매 cohort까지 연결하되 플랫폼별 attribution 차이를 문서화한다.
10. **통계·실험:** 효과 크기와 신뢰구간을 이해한 뒤 안정적으로 군을 배정하고 SRM·오류율을 확인한다.
11. **품질·모바일:** 키보드·스크린 리더·LCP/INP/CLS·SEO·보안·개인정보를 확인하고 WebView에서는 bridge capability와 timeout을 처리한다.
12. **운영·검증:** 관리자 주문 상태를 상태 머신과 권한으로 보호하고 audit log를 남기며, 중복 클릭·역순 응답·충돌을 자동 테스트한다.
13. **협업·제출:** 공용 계약과 디자인 token을 적절한 package로 관리하고 CI/CD, README, 결정과 검증 근거를 남긴다.

각 기술의 가치는 “무엇을 썼는가”보다 **어떤 경계의 어떤 실패를 줄였고, 무엇은 여전히 다른 계층의 책임으로 남는가**로 설명할 수 있어야 한다.

## 읽은 뒤 자기점검

1. **JavaScript·브라우저:** Promise와 microtask가 왜 화면 갱신과 race condition에 영향을 주는지 설명할 수 있는가?
2. **TypeScript·React:** 정적 타입과 런타임 검증, 렌더와 Effect를 구분할 수 있는가?
3. **상태·API:** 값마다 원본 소유자를 정하고 재시도·중복·동시 수정의 책임을 나눌 수 있는가?
4. **데이터·Next.js:** 클라이언트와 서버의 cache 신선도, 실행 위치와 무효화 정책을 구분할 수 있는가?
5. **분석·그로스·통계·실험:** 이벤트 정의부터 퍼널, 신뢰구간, SRM과 실질적 유의성까지 연결할 수 있는가?
6. **품질·운영:** 접근성·성능·보안·개인정보·모바일·관리자 위험을 출시 조건으로 검증할 수 있는가?
7. **문화·제출:** 결정의 이유, 대안, 검증 증거와 한계를 다른 사람이 재현할 수 있게 남길 수 있는가?

## 참고 자료

- [MDN: Promise](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise), [`fetch`](https://developer.mozilla.org/en-US/docs/Web/API/Window/fetch), [`AbortSignal`](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal)
- [TypeScript Narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing), [Generics](https://www.typescriptlang.org/docs/handbook/2/generics.html)
- [React: Keeping Components Pure](https://react.dev/learn/keeping-components-pure), [You Might Not Need an Effect](https://react.dev/learn/you-might-not-need-an-effect), [`useEffect`](https://react.dev/reference/react/useEffect), [`StrictMode`](https://react.dev/reference/react/StrictMode), [`hydrateRoot`](https://react.dev/reference/react-dom/client/hydrateRoot)
- [TanStack Query Important Defaults](https://tanstack.com/query/latest/docs/framework/react/guides/important-defaults), [Query Invalidation](https://tanstack.com/query/latest/docs/framework/react/guides/query-invalidation), [Optimistic Updates](https://tanstack.com/query/latest/docs/framework/react/guides/optimistic-updates)
- [Next.js App Router](https://nextjs.org/docs/app), [Server and Client Components](https://nextjs.org/docs/app/getting-started/server-and-client-components), [Cache Components](https://nextjs.org/docs/app/api-reference/config/next-config-js/cacheComponents), [Revalidating](https://nextjs.org/docs/app/getting-started/revalidating), [Metadata](https://nextjs.org/docs/app/getting-started/metadata-and-og-images), [`notFound`](https://nextjs.org/docs/app/api-reference/functions/not-found)
- [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110), [RFC 6585: Additional HTTP Status Codes](https://www.rfc-editor.org/rfc/rfc6585), [IETF Idempotency-Key 초안](https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/)
- [Android WebView Native Bridge 보안](https://developer.android.com/privacy-and-security/risks/insecure-webview-native-bridges), [`WebViewCompat.addWebMessageListener`](https://developer.android.com/reference/androidx/webkit/WebViewCompat#addWebMessageListener), [Apple `WKScriptMessage`](https://developer.apple.com/documentation/webkit/wkscriptmessage)
- [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/), [Core Web Vitals](https://web.dev/articles/vitals), [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Testing Library Guiding Principles](https://testing-library.com/docs/guiding-principles), [Playwright Best Practices](https://playwright.dev/docs/best-practices), [Playwright Accessibility Testing](https://playwright.dev/docs/accessibility-testing)
- [Microsoft Research: Diagnosing Sample Ratio Mismatch](https://www.microsoft.com/en-us/research/publication/diagnosing-sample-ratio-mismatch-in-online-controlled-experiments-a-taxonomy-and-rules-of-thumb-for-practitioners/), [NIST: Confidence Intervals](https://www.itl.nist.gov/div898/handbook/prc/section1/prc14.htm)
- [Google Analytics: Campaign URL parameters](https://support.google.com/analytics/answer/10917952), [Transaction ID를 이용한 구매 중복 제거](https://support.google.com/analytics/answer/12313109)
- [pnpm Workspaces](https://pnpm.io/workspaces), [Turborepo Caching](https://turborepo.com/docs/crafting-your-repository/caching), [Module Federation shared configuration](https://module-federation.io/configure/shared), [Mantine Theme](https://mantine.dev/theming/theme-object/), [Google Tag Manager data layer](https://developers.google.com/tag-platform/tag-manager/datalayer)

## 관련 문서

- [JavaScript 기본 개념 요약](javascript-basics.md)
- [이벤트 루프와 브라우저 렌더링 타이밍](event-loop-rendering-timing.md)
- [렌더링 파이프라인과 성능 병목 진단](rendering-pipeline-performance.md)
- [WebView와 네이티브 앱의 브리지 통신 설계](webview-native-bridge-communication.md)
- [Playwright로 React 컴포넌트 스크린샷을 생성하고 PR에서 검토하기](playwright-react-component-screenshot-pr-review.md)
