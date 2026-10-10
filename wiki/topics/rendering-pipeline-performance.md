---
id: topic-rendering-pipeline-performance
title: 렌더링 파이프라인과 성능 병목 진단
summary: Style·Layout·Paint·Raster·Composite의 역할과 강제 동기 레이아웃·layout thrashing을 구분하고, 실제 모바일 WebView에서 성능 병목을 측정하고 개선하는 흐름을 정리한다.
aliases:
  - 브라우저 렌더링 파이프라인
  - 레이아웃 스래싱
  - 강제 동기 레이아웃
  - 웹뷰 스크롤 성능
tags:
  - 렌더링
  - 성능
  - 레이아웃
  - 웹뷰
  - 크로스 브라우징
type: topic
status: active
created: 2026-10-10
updated: 2026-10-10
index: true
related:
  - topic-event-loop-rendering-timing
  - topic-frontend-web-mobile-core-concepts
---

# 렌더링 파이프라인과 성능 병목 진단

**핵심: 화면이 느리면 먼저 비용이 큰 단계를 측정하고, 그 단계의 작업량을 줄인다.**

[이벤트 루프 문서](event-loop-rendering-timing.md)가 **화면을 갱신할 수 있는 시점**을 다뤘다면, 이 문서는 **갱신할 때 수행하는 작업과 비용**을 다룬다.

## 먼저 알아둘 개념

| 개념 | 필요한 만큼만 이해하기 |
|---|---|
| DOM·스타일 | DOM은 문서 구조이고, CSS는 표현 규칙이다. 브라우저는 둘을 바탕으로 요소의 스타일과 표시 정보를 계산한다. |
| 프레임 예산 | 60Hz 화면의 갱신 간격은 약 16.7ms, 120Hz는 약 8.3ms다. 이 시간 전체를 JavaScript만 쓸 수 있는 것은 아니다. |
| 무효화 | 변경 때문에 이전 계산 결과를 다시 계산해야 하는 상태. 영향을 받는 범위에 따라 비용이 달라진다. |
| 합성 레이어 | 일부 콘텐츠를 별도로 다뤄 합성할 수 있게 하는 단위. DOM 요소 하나마다 레이어 하나가 생기는 것은 아니다. |

## 화면이 만들어지는 흐름

**변경 → Style → Layout → Paint → Raster → Composite**

| 단계 | 수행하는 일 | 대표적인 비용 원인 |
|---|---|---|
| Style | 요소에 적용될 스타일을 계산한다. | 넓은 범위의 스타일 재계산 |
| Layout | 요소의 크기와 위치를 계산한다. | 많은 요소, 복잡한 배치, 반복 계산 |
| Paint | 배경·글자·테두리 등을 그릴 명령을 만든다. | 큰 변경 영역, 복잡한 시각 효과 |
| Raster | 그릴 명령을 실제 픽셀로 만든다. | 큰 이미지·레이어, 높은 해상도 |
| Composite | 준비된 레이어들을 배치해 최종 화면을 구성한다. | 과도한 레이어와 합성 부담 |

이는 이해를 위한 개념 모델이다. 브라우저는 변경에 필요한 단계만 수행할 수 있고, 모든 단계가 메인 스레드에서 실행되는 것도 아니다. [web.dev: Rendering performance](https://web.dev/articles/rendering-performance)

## 속성 변경에 따라 비용이 달라진다

- **`width`, `height` 등**: 배치가 달라지면 Layout 이후 작업이 필요할 수 있다.
- **`color`, `background-color` 등**: 보통 배치는 유지하면서 Paint 이후 작업이 필요하다.
- **`transform`, `opacity` 등**: 조건이 맞으면 기존 레이어를 이용해 Layout·Paint를 생략할 수 있다.

따라서 이동 애니메이션은 `left`보다 `transform`이 유리한 경우가 많다. 다만 **속성 이름만으로 합성만 수행된다고 보장할 수는 없다.** 실제 레이어와 실행 기록으로 확인한다. [web.dev: 렌더링 단계와 속성](https://web.dev/articles/rendering-performance)

## 강제 동기 레이아웃과 layout thrashing

브라우저는 보통 변경을 모아 계산한다. 그런데 배치 정보가 오래된 상태에서 `offsetWidth`처럼 최신 크기를 요청하면, 값을 반환하기 위해 **그 자리에서 Layout을 수행할 수 있다.** 이것이 강제 동기 레이아웃이다.

```js
// 쓰기와 읽기를 반복: 매번 최신 배치가 필요해질 수 있다.
for (const item of items) {
  item.style.width = '200px';
  console.log(item.offsetWidth);
}

// 쓰기를 모은 뒤 읽기: 반복 계산을 줄인다.
for (const item of items) item.style.width = '200px';
const widths = items.map((item) => item.offsetWidth);
```

두 번째 코드도 첫 읽기에서 Layout이 필요할 수 있다. 목적은 **계산을 없애는 것이 아니라 읽기·쓰기 교차로 인한 반복 계산을 줄이는 것**이다. 계산을 반복해서 강제하는 패턴을 layout thrashing이라 부른다. [web.dev: Layout thrashing](https://web.dev/articles/avoid-large-complex-layouts-and-layout-thrashing)

## 실무 사례: 모바일 WebView에서만 스크롤이 느리다

**1. 같은 조건으로 재현한다.**

실제 기기, OS·WebView 엔진 버전, 데이터 양, 화면 크기를 기록한다. 데스크톱 결과만으로 모바일 원인을 단정하지 않는다.

**2. 해당 환경의 Performance 기록을 잡는다.**

지원되는 원격 디버깅 도구로 버벅이는 구간을 기록한다. 프레임 누락과 함께 JS·Layout·Paint 등의 긴 구간을 찾아 관련 호출을 확인한다.

**3. 측정 결과에 맞춰 한 가지씩 바꾼다.**

| 발견한 병목 | 우선 검토할 개선 |
|---|---|
| 스크롤 핸들러의 JS가 길다 | 반복 연산 축소, 최신 값만 사용해 rAF에서 시각적 변경 묶기 |
| Layout이 반복된다 | 배치 읽기·쓰기 분리, DOM 규모 축소, 긴 목록 가상화 |
| Paint·Raster 비용이 크다 | 큰 변경 영역, 이미지 크기, 그림자·필터 등 효과 점검 |
| 레이어가 지나치게 많다 | 불필요한 레이어 승격과 `will-change` 축소 |

이 표는 진단을 시작하는 가설이다. 변경 전후 같은 구간을 다시 측정해 프레임 안정성과 상호작용 반응이 개선됐는지 확인한다. 웹 기록만으로 설명되지 않으면 호스트 앱과 기기 자원도 조사한다.

## 헷갈리기 쉬운 설명 바로잡기

| 흔한 설명 | 정확한 이해 |
|---|---|
| “크기를 읽으면 항상 reflow가 생긴다.” | 최신 배치 정보가 이미 있으면 재계산이 필요 없을 수 있다. |
| “강제 레이아웃 한 번도 layout thrashing이다.” | 강제 계산과 반복적으로 계산을 강제하는 패턴을 구분한다. |
| “rAF로 감싸면 layout thrashing이 사라진다.” | 콜백 안에서 쓰기·읽기를 반복하면 여전히 발생할 수 있다. |
| “`will-change`는 많이 붙일수록 빠르다.” | 준비 비용과 메모리 사용이 늘 수 있다. 필요한 곳에 제한해서 사용한다. |
| “GPU를 쓰면 무조건 빠르다.” | 레이어 생성·픽셀 처리·메모리 비용도 있다. 측정이 필요하다. |

## 스스로 검토할 꼬리질문

**Q. `transform`으로 이동하면 주변 요소도 자리를 비켜 주는가?**

A. 아니다. 시각적 위치는 바뀌지만 일반적인 문서 흐름에서 차지하는 배치 공간은 유지된다.

**Q. DOM 변경 횟수가 많으면 Layout 횟수도 반드시 같은가?**

A. 아니다. 브라우저가 여러 변경을 모아서 계산할 수 있다. 중간의 배치 정보 읽기가 이 묶음을 깨뜨릴 수 있다.

**Q. Chrome에서 빠르면 다른 브라우저와 WebView도 빠른가?**

A. 보장할 수 없다. 엔진·버전·기기 조건이 다르므로 실제 지원 환경에서 같은 시나리오를 검증한다.

**Q. 5년 차라면 무엇까지 설명할 수 있어야 하는가?**

A. “느리다”를 JS·Layout·Paint 등의 관측 결과로 좁히고, 변경이 그 비용을 왜 줄이는지 설명할 수 있어야 한다.

## 관련 문서

- [이벤트 루프와 브라우저 렌더링 타이밍](event-loop-rendering-timing.md)
- [웹·모바일 프론트엔드 업무를 위한 핵심 개념](frontend-web-mobile-core-concepts.md)
