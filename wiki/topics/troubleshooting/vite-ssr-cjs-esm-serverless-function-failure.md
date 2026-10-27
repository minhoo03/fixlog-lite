---
id: topic-vite-ssr-cjs-esm-serverless-function-failure
title: Vite SSR 서버리스 환경의 CJS·ESM 호환성 장애
summary: Vite SSR에서 외부화된 CommonJS 패키지가 ESM-only 의존성을 require해 배포 함수가 실패한 문제와, noExternal 적용 후 로컬 dev에서 require가 정의되지 않은 후속 문제를 각각 ssr.noExternal과 SSR optimizeDeps로 해결한 과정을 정리한다.
aliases:
  - Vite SSR ERR_REQUIRE_ESM
  - FUNCTION_INVOCATION_FAILED 원인
  - sanitize-html htmlparser2 호환성
  - SSR noExternal 설정
  - Vite SSR require is not defined
  - SSR optimizeDeps include
tags:
  - vite
  - ssr
  - serverless
  - commonjs
  - esm
  - nodejs
  - dependency-optimization
  - debugging
type: topic
status: active
created: 2026-10-26
updated: 2026-10-27
index: true
related:
  - topic-frontend-web-mobile-core-concepts
---

# Vite SSR 서버리스 환경의 CJS·ESM 호환성 장애

## 핵심 요약

- `<문서 표시 기능>`에 `sanitize-html@2.18.1`을 추가한 뒤, 배포된 서버리스 함수가 초기화 단계에서 실패해 `500 FUNCTION_INVOCATION_FAILED`를 반환했다.
- `sanitize-html@2.18.1`은 CommonJS 형식이며 시작 시 `require('htmlparser2')`를 실행한다. 의존하는 `htmlparser2@12`는 ESM-only 패키지다.
- Vite SSR 빌드가 이 패키지들을 외부화하면 해당 모듈 연결은 빌드 시점에 처리되지 않고 배포 런타임의 Node 모듈 로더에 남는다. 런타임이 `require(ESM)`을 지원하지 않거나 비활성화한 환경이면 모듈 초기화가 실패한다.
- `ssr.noExternal`에 `sanitize-html`과 `htmlparser2`를 추가해 둘을 SSR 결과물에 번들링하면, 문제가 된 런타임 `require()` 경계를 빌드 시점에 해소할 수 있다.
- 이 수정 뒤에는 로컬 dev의 SSR 모듈 러너가 사전 변환되지 않은 `sanitize-html`의 CommonJS `require()`를 평가해 `require is not defined`가 발생했다. `environments.ssr.optimizeDeps.include`에 `sanitize-html`을 추가해 dev 전용 사전 번들링으로 해결했다.
- 초기 조사에서 언급된 “`htmlparser2`는 v9부터 ESM-only”라는 설명은 정확하지 않다. 공식 변경 이력 기준으로 ESM-only 전환은 v11부터다.

## 장애 정보

| 항목 | 내용 |
|---|---|
| 증상 | 배포 환경에서 `500 FUNCTION_INVOCATION_FAILED` 발생 |
| 계기 | `<문서 표시 기능>`에 HTML 정제 로직 추가 |
| 직접 의존성 | `sanitize-html@2.18.1` |
| 전이 의존성 | `htmlparser2@12.x` |
| 실패 경계 | CommonJS의 `require()` → ESM-only 모듈 |
| 사용 위치 | `<웹 앱>/<문서 기능>/sanitize.ts` |
| 수정 위치 | `<프로젝트 루트>/vite.config.ts` |

내부 기능명, 업무 번호, 커밋 해시, 저장소명과 실제 경로는 공개 가능한 형태로 마스킹했다.

## 먼저 알아둘 개념

### SSR

SSR(Server-Side Rendering)은 서버가 요청을 받아 React 등의 화면 코드를 실행하고, 브라우저에 보낼 초기 HTML을 만드는 방식이다. 브라우저 전용 코드만 있는 CSR과 달리, SSR에 포함된 애플리케이션 코드와 패키지는 배포 서버의 Node.js 환경에서도 실행된다.

따라서 화면에서 사용하는 패키지라도 SSR 모듈 그래프에 들어오면 서버 코드와 같은 로딩 규칙의 영향을 받는다. 라우트 모듈을 서버 시작 시 미리 불러오는 구조라면 특정 화면에 추가한 패키지의 로드 실패가 해당 화면에만 머물지 않고 서버 함수 전체의 초기화를 막을 수 있다.

### CommonJS와 ESM

CommonJS(CJS)는 Node.js에서 오래 사용한 모듈 형식이다.

```js
const parser = require('htmlparser2');
module.exports = sanitize;
```

ES Modules(ESM)은 JavaScript 표준 모듈 형식이다.

```js
import { Parser } from 'htmlparser2';
export { sanitize };
```

두 형식은 모듈을 찾고 평가하며 내보낸 값을 연결하는 방법이 다르다. 최신 Node.js는 일정 조건에서 CJS의 `require()`로 동기식 ESM을 불러올 수 있지만, Node 버전이 오래됐거나 서버리스 제공자가 해당 기능을 비활성화했다면 `ERR_REQUIRE_ESM`이 발생할 수 있다. Node.js 22.12.0부터 `require(ESM)` 지원이 기본 활성화됐지만, 실행 환경 설정에 따라 사용할 수 없는 경우도 있으므로 배포 런타임을 확인해야 한다.

### 런타임

런타임은 빌드가 끝난 코드를 실제로 실행하는 환경이다. 여기에는 Node.js 버전, 활성화된 실행 플래그, 운영체제, 배포 파일 구조, 환경 변수와 모듈 로딩 방식이 포함된다.

같은 소스라도 로컬 개발 서버와 서버리스 런타임의 조건이 다르면 결과가 달라질 수 있다. “빌드 성공”은 “배포 런타임에서 모든 모듈을 정상 로드한다”는 뜻이 아니다.

### 번들링과 외부화

번들링은 애플리케이션과 의존 모듈을 분석·변환해 배포 결과물 안에 포함하는 과정이다. 외부화(externalization)는 특정 패키지를 번들 안에 넣지 않고, 배포 런타임이 `node_modules`에서 직접 불러오도록 남겨두는 방식이다.

Vite는 SSR에서 일반 의존성을 기본적으로 외부화하고, `ssr.noExternal`에 지정한 의존성은 외부화하지 않고 빌드 결과물에 포함한다. 외부화는 패키지를 배포에서 완전히 제거한다는 뜻이 아니라, 애플리케이션 번들 내부로 합치지 않는다는 뜻이다.

## SSR에서 모든 의존성을 번들에 넣지 않는 이유

외부화는 다음과 같은 비용을 줄인다.

- 이미 Node.js에서 바로 실행할 수 있는 패키지를 다시 변환하는 빌드 비용
- 하나의 서버 번들에 모든 의존성을 합칠 때 커지는 결과물과 소스맵
- Node 전용 패키지, 네이티브 애드온, 조건부 exports를 번들러가 잘못 변환할 위험
- 개발 중 의존성까지 반복 처리하면서 생기는 시작 시간과 변경 반영 비용

서버리스에서는 배포 크기와 콜드 스타트도 고려 대상이다. 그래서 “기본은 외부화하고, 변환이 필요한 패키지만 선택적으로 번들링”하는 방식이 합리적이다. `ssr.noExternal: true`로 모든 패키지를 포함시키기보다 문제가 확인된 패키지만 지정하는 편이 영향 범위를 통제하기 쉽다.

## 첫 번째 장애: 배포 함수가 실패한 흐름

```text
SSR 서버 진입점
  → <문서 기능>의 sanitize 모듈 로드
    → 외부화된 sanitize-html 로드(CommonJS)
      → require('htmlparser2')
        → htmlparser2@12 로드 시도(ESM-only)
          → 런타임에서 require(ESM) 불가
            → 모듈 초기화 실패
              → 서버리스 함수 호출 실패
```

세부 흐름은 다음과 같다.

1. `sanitize-html@2.18.1`의 진입 파일은 CommonJS이며 첫 줄에서 `htmlparser2`를 `require()`한다.
2. 이 버전은 `htmlparser2@^12.0.0`을 의존하고, `htmlparser2@12`의 패키지 형식은 ESM이다.
3. 두 패키지가 SSR 번들에서 외부화되면 이 연결은 배포 런타임의 Node 모듈 로더가 직접 처리한다.
4. 해당 런타임에서 CJS가 ESM을 `require()`할 수 없으면 모듈 평가 중 예외가 발생한다.
5. 요청 처리 함수가 준비되기 전에 초기화가 실패하므로 플랫폼은 정상 응답 대신 `FUNCTION_INVOCATION_FAILED`를 반환한다. 함수 프로세스는 종료되거나 재활용될 수 있다.
6. 서버 엔트리가 여러 라우트를 한 함수에 포함하고 라우트 모듈을 미리 로드한다면, 문제의 기능을 직접 방문하지 않은 요청도 같은 초기화 실패의 영향을 받을 수 있다.

## 첫 번째 장애가 로컬 개발에서는 재현되지 않은 이유

Vite 개발 서버와 배포용 SSR 결과물은 패키지를 처리하는 경로가 같지 않을 수 있다. 개발 서버는 요청 시 모듈을 변환하고 ESM 기반 로딩을 중개하므로 호환성 문제가 가려질 수 있다. 반면 배포 빌드에서 외부화된 패키지는 Node가 직접 해석한다.

따라서 아래 결과가 동시에 나올 수 있다.

- 로컬 `dev`: 정상
- 프로덕션 빌드: 성공
- 배포 함수의 콜드 스타트 또는 첫 요청: 모듈 초기화 실패

로컬 확인은 개발 서버만으로 끝내지 말고, 배포와 같은 Node 버전·실행 옵션으로 프로덕션 SSR 결과물을 직접 실행해야 한다.

## 첫 번째 장애 해결: SSR 번들에 패키지 포함

기존 `ssr.noExternal` 목록에 두 패키지를 추가한다.

```ts
export default defineConfig({
  ssr: {
    // ESM/CJS 상호 운용 문제가 있는 패키지는 SSR 결과물에 포함한다.
    noExternal: [
      'styled-components',
      'react-slick',
      'slick-carousel',
      'sanitize-html',
      'htmlparser2',
    ],
  },
});
```

이 설정은 Vite가 두 패키지를 SSR 빌드 과정에서 분석하고 결과물에 포함하게 한다. 그러면 배포 런타임이 `sanitize-html`의 `require('htmlparser2')` 연결을 그대로 수행하지 않아도 된다.

두 패키지를 함께 지정하는 이유는 직접 의존성만 번들링하고 전이 의존성이 다시 외부화되는 여지를 없애, 문제가 발생한 모듈 경계 전체를 명시적으로 빌드 대상에 넣기 위해서다.

### `noExternal`이 이 문제를 해결하는 원리

`ssr.noExternal`에 등록된 패키지는 외부 의존성으로 남지 않는다. Vite는 빌드할 때 해당 패키지의 소스까지 모듈 그래프에 포함해 읽고, 필요한 변환을 거쳐 SSR 번들에 통합한다.

이 과정에서 다음과 같은 변화가 생긴다.

- 외부화 상태에서는 `require('htmlparser2')`가 배포된 `node_modules`의 패키지를 런타임에 찾는 호출로 남는다.
- 번들링 상태에서는 `sanitize-html`과 `htmlparser2`의 연결을 Vite가 빌드 시점에 해석한다. CommonJS와 ESM의 export/import 연결도 번들러가 호환 가능한 내부 모듈 형태로 변환한다.
- 최종 SSR 결과물에서는 문제가 된 `require('htmlparser2')`가 외부 ESM 패키지를 Node 모듈 로더로 불러오는 경계로 남지 않는다. 번들 내부 코드나 번들러가 만든 내부 참조를 사용하게 된다.
- 따라서 런타임 Node가 `node_modules/htmlparser2`를 CommonJS `require()`로 다시 해석할 기회가 없어지고, 이 경계에서 발생하던 `ERR_REQUIRE_ESM`도 피할 수 있다.

개념적으로는 다음과 같이 바뀐다.

```text
# 외부화된 경우
SSR 번들
  → require('sanitize-html')
    → node_modules/sanitize-html
      → require('htmlparser2')
        → node_modules/htmlparser2(ESM)에서 실패

# noExternal로 번들링한 경우
SSR 번들
  ├─ 변환된 sanitize-html 코드
  ├─ 변환된 htmlparser2 코드
  └─ 두 모듈을 잇는 번들 내부 참조
```

정확히 말하면 패키지 파일을 `index.js`에 “그대로 복사”하는 것은 아니다. Vite와 내부 번들러가 소스를 분석하고 변환·결합하며, 출력 분할 설정에 따라 하나 이상의 서버 청크가 만들어질 수도 있다. 또한 모든 `require()`가 반드시 사라진다고 보장할 수는 없다. 이번 해결의 핵심은 **문제가 된 `sanitize-html` → `htmlparser2` 연결이 런타임의 외부 `require(ESM)` 호출로 남지 않는 것**이다.

## 후속 장애: 로컬 dev에서 `require is not defined`

### 증상

첫 번째 장애를 해결한 뒤에는 반대로 배포 환경은 정상화됐지만, 로컬에서 `pnpm dev`로 실행한 `<문서 기능 페이지>`에서 다음 오류가 발생했다.

```text
ReferenceError: require is not defined
```

이 문제는 로컬 Vite 개발 서버에서만 재현됐다. 내부 기능명, 실제 라우트 경로와 환경 이름은 공개 가능한 형태로 일반화했다.

### 같은 `noExternal` 설정이 dev에서 다르게 동작한 이유

`ssr.noExternal`은 production 전용 옵션이 아니다. Vite 공식 문서에 따르면 별도 설명이 없는 SSR 옵션은 dev와 build에 모두 적용된다. 다만 production build와 dev 서버는 모듈을 처리하는 목적과 파이프라인이 다르다.

| 구분 | Production SSR build | Dev SSR 서버 |
|---|---|---|
| 목적 | 배포할 정적 결과물 생성 | 빠른 시작과 HMR 제공 |
| 처리 시점 | 빌드할 때 전체 모듈 그래프 처리 | 요청된 모듈을 필요할 때 처리 |
| 주요 처리 | Rollup 기반 번들링과 CommonJS 변환 | Vite 변환 파이프라인과 SSR 모듈 러너 평가 |
| `noExternal`의 효과 | 패키지를 외부화하지 않고 SSR 결과물에 번들링 | 패키지 로딩을 Node에 위임하지 않고 Vite가 직접 처리 |
| 산출물 | 하나 이상의 서버 번들·청크 | 개발 중 변환된 모듈과 최적화 캐시 |

Production에서는 `vite build`가 전체 모듈 그래프를 미리 순회한다.

```text
vite build
  → sanitize-html과 htmlparser2를 빌드 그래프에 포함
    → CommonJS·ESM 연결 변환
      → SSR 번들 또는 서버 청크 생성
        → 배포 런타임에서 완성된 결과물 실행
```

반면 dev 서버는 애플리케이션 전체를 production과 같은 방식으로 먼저 번들링하지 않는다. 페이지 요청에 필요한 모듈을 가져와 변환한 뒤 Vite 7의 SSR 호환 모듈 러너가 즉시 평가한다.

```text
pnpm dev
  → 페이지 요청
    → 필요한 SSR 모듈 탐색·변환
      → SSR 모듈 러너가 ESM 방식으로 평가
        → 화면 응답
```

`sanitize-html`을 `noExternal`로 지정하면 dev에서도 Node의 외부 패키지 로딩에 맡기지 않고 Vite가 직접 처리한다. 그런데 이 패키지가 dev 의존성 최적화를 거치지 않으면 진입 파일의 CommonJS 호출이 평가 가능한 ESM 형태로 충분히 변환되지 않은 채 남을 수 있다.

```js
const htmlparser = require('htmlparser2');
```

SSR 모듈 러너의 ESM 평가 컨텍스트에는 CommonJS 전역 함수인 `require`가 없다. 그 결과 첫 번째 장애와는 다른 `ReferenceError`가 발생했다. 기존에 다른 CommonJS UI 패키지에서도 같은 방식으로 발생할 수 있는 패턴이다.

### 후속 장애의 원인 흐름

```text
배포 장애 해결을 위해 sanitize-html을 noExternal로 지정
  → Production: Rollup이 CJS·ESM을 변환하여 정상 번들 생성
  → Dev: Vite가 패키지를 외부화하지 않고 직접 처리
    → 사전 번들링되지 않은 CommonJS require가 남음
      → ESM 컨텍스트에서 require 평가
        → require is not defined
```

즉, `noExternal` 자체가 잘못된 것은 아니다. 같은 옵션을 처리하는 **production 번들러와 dev 모듈 러너의 실행 방식 차이**가 후속 장애를 드러냈다.

### 후속 장애 해결: SSR dev 의존성 사전 번들링

SSR 개발 환경의 `optimizeDeps.include`에 `sanitize-html`을 추가한다.

```ts
export default defineConfig({
  environments: {
    ssr: {
      optimizeDeps: {
        include: ['sanitize-html'],
      },
    },
  },
});
```

Vite의 의존성 최적화기는 dev에서 패키지를 미리 번들링하고 CommonJS 코드를 ESM에서 소비할 수 있는 형태로 변환한다. 이후 SSR 모듈 러너는 `require()`가 남은 원본 CommonJS 진입 파일이 아니라 최적화된 결과를 평가한다.

```text
dev 서버 시작
  → sanitize-html을 의존성 최적화 대상으로 선택
    → esbuild가 CommonJS를 ESM 호환 형태로 사전 번들링
      → 최적화 캐시에 저장
        → 페이지 요청
          → SSR 모듈 러너가 최적화된 모듈 평가
            → 정상 렌더링
```

`htmlparser2`는 `sanitize-html`의 전이 의존성이므로 이 사전 번들링 과정에서 함께 추적된다. 현재 의존성 구조에서는 `optimizeDeps.include`에 별도로 등록하지 않아도 된다.

### 최종 설정과 역할 구분

두 설정은 중복이 아니라 서로 다른 실행 단계의 문제를 해결한다.

```ts
export default defineConfig({
  ssr: {
    noExternal: [
      'styled-components',
      'react-slick',
      'slick-carousel',
      'sanitize-html',
      'htmlparser2',
    ],
  },
  environments: {
    ssr: {
      optimizeDeps: {
        include: [
          'react-slick',
          'sanitize-html',
        ],
      },
    },
  },
});
```

| 설정 | 적용 목적 |
|---|---|
| `ssr.noExternal` | Production SSR 결과물에서 문제가 된 패키지가 외부 `require(ESM)` 경계로 남지 않게 한다. |
| `environments.ssr.optimizeDeps.include` | Dev SSR에서 CommonJS 패키지를 미리 ESM 호환 형태로 변환해 모듈 러너가 평가할 수 있게 한다. |

## 검증 방법

1. 설정 변경 후 `vite --force` 등으로 기존 의존성 최적화 캐시를 무시하고 dev 서버를 다시 시작한다.
2. 로컬 dev에서 대상 화면과 무관한 화면을 각각 열어 `require is not defined`가 사라졌는지 확인한다.
3. 배포와 동일한 Node 주 버전 및 실행 옵션으로 프로덕션 SSR 빌드를 실행한다.
4. 빌드 결과물에서 런타임 `require('htmlparser2')`가 외부 참조로 남아 있지 않은지 확인한다.
5. 로컬 프로덕션 서버에서 두 화면을 각각 새 프로세스의 첫 요청으로 호출한다.
6. 프리뷰 배포 후 콜드 스타트 로그에서 `ERR_REQUIRE_ESM`과 함수 초기화 오류가 사라졌는지 확인한다.
7. 대상 화면의 HTML 정제 결과가 기존 보안 정책과 일치하는지 회귀 테스트한다.

## 주의점과 대안

- `sanitize-html@2.18.1`은 패키지 메타데이터상 Node.js `>=22.12.0`을 요구한다. 번들링으로 당장의 로더 오류가 없어져도 배포 Node 버전이 이 요구사항보다 낮다면 공식 지원 범위 밖이므로 런타임 버전도 맞춰야 한다.
- Node.js 22.12.0 이상으로 올리는 방법도 있지만, 서버리스 환경이 `require(ESM)` 기능을 비활성화할 수 있다. 실제 `process.version`, `process.features.require_module`, 실행 플래그를 확인해야 한다.
- 과거 `sanitize-html` 버전으로 내리면 CJS 호환성은 돌아올 수 있지만, 이후 버전의 보안 수정도 함께 잃을 수 있다. 보안 검토 없이 단순 다운그레이드를 기본 해결책으로 삼지 않는다.
- `ssr.noExternal: true`는 해결 범위가 지나치게 넓다. 빌드 크기와 다른 Node 전용 패키지의 변환 위험을 늘릴 수 있으므로 필요한 패키지만 지정한다.
- `optimizeDeps`는 dev 의존성 최적화 설정이다. production의 외부화 문제를 대신 해결하지 않으므로 `ssr.noExternal`을 제거해서는 안 된다.
- 이 수정은 HTML 정제 정책 자체를 검증하지 않는다. 허용 태그·속성·URL 스킴에 대한 테스트는 별도로 유지해야 한다.

## 재발 방지 체크리스트

- 새 서버 의존성을 추가할 때 `type`, `main`, `exports`, `engines`를 확인한다.
- 직접 의존성뿐 아니라 잠금 파일의 전이 의존성 버전과 모듈 형식도 확인한다.
- SSR 프로덕션 결과물을 배포와 같은 Node 환경에서 실행하는 테스트를 CI에 둔다.
- `ssr.noExternal`에 CommonJS 패키지를 추가할 때 로컬 dev의 SSR 진입 경로도 함께 스모크 테스트한다.
- 서버 엔트리의 모듈 로드 실패를 잡을 수 있도록 콜드 스타트 스모크 테스트를 추가한다.
- 보안 패키지는 버전 고정이나 다운그레이드 전에 관련 보안 수정 이력을 확인한다.

## 참고 자료

- [Vite SSR 옵션: `ssr.external`과 `ssr.noExternal`](https://vite.dev/config/ssr-options.html)
- [Vite 의존성 최적화 옵션: `optimizeDeps.include`](https://vite.dev/config/dep-optimization-options.html)
- [Vite Environment API: 환경별 `optimizeDeps` 설정](https://vite.dev/guide/api-environment.html)
- [`sanitize-html@2.18.1` 패키지 메타데이터](https://github.com/apostrophecms/apostrophe/blob/sanitize-html%402.18.1/packages/sanitize-html/package.json)
- [`sanitize-html@2.18.1`의 CommonJS 진입 파일](https://github.com/apostrophecms/apostrophe/blob/sanitize-html%402.18.1/packages/sanitize-html/index.js)
- [`htmlparser2@12` 패키지 메타데이터](https://github.com/fb55/htmlparser2/blob/v12.0.0/package.json)
- [`sanitize-html` 변경 이력의 Node.js 및 ESM 호환성 설명](https://github.com/apostrophecms/apostrophe/blob/main/packages/sanitize-html/CHANGELOG.md)
- [Node.js 22.12.0의 `require(ESM)` 변경 사항](https://nodejs.org/en/blog/release/v22.12.0)

## 관련 문서

- [웹·모바일 프론트엔드 업무를 위한 핵심 개념](../frontend-web-mobile-core-concepts.md)
