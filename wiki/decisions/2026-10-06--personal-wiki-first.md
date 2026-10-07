---
id: decision-20261006-personal-wiki-first
title: 개인 위키 검증을 Discord 봇 운영보다 우선한다
summary: Codex에서 개인 위키의 검색·작성·업데이트 흐름을 먼저 검증하고, Gemini 기반 Discord 팀 위키 봇의 배포와 상시 운영은 이후로 보류한다.
aliases:
  - 개인 위키 우선 검증
  - Discord 봇 운영 보류
  - 팀 위키 봇 보류
tags:
  - llm-wiki
  - codex
  - discord
  - gemini
  - priority
type: decision
status: accepted
created: 2026-10-06
updated: 2026-10-06
index: true
related:
  - ./2026-10-06--semantic-search-rollout.md
---

# 개인 위키 검증을 Discord 봇 운영보다 우선한다

## 배경

개인 위키는 별도의 AI API 키 없이 사용자의 Codex가 Markdown 저장소를 직접 검색하고, 전역 위키 스킬을 통해 문서를 작성하거나 업데이트할 수 있도록 구성했다.

팀 위키용 `llm-wiki-discord-bot` 소스도 구현했으며, Discord에서는 Gemini API가 자연어 의도 판단, 의미 검색과 답변·문서 작성을 담당한다. 그러나 봇을 계속 사용하려면 Mac이나 외부 서버에서 프로세스를 상시 실행해야 하고, Discord 토큰·Gemini 키·Git 쓰기 권한과 배포 환경을 준비해야 한다.

## 결정

우선 개인 위키를 Codex에 연결해 다음 흐름을 실제로 검증한다.

- 어느 Codex 프로젝트에서든 등록된 개인 위키를 찾을 수 있는지 확인한다.
- 과거 내용과 특정 주제를 자연어로 검색해 근거 문서를 읽는지 확인한다.
- 대화 내용을 새 문서로 작성하고 적절한 폴더에 배치하는지 확인한다.
- 기존 문서를 안전하게 업데이트하고 관련 파일만 Git 커밋하는지 확인한다.

Gemini 기반 Discord 팀 위키 봇의 서버 추가, 키 설정, 상시 호스팅과 실제 운영 검증은 개인 위키 흐름이 확인될 때까지 보류한다.

## 근거

- 개인 위키는 추가 API 키나 별도 서버 없이 바로 검증할 수 있다.
- 위키 문서 구조와 작성·검색 규칙을 먼저 안정화하면 Discord 봇도 같은 저장소 계약을 재사용할 수 있다.
- 상시 호스팅과 팀 권한 문제를 뒤로 미뤄 현재 핵심인 Codex 장기 기억 보완 효과부터 확인할 수 있다.

## 영향

- 다음 작업은 개인 위키 저장소의 실제 사용 시나리오 검증이다.
- Discord 봇 소스는 유지하되 당분간 배포하거나 상시 실행하지 않는다.
- Discord 작업을 재개할 때는 봇 호스팅, Gemini 무료 티어의 데이터 정책, Git push 권한과 `AUTO_PUSH` 설정을 다시 검토한다.

## 관련 문서

- [의미 기반 검색 단계적 도입](./2026-10-06--semantic-search-rollout.md)
