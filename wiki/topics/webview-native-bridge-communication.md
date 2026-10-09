---
id: topic-webview-native-bridge-communication
title: WebView와 네이티브 앱의 브리지 통신 설계
summary: WebView의 JavaScript와 Android·iOS 네이티브 앱이 통신하는 직접 브리지, 메시지, URL Scheme 방식을 구분하고 결합도·비동기 처리·플랫폼 호환성·보안·버전 관리에 따라 선택하는 기준을 정리한다.
aliases:
  - 웹뷰 네이티브 통신
  - WebView 브리지
  - JavaScript Bridge
  - postMessage와 직접 호출 비교
  - addJavascriptInterface
  - WKScriptMessageHandler
tags:
  - webview
  - native-bridge
  - javascript-bridge
  - postmessage
  - android
  - ios
  - hybrid-app
  - security
type: topic
status: active
created: 2026-10-08
updated: 2026-10-09
index: true
related:
  - topic-frontend-web-mobile-core-concepts
---

# WebView와 네이티브 앱의 브리지 통신 설계

## 핵심 요약

- WebView는 앱 안에서 HTML·CSS·JavaScript를 실행하는 브라우저 영역이며, JavaScript와 네이티브 앱은 서로 다른 실행 환경이다.
- 브리지 통신을 설계할 때는 `직접 호출 대 postMessage`만 비교하지 말고 웹에 보여줄 API, 실제 전송 방식, 웹과 앱 사이의 계약을 분리해서 봐야 한다.
- Android의 `addJavascriptInterface`처럼 네이티브 객체를 실제로 노출하는 직접 브리지는 단순하지만 플랫폼 의존성과 보안 제약이 있다.
- 메시지 방식은 요청·응답·오류·취소·타임아웃·버전을 설계해야 해서 초기 구현이 복잡하지만 플랫폼 통합과 독립 배포에 유리하다.
- 실무에서는 웹에 `App.pickPhoto()` 같은 Promise 기반 API를 제공하고 내부 전송은 origin이 제한된 메시지 채널로 구현하는 구조가 범용적이다.
- 외부 또는 신뢰할 수 없는 콘텐츠에는 방식과 관계없이 강력한 네이티브 기능을 노출하지 않는다.

## 범위

이 문서는 WebView 전체가 아니라 **WebView와 네이티브 앱 사이의 통신**을 다룬다. 쿠키·세션, 캐시, 뒤로 가기, 파일 다운로드, WebView 생명주기 전반과 같은 주제는 별도 범위다.

## 기본 구조

일반적인 네이티브 앱과 WebView는 서로 다른 기술로 실행된다.

```text
네이티브 앱
├── Android: Kotlin·Java
├── iOS: Swift·Objective-C
└── WebView: HTML·CSS·JavaScript
```

WebView의 JavaScript는 앱의 카메라, 사진첩, 진동, 네이티브 로그인 상태를 기본적으로 직접 사용할 수 없다. 이 경계를 연결하는 통로를 네이티브 브리지 또는 JavaScript 브리지라고 한다.

## 세 층으로 구분하기

브리지 설계는 다음 세 층으로 나누어 생각한다.

```text
1. 웹에 제공하는 API
   App.pickPhoto()

2. 실제 전송 방식
   직접 네이티브 브리지 또는 메시지 채널

3. 웹과 앱의 계약
   요청 이름, 파라미터, 버전, 성공·실패·취소 규칙
```

웹에서 직접 함수처럼 보이는 것과 실제 네이티브 직접 브리지는 같은 의미가 아니다.

```js
const photo = await App.pickPhoto();
```

위 코드는 내부적으로 다음 메시지를 보낼 수 있다.

```text
App.pickPhoto()
→ postMessage 요청
→ 네이티브가 사진첩 실행
→ 결과 메시지 반환
→ Promise 완료
```

## 방식 1: 네이티브 객체 직접 노출

Android의 대표적인 API는 `addJavascriptInterface`다.

```kotlin
webView.addJavascriptInterface(AppBridge(), "Native")
```

웹에서는 앱이 주입한 객체를 일반 JavaScript 객체처럼 호출한다.

```js
Native.close();
const version = Native.getAppVersion();
```

여기서 “함수를 웹에 노출한다”는 말은 인터넷 전체에 공개한다는 뜻이 아니다. 해당 WebView의 JavaScript 실행 환경에서 `Native.close()` 같은 네이티브 메서드를 호출할 수 있게 만든다는 뜻이다.

### 장점

- 호출 형태가 단순하다.
- 기능이 몇 개 없을 때 기반 코드가 적다.
- 단순 명령이나 작은 값 조회를 API처럼 사용할 수 있다.

### 제약

- 웹 코드가 네이티브 객체명, 메서드명과 파라미터에 직접 의존하기 쉽다.
- Android와 iOS의 기본 브리지 API가 서로 다르다.
- Android `addJavascriptInterface` 객체는 모든 프레임과 iframe에 노출된다.
- Android 앱에서는 어떤 프레임 origin이 메서드를 호출했는지 식별할 수 없다.
- Android 직접 브리지 호출은 WebView 전용 백그라운드 스레드에서 실행되므로 UI 작업에는 스레드 전환이 필요하다.

## 방식 2: 메시지 통신

웹은 네이티브 함수를 직접 호출하는 대신 요청 데이터를 보낸다.

```js
bridge.postMessage({
  version: 1,
  id: "req-42",
  method: "photo.pick",
  params: {
    source: "library"
  }
});
```

네이티브 앱은 메시지를 받아 검증한 뒤 해당 기능을 실행한다.

```text
메시지 수신
→ origin과 프레임 확인
→ 데이터 구조 확인
→ 허용된 method인지 확인
→ 사용자 권한 확인
→ 네이티브 기능 실행
→ 결과 반환
```

### 장점

- Android와 iOS에 같은 메시지 계약을 적용하기 쉽다.
- 네이티브 내부 클래스와 실제 함수 이름을 웹에서 숨길 수 있다.
- 요청 검증, 로깅, 버전 호환을 중앙 처리하기 쉽다.
- 로그인·결제·사진 선택처럼 비동기 결과가 복잡한 작업과 잘 맞는다.

### 초기 구현이 더 복잡한 이유

함수 호출처럼 신뢰할 수 있게 만들려면 다음 항목이 필요하다.

- 요청을 구분하는 ID
- 성공·실패·사용자 취소 응답
- 타임아웃
- 잘못된 데이터 검증
- 지원하지 않는 기능 처리
- 페이지 종료 또는 새로고침 시 요청 정리
- 구버전 앱과 최신 웹 사이의 호환
- 중복 요청과 재시도 정책

응답 예시는 다음과 같다.

```js
{
  version: 1,
  id: "req-42",
  status: "error",
  error: {
    code: "USER_CANCELLED"
  }
}
```

`postMessage`가 반드시 JSON 문자열이거나 단방향인 것은 아니다. JSON은 플랫폼 공통화, 로깅과 버전 관리가 쉬워 흔히 사용하는 계약 형식이다. Android 메시지 API는 문자열과 `ArrayBuffer`를 지원하며, iOS는 reply handler를 통해 JavaScript 호출에 응답할 수 있다.

## 방식 3: URL 이동 가로채기

웹이 특수 URL로 이동하면 앱이 이를 가로채 기능을 실행한다.

```js
location.href = "myapp://camera/open?direction=front";
```

이 방식은 딥링크, 네이티브 화면 열기, 오래된 WebView 호환처럼 단순한 작업에는 사용할 수 있다. 하지만 복잡한 payload, 응답, 실패·취소·타임아웃을 표현하기 어려워 일반적인 양방향 RPC에는 적합하지 않다.

## 결합도의 의미

결합도는 한쪽의 변경이 다른 쪽의 변경을 얼마나 요구하는지를 뜻한다.

직접 브리지의 예시는 다음과 같다.

```js
Native.openCamera("front");
```

웹은 `Native`, `openCamera`, 첫 번째 인자의 의미와 반환 형식을 알고 있다. 앱이 메서드를 `launchCamera({ direction: "front" })`로 바꾸면 웹도 함께 수정해야 한다.

메시지 방식도 계약에 의존하므로 결합이 사라지지는 않는다.

```js
{
  version: 1,
  method: "photo.capture",
  params: {
    direction: "front"
  }
}
```

차이는 앱 내부 함수가 바뀌어도 `photo.capture` 계약을 유지할 수 있다는 점이다. 결합도를 실제로 낮추는 것은 `postMessage` 자체가 아니라 안정적인 기능 이름, 버전 관리, 이전 버전 호환과 플랫폼 어댑터다.

## 크로스플랫폼의 의미

크로스플랫폼은 같은 웹 코드가 Android와 iOS에서 같은 API를 사용한다는 뜻이다.

```js
await App.pickPhoto();
```

실제 플랫폼 연결은 다를 수 있다.

```text
Android → WebMessageListener 또는 Android 브리지
iOS     → WKScriptMessageHandler
```

메시지 방식을 쓴다고 자동으로 크로스플랫폼이 되지는 않는다. 두 플랫폼이 같은 메서드명, 파라미터, 결과와 오류 코드를 구현해야 한다.

## 통제된 콘텐츠와 보안

통제된 콘텐츠는 단순히 회사 도메인이라는 뜻이 아니다. 다음을 함께 관리할 수 있어야 한다.

- 허용된 scheme과 host
- 외부 주소로의 이동
- iframe 출처
- 광고·분석 등 외부 JavaScript
- 사용자 입력으로 인한 XSS
- 로컬 파일 접근
- 서버와 CDN의 배포 및 침해 대응

직접 브리지와 메시지 브리지 모두 잘못 사용하면 위험하다. 메시지 방식도 모든 origin을 허용하거나 입력을 검증하지 않으면 안전하지 않다.

최소 보안 원칙은 다음과 같다.

- 로드 가능한 HTTPS origin을 허용 목록으로 제한한다.
- 메인 프레임과 iframe을 구분한다.
- 메시지 스키마와 값을 검증한다.
- 최소한의 기능만 노출한다.
- 권한이 필요한 작업은 현재 사용자 권한을 다시 확인한다.
- 인증 토큰 같은 민감정보를 불필요하게 웹에 반환하지 않는다.
- 외부 또는 신뢰하지 않는 페이지에는 권한 있는 브리지를 제공하지 않는다.
- 외부 콘텐츠는 가능한 경우 Custom Tab이나 시스템 브라우저로 연다.

## 비동기 작업과 운영 문제

사진 선택, 로그인과 결제는 결과가 즉시 나오지 않는다.

```text
요청
→ 네이티브 화면 또는 시스템 UI 표시
→ 사용자 선택·취소
→ 권한 오류 또는 성공
→ 나중에 결과 반환
```

페이지가 새로고침되거나 WebView가 닫히면 결과를 받을 JavaScript 환경이 사라질 수 있다. 따라서 페이지별 `sessionId`, 요청 취소, 브리지 준비 상태와 WebView 종료 처리가 필요하다.

웹은 서버에서 바로 업데이트되지만 네이티브 앱은 사용자가 업데이트하지 않을 수 있다. 최신 웹과 구버전 앱의 충돌을 막으려면 브리지 버전 또는 지원 기능을 확인한다.

```js
const capabilities = await App.getCapabilities();

if (capabilities.includes("photo.pick.v2")) {
  await App.pickPhoto();
} else {
  useFallback();
}
```

결제와 같이 되돌리기 어려운 작업은 타임아웃을 실패로 단정해서 자동 재시도하면 안 된다. 브리지 요청 ID와 별개로 서버가 인식하는 멱등성 키를 사용해야 한다.

## 상황별 선택 기준

| 상황 | 적합한 구조 | 근거 |
|---|---|---|
| 앱에 포함된 HTML, Android 전용, 단순 기능 2~3개 | 직접 브리지 가능 | 구조와 배포를 함께 통제하며 메시지 인프라의 비용이 더 클 수 있음 |
| 동일한 웹을 Android와 iOS에서 사용 | 공통 JS API와 메시지 브리지 | 플랫폼별 API 차이를 JS SDK 아래로 숨길 수 있음 |
| 결제·로그인·사진 선택 | Promise API와 요청·응답 메시지 | 성공·실패·취소·타임아웃 관리가 필요함 |
| 외부 뉴스·광고·제3자 페이지 | 권한 있는 브리지 미제공 | 콘텐츠와 실행 JavaScript를 신뢰할 수 없음 |
| 단순 네이티브 화면 이동 | URL Scheme 또는 메시지 | 복잡한 응답이 없다면 URL 이동 가로채기도 가능 |
| 웹과 앱의 배포 시점이 다름 | 버전이 있는 메시지 계약 | 구버전 앱 호환과 기능 탐지가 필요함 |

## 권장 구조

규모가 있는 하이브리드 앱에서는 다음 구조가 균형이 좋다.

```text
웹 비즈니스 코드
        ↓
App.pickPhoto() 같은 공통 JS SDK
        ↓
요청 ID·버전·타임아웃·오류 정규화
        ↓
origin이 제한된 메시지 채널
        ↓
Android·iOS 네이티브 요청 라우터
        ↓
허용된 기능 실행 및 표준 응답
```

웹 개발자는 다음과 같이 사용한다.

```js
try {
  const photo = await App.pickPhoto({ source: "library" });
} catch (error) {
  switch (error.code) {
    case "USER_CANCELLED":
      break;
    case "PERMISSION_DENIED":
      showPermissionGuide();
      break;
    case "UNSUPPORTED":
      useWebFallback();
      break;
  }
}
```

공통 오류는 `INVALID_ARGUMENT`, `UNSUPPORTED`, `PERMISSION_DENIED`, `USER_CANCELLED`, `TIMEOUT`, `NAVIGATION_ABORTED`, `INTERNAL_ERROR`처럼 플랫폼과 무관한 코드로 정규화한다.

## 면접 꼬리질문 점검

### 직접 브리지가 항상 나쁜가?

아니다. 완전히 통제된 콘텐츠, 소수의 단순 기능, 단일 플랫폼과 동시 배포 조건에서는 복잡한 메시지 계층보다 합리적일 수 있다.

### 메시지 방식은 항상 결합도가 낮은가?

아니다. 네이티브 구현 세부사항을 메시지 이름과 payload에 그대로 노출하면 여전히 강하게 결합된다. 안정적인 계약과 버전 관리가 핵심이다.

### 메시지 방식은 자동으로 안전한가?

아니다. origin, 프레임, 데이터와 권한을 검증하지 않으면 메시지도 공격 경로가 된다.

### 직접 호출은 항상 동기적인가?

아니다. 사진 선택과 결제처럼 원래 비동기인 작업은 직접 호출 형태라도 콜백, 이벤트 또는 Promise가 필요하다.

### 앱에서 웹으로도 요청할 수 있는가?

가능하다. Android의 `evaluateJavascript`, iOS의 `evaluateJavaScript` 또는 연결된 메시지 채널을 사용할 수 있다. 데이터를 JavaScript 문자열에 직접 이어 붙이지 않도록 주의한다.

### 고빈도 통신은 어떤 방식이 빠른가?

일반화할 수 없다. 직접 브리지와 메시지 모두 스레드 전환, 값 변환과 복사 비용이 있다. 고빈도 센서 데이터나 대용량 버퍼는 실제 기기에서 측정하며, 큰 버퍼를 한 번에 전달하지 않는다.

### 페이지 새로고침 중 응답이 오면 어떻게 하는가?

이전 세션의 요청으로 판단해 폐기하고, 기존 대기 Promise를 `NAVIGATION_ABORTED` 같은 오류로 종료한다.

### 구버전 앱이 새 메시지를 모르면 어떻게 하는가?

브리지 버전과 capabilities를 먼저 확인하고, 지원하지 않는 기능은 fallback하거나 명확한 `UNSUPPORTED` 오류를 반환한다.

### 타임아웃 요청은 재시도해도 되는가?

조회처럼 안전한 작업은 정책에 따라 가능하지만 결제·삭제 같은 작업은 결과 미확인 상태일 수 있으므로 멱등성 보장 없이 자동 재시도하지 않는다.

### 외부 페이지에도 읽기 전용 함수 정도는 제공해도 되는가?

반환값에 기기·사용자 식별 정보가 포함될 수 있고 이후 기능이 확장될 수 있으므로 기본적으로 제공하지 않는다. 꼭 필요하다면 최소 기능, 명확한 origin 제한과 별도의 위협 모델이 필요하다.

## 한 문장 정리

WebView 브리지에서 직접 호출은 작은 통제된 문제를 단순하게 해결하는 선택이고, 메시지 프로토콜은 플랫폼·버전·비동기 흐름이 복잡한 문제를 명시적인 계약으로 관리하는 선택이며, 실무에서는 직접 호출 형태의 Promise API를 메시지 채널 위에 제공하는 조합이 범용적이다.

## 참고 자료

- [Android WebView `addJavascriptInterface`](https://developer.android.com/reference/android/webkit/WebView#addJavascriptInterface(java.lang.Object,%20java.lang.String))
- [Android WebView 네이티브 브리지 보안](https://developer.android.com/privacy-and-security/risks/insecure-webview-native-bridges)
- [Android WebView 보안 권장사항](https://developer.android.com/privacy-and-security/security-best-practices#webview)
- [Android `WebViewCompat.addWebMessageListener`](https://developer.android.com/reference/androidx/webkit/WebViewCompat#addWebMessageListener(android.webkit.WebView,java.lang.String,java.util.Set,androidx.webkit.WebViewCompat.WebMessageListener))
- [Apple `WKScriptMessageHandler`](https://developer.apple.com/documentation/webkit/wkscriptmessagehandler)
- [Apple `WKScriptMessageHandlerWithReply`](https://developer.apple.com/documentation/webkit/wkscriptmessagehandlerwithreply)
- [Apple `WKContentWorld`](https://developer.apple.com/documentation/webkit/wkcontentworld)

## 관련 문서

- [웹·모바일 프론트엔드 업무를 위한 핵심 개념](frontend-web-mobile-core-concepts.md)
