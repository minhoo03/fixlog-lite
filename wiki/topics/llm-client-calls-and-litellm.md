---
id: topic-llm-client-calls-and-litellm
title: 클라이언트 LLM 호출 구조와 LiteLLM
summary: 브라우저에서 LLM 기능을 사용할 때 API 키를 노출하지 않도록 프록시를 두는 이유와 LiteLLM의 역할을 간단히 정리한다.
aliases:
  - 프론트엔드 LLM 호출
  - LLM 프록시
  - LiteLLM Gateway
tags:
  - llm
  - frontend
  - proxy
  - litellm
  - security
type: topic
status: active
created: 2026-10-12
updated: 2026-10-12
index: true
related: []
---

# 클라이언트 LLM 호출 구조와 LiteLLM

## 핵심 요약

- 서버 데이터를 사용하지 않더라도 일반 LLM API 키를 브라우저에 넣으면 안 된다.
- 보통 브라우저와 LLM 제공자 사이에 얇은 API 또는 LLM Gateway를 둔다.
- LiteLLM은 여러 LLM 제공자를 하나의 OpenAI 호환 API로 연결하고 키·비용·사용량을 중앙 관리하는 Gateway다.

## 일반적인 구조

```text
브라우저 → 앱 API 또는 Serverless Function → LLM 제공자
```

중간 프록시는 API 키 보관, 사용자 인증, 요청 제한, 비용 통제와 스트리밍 전달을 담당한다.

여러 모델을 함께 사용하거나 팀별 비용·모델 접근을 관리해야 한다면 다음처럼 LiteLLM을 둘 수 있다.

```text
브라우저 → 앱 API/LiteLLM → OpenAI·Anthropic·Gemini 등
```

LiteLLM의 virtual key도 브라우저에 장기간 노출하면 복사할 수 있다. 공개 서비스에서는 사용자 인증, 짧은 수명의 토큰 또는 별도의 앱 API가 추가로 필요하다.

예외적으로 Realtime API처럼 브라우저용 임시 토큰을 지원하는 서비스는 서버가 단기 토큰만 발급한 뒤 브라우저가 직접 연결할 수 있다. 작은 모델이라면 WebGPU를 사용해 브라우저 내부에서 실행하는 방법도 있다.

## 선택 기준

- 단일 LLM을 간단히 호출: 얇은 Serverless API
- 여러 제공자·모델·예산을 통합 관리: LiteLLM
- 실시간 음성 연결: 서버 발급 임시 토큰
- 외부 전송 없이 작은 모델 실행: 브라우저 로컬 추론

## 참고

- [OpenAI API 키 보안 지침](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety)
- [LiteLLM Gateway](https://docs.litellm.ai/docs/simple_proxy)
- [LiteLLM Virtual Keys](https://docs.litellm.ai/docs/proxy/virtual_keys)

## 관련 문서

- 없음
