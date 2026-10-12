---
id: topic-audio-duration-and-truncated
title: VBR 오디오 duration 오표시와 truncated 재생 UI 대응
summary: 전체 길이 정보가 불완전한 VBR 오디오의 duration을 브라우저가 잘못 추정하는 문제와, 서버 durationMs 및 truncated 여부에 따라 커스텀 재생 UI를 분리하는 해결책을 정리한다.
aliases:
  - 오디오 1분 47초가 7분으로 표시되는 문제
  - audio duration VBR 오류
  - truncated 오디오 플레이어
tags:
  - audio
  - vbr
  - duration
  - truncated
  - react
  - debugging
type: topic
status: active
created: 2026-10-12
updated: 2026-10-12
index: true
related: []
---

# VBR 오디오 duration 오표시와 truncated 재생 UI 대응

> 아래 컴포넌트 이름은 역할을 설명하기 위한 가칭이며, 프로젝트 규칙에 맞게 변경할 수 있다.

## 원인

`<audio controls>`가 사용하는 오디오 파일에 신뢰할 수 있는 전체 재생 시간 정보가 없다.

브라우저는 이런 경우 파일 초반 프레임에서 확인한 비트레이트와 파일 크기 등을 기준으로 `duration`을 추정할 수 있다. 해당 파일은 VBR(가변 비트레이트) 오디오이므로 초반 비트레이트와 실제 평균 비트레이트가 달랐고, 그 결과 실제 **1분 47초**인 녹음이 약 **7분**으로 표시됐다.

> 핵심: 오디오가 실제로 7분인 것이 아니라, 브라우저가 전체 길이를 잘못 추정한 것이다.

## 해결 방향

서버가 계산 가능한 경우 정확한 `durationMs`를 API로 내려준다. 프론트는 네이티브 `<audio controls>`를 사용하지 않고, `durationMs` 존재 여부에 따라 두 종류의 플레이어를 사용한다.

| 조건 | 서버의 `durationMs` | 프론트 UI |
|---|---:|---|
| `truncated = false` | 정확한 재생 시간 | `DurationAwareAudioPlayer` — API의 `durationMs`를 슬라이더 최댓값으로 사용하고 정확한 재생 위치와 총 길이를 표시한다. |
| `truncated = true` | `null` | `ElapsedOnlyAudioPlayer` — 슬라이더와 총 길이는 표시하지 않고, 재생·일시정지 버튼과 현재까지의 경과 시간만 표시한다. |

`truncated = true`인 녹음에는 footer가 없어서 `endedAt` 자체가 존재하지 않는다. 따라서 서버가 신뢰할 수 있는 전체 길이를 계산할 수 없으며 `durationMs`는 `null`로 반환한다.

> 핵심: `durationMs = null`은 길이가 0이라는 뜻이 아니라, 신뢰할 수 있는 전체 길이를 알 수 없다는 뜻이다.

## 프론트 분기

`AudioRecordingPlayback`은 `truncated`를 다시 해석하기보다 API의 최종 결과인 `durationMs` 존재 여부를 기준으로 분기한다.

```tsx
if (audioObjectUrl) {
  const hasKnownDuration = durationMs !== null;

  if (hasKnownDuration) {
    return (
      <DurationAwareAudioPlayer
        src={audioObjectUrl}
        durationMs={durationMs}
        onError={onPlaybackError}
      />
    );
  }

  return (
    <ElapsedOnlyAudioPlayer
      src={audioObjectUrl}
      onError={onPlaybackError}
    />
  );
}
```

> 핵심: API의 `durationMs`를 받아도 네이티브 `<audio controls>`의 `duration`을 덮어쓸 수는 없다. 정확한 슬라이더를 만들려면 커스텀 컨트롤이 필요하다.

## 필요한 변경 범위

1. **백엔드**
   - `AudioRecordingLog` 응답에 `durationMs: number | null`을 추가한다.
   - `truncated = false`이면 정확한 duration을 밀리초 단위로 반환한다.
   - `truncated = true`이면 `durationMs: null`을 반환한다.

2. **프론트 타입**
   - `types.ts`의 `AudioRecordingLog`에 다음 필드를 추가한다.

   ```ts
   durationMs: number | null;
   ```

3. **프론트 플레이어**
   - `AudioRecordingSection.tsx`에 다음 커스텀 플레이어를 추가한다.
     - `DurationAwareAudioPlayer`: 슬라이더, 현재 시간, 총 길이 표시
     - `ElapsedOnlyAudioPlayer`: 재생·일시정지와 경과 시간만 표시
   - `AudioRecordingPlayback`에서 `durationMs !== null`을 기준으로 두 플레이어를 분기한다.

## 최종 동작

- 정상 녹음은 서버 duration을 기준으로 정확한 재생바와 총 길이를 보여준다.
- truncated 녹음은 알 수 없는 총 길이를 추정하거나 잘못된 슬라이더를 보여주지 않는다.
- 두 경우 모두 브라우저가 잘못 계산한 네이티브 duration에 UI가 의존하지 않는다.

## 관련 문서

- 없음
