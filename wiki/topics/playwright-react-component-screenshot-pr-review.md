---
id: topic-playwright-react-component-screenshot-pr-review
title: Playwright로 React 컴포넌트 스크린샷을 생성하고 PR에서 검토하기
summary: Playwright Component Testing으로 React 컴포넌트를 실제 브라우저에 렌더링하고 스크린샷을 생성·비교한 뒤, GitHub Actions와 GitHub CLI를 통해 PR 코멘트에서 검토하는 구조와 근거를 정리한다.
aliases:
  - React 컴포넌트 스크린샷 자동화
  - Playwright Component Testing 시각적 회귀 테스트
  - PR 코멘트 UI 리뷰
  - Playwright Visual Regression
tags:
  - playwright
  - react
  - component-testing
  - screenshot
  - visual-regression
  - github-actions
  - pull-request
type: topic
status: active
created: 2026-10-11
updated: 2026-10-11
index: true
related: []
---

# Playwright로 React 컴포넌트 스크린샷을 생성하고 PR에서 검토하기

## 핵심 요약

- Playwright는 실제 브라우저를 자동화하며, 화면 전체나 특정 요소의 스크린샷을 생성하고 기준 이미지와 비교할 수 있다.
- Component Testing은 전체 애플리케이션 대신 Button, Modal 같은 개별 컴포넌트와 특정 상태를 독립적으로 검증한다.
- 현재 Playwright는 `@playwright/test`의 Story Gallery와 `mount()` 방식을 권장한다. 과거의 `@playwright/experimental-ct-react` 방식은 새 구성에 사용하지 않는다.
- Playwright는 이미지를 만들고 비교할 뿐이다. 테스트 실행은 GitHub Actions가, PR 코멘트 작성과 이미지 첨부는 GitHub CLI 또는 API가 담당한다.
- 대표 이미지는 PR 코멘트에서 바로 보여주고, 전체 이미지·diff·로그·HTML Report는 Artifact로 분리하는 구성이 읽기 쉽다.

## 범위

이 문서는 특정 저장소에 종속되지 않은 일반적인 설계 원칙을 다룬다. `tada-web-monorepo`의 코드나 설정을 분석해 작성한 문서가 아니며, 실제 적용 시 해당 저장소의 패키지 매니저, 개발 서버, 컴포넌트 경로와 CI 정책에 맞춘 조정이 필요하다.

## 핵심 개념

### Playwright

Playwright는 Chromium, Firefox, WebKit 등의 실제 브라우저를 실행하고 페이지 이동, 입력, 클릭, 네트워크 제어와 화면 캡처를 자동화하는 테스트 도구다. 브라우저가 CSS와 폰트를 실제로 렌더링한 결과를 검사하므로 DOM 단위 테스트만으로 찾기 어려운 레이아웃 문제를 확인할 수 있다.

### Playwright Component Testing

Component Testing은 전체 서비스가 아니라 필요한 UI 상태만 브라우저에 렌더링한다. 현재 권장 모델에서는 `Primary`, `Disabled`, `Error`처럼 재현 가능한 상태를 Story로 정의하고, 프로젝트 개발 서버가 제공하는 Gallery 페이지에 `mount()`로 렌더링한다.

Story가 필요한 이유는 props, Provider, mock 데이터와 상태를 고정해 로컬과 CI에서 동일한 화면을 반복해서 만들기 위해서다. E2E 테스트보다 범위가 작아 빠르고 실패 원인을 찾기 쉽지만, 전체 사용자 흐름을 검증하는 E2E 테스트를 대체하지는 않는다.

### 스크린샷 생성과 비교

- `component.screenshot()`은 현재 화면을 이미지 파일로 저장한다. PR에 현재 UI를 보여주는 목적에 적합하다.
- `expect(component).toHaveScreenshot()`은 현재 화면을 저장된 기준 이미지와 비교한다. 의도하지 않은 시각적 변경을 검출하는 시각적 회귀 테스트다.

PR에서 현재 화면을 항상 보여주면서 회귀도 검출하려면 두 기능을 함께 사용한다. 기준 이미지는 CI가 자동 승인하게 두지 않고, 변경 의도를 사람이 확인한 뒤 코드와 함께 갱신하는 편이 안전하다.

## 자동화 흐름과 역할

```text
PR 생성·업데이트
→ GitHub Actions가 컴포넌트 테스트 실행
→ Playwright가 Story를 실제 브라우저에 렌더링
→ 현재 스크린샷 생성 및 기준 이미지 비교
→ 상세 결과를 Artifact로 보관
→ 대표 이미지를 PR 코멘트에 첨부
```

Playwright 자체에는 PR 코멘트를 작성하는 기능이 없다. GitHub CLI의 `gh pr comment --attach`를 사용하면 로컬 이미지를 GitHub에 업로드하고 코멘트 안에 표시할 수 있다.

Artifact는 전체 결과와 Playwright HTML Report를 보관하는 데 적합하다. 그러나 다운로드와 인증이 필요하고 보통 압축 파일로 제공되므로, Artifact 주소를 PR 코멘트의 인라인 이미지 주소처럼 사용하는 방식은 적합하지 않다.

## 실행 환경을 고정해야 하는 이유

같은 코드라도 운영체제, 브라우저 버전, 폰트, 화면 크기에 따라 픽셀이 달라질 수 있다. 이런 차이를 UI 오류로 잘못 판단하지 않으려면 다음 조건을 고정한다.

- Node.js, Playwright와 브라우저 버전
- viewport, device scale factor, locale, timezone과 color scheme
- 폰트와 이미지 로딩 조건
- 날짜, 랜덤 데이터와 API 응답
- 애니메이션과 caret 표시
- 기준 이미지 생성 환경과 CI 실행 환경

스크린샷 테스트만으로 기능적 정확성이나 접근성을 보장할 수는 없다. 클릭과 상태 변경을 확인하는 기능 테스트, role과 accessible name을 확인하는 접근성 기반 검사와 함께 사용해야 한다.

## PR 권한과 보안

같은 저장소의 브랜치에서 만든 PR은 `GITHUB_TOKEN`에 필요한 쓰기 권한을 부여해 코멘트를 작성할 수 있다. 외부 fork PR은 기본적으로 토큰이 읽기 전용으로 제한되어 이미지 첨부나 코멘트 작성이 실패할 수 있다.

이를 우회하려고 `pull_request_target`에서 외부 PR 코드를 체크아웃해 설치하거나 실행하면 안 된다. 이 이벤트는 높은 권한과 secrets에 접근할 수 있어 신뢰할 수 없는 코드가 토큰을 탈취할 위험이 있다.

외부 기여를 지원해야 한다면 읽기 전용 `pull_request` Workflow에서 테스트와 Artifact 생성을 수행하고, 별도의 신뢰된 Workflow가 결과를 데이터로만 읽어 코멘트를 작성하도록 분리한다. 높은 권한을 가진 단계에서는 PR의 스크립트나 실행 파일을 실행하지 않는다.

## 검토 기준

- 대표 상태만 PR 코멘트에 표시하고 전체 결과는 Artifact로 연결했는가?
- 컴포넌트의 루트 영역만 캡처해 Gallery의 테스트용 UI가 포함되지 않게 했는가?
- 기준 이미지와 CI가 동일한 환경에서 생성되는가?
- 날짜, 애니메이션, 네트워크 응답 같은 비결정적 요소를 고정했는가?
- 스크린샷 변경을 자동 승인하지 않고 사람이 의도를 확인하는가?
- fork PR에서 권한 상승 상태로 신뢰할 수 없는 코드를 실행하지 않는가?

## 참고 자료

- [Playwright Component Testing](https://playwright.dev/docs/test-components)
- [Playwright Visual Comparisons](https://playwright.dev/docs/test-snapshots)
- [GitHub CLI로 파일 첨부하기](https://docs.github.com/en/github-cli/github-cli/attaching-files-with-github-cli)
- [GitHub Actions Workflow 권한](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
- [pull_request_target 안전하게 사용하기](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target)

## 관련 문서

- 없음
