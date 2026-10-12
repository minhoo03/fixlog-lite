---
id: topic-lucide-react-barrel-import-performance
title: lucide-react Barrel Import와 개발 성능
summary: lucide-react 루트의 Named Import가 큰 Barrel File을 거치면서 개발 서버 초기 구동과 HMR 비용을 높일 수 있는 이유를 정리한다.
aliases:
  - lucide-react named import 성능
  - lucide-react barrel file
  - lucide-react HMR 지연
tags:
  - lucide-react
  - barrel-file
  - import
  - hmr
  - performance
  - debugging
type: topic
status: active
created: 2026-10-12
updated: 2026-10-12
index: true
related: []
---

# lucide-react Barrel Import와 개발 성능

## 핵심 요약

PERF §2.1에서는 `lucide-react`를 모든 아이콘을 다시 내보내는 진입점(Barrel Entry)을 가진 라이브러리로 분류한다.

```ts
import { Search, Settings } from 'lucide-react';
```

루트 경로의 Named Import를 사용하면 개발 도구가 큰 Barrel File의 export 목록을 분석해야 할 수 있다. 이 비용은 개발 서버의 초기 구동과 HMR 속도에 영향을 줄 수 있다.

> 핵심: 실제로 사용하는 아이콘은 일부여도, 개발 과정에서는 어떤 export를 사용하는지 확인하기 위해 큰 진입점을 먼저 처리할 수 있다.

프로덕션 빌드에서는 tree shaking으로 사용하지 않는 아이콘이 제거될 수 있으므로, 이 문제를 곧바로 “전체 아이콘이 최종 번들에 포함된다”는 뜻으로 해석하면 안 된다. 핵심은 주로 **개발 시 모듈 분석 비용**이다.

개선 방법은 사용하는 프레임워크와 번들러에 따라 다음 중 하나를 선택한다.

- 패키지 import 최적화 기능 사용
- 라이브러리가 공식 지원하는 아이콘별 직접 import 사용
- 변경 전후의 초기 구동 시간과 HMR 시간을 실제 측정

## 관련 문서

- 없음
