---
id: topic-codex-llm-wiki-setup-and-operation
title: LLM Wiki를 Codex에 초기 설정하는 방법과 동작 원리
summary: LLM Wiki 저장소를 내려받은 뒤 설치 도구로 전역 스킬 링크와 위키 경로 설정을 만들고, Codex가 질문에 맞는 스킬을 선택해 설정된 Markdown 원문을 검색하는 전체 흐름을 설명한다.
aliases:
  - Codex 위키 처음 세팅
  - llm-wiki 설치 방법
  - wiki-search 동작 원리
  - 전역 위키 스킬 설정
tags:
  - codex
  - llm-wiki
  - setup
  - skills
  - wiki-search
  - configuration
type: topic
status: active
created: 2026-10-07
updated: 2026-10-07
index: true
related: []
---

# LLM Wiki를 Codex에 초기 설정하는 방법과 동작 원리

## 핵심 요약

- 저장소를 `git clone`하는 것만으로는 Codex 전역 위키 설정이 끝나지 않는다.
- 저장소에 포함된 `tools/llm_wiki.py install`을 한 번 실행해야 전역 스킬 링크와 위키 경로 설정이 만들어진다.
- Codex는 `~/.agents/skills/`에서 사용자 전역 스킬을 발견하고, 질문이 스킬 설명과 맞으면 해당 `SKILL.md`의 전체 절차를 읽어 실행한다.
- `~/.config/llm-wiki/config.ini`는 위키 이름을 실제 저장소 절대 경로와 연결하는 주소록이다.
- 위키 검색은 대화 내용을 영구 기억해서 답하는 기능이 아니라, 필요할 때 설정된 Markdown 저장소를 검색하고 원문을 확인해 답하는 방식이다.

## 구성 요소

### 위키 저장소

실제 지식이 저장되는 Git 저장소다. 주요 디렉터리와 파일은 다음과 같다.

- `wiki/topics/`: 재사용 가능한 지식과 개념
- `wiki/projects/`: 프로젝트의 현재 상태와 기획
- `wiki/decisions/`: 결정과 근거
- `logs/`: 날짜순 원본 기록
- `.agents/skills/`: 위키 검색·작성·업데이트 절차
- `AGENTS.md`: 저장소 안에서 지켜야 할 위키 운영 규칙
- `tools/llm_wiki.py`: 위키 등록과 스킬 설치 도구

### 사용자 전역 스킬 디렉터리

`~/.agents/skills/`는 어느 작업 폴더에서도 사용할 개인 스킬의 위치다. 설치 도구는 다음 세 디렉터리를 복사하지 않고 위키 저장소의 원본으로 연결하는 심볼릭 링크를 만든다.

- `wiki-search`
- `wiki-write`
- `wiki-update`

심볼릭 링크를 사용하므로 저장소에서 스킬 지침을 갱신하면 전역 위치에서도 같은 내용을 보게 된다.

### 위키 설정 파일

기본 위치는 `~/.config/llm-wiki/config.ini`다. `LLM_WIKI_CONFIG` 환경 변수가 있으면 그 경로를 대신 사용한다.

```ini
[llm-wiki]
default = personal

[repo:personal]
path = /absolute/path/to/personal-wiki
kind = personal
writable = true
```

이 파일은 다음 정보를 보관한다.

- 위키의 논리적인 이름
- 저장소의 절대 경로
- 개인·팀·템플릿 구분
- 쓰기 허용 여부
- 대상이 지정되지 않았을 때 사용할 기본 위키

## 최초 설치 절차

### 1. 저장소 내려받기

```bash
git clone <repository-url> <wiki-directory>
cd <wiki-directory>
```

### 2. Codex 전역 위키로 등록하기

```bash
python3 tools/llm_wiki.py install \
  --repo-root . \
  --name personal \
  --kind personal \
  --default
```

각 옵션의 의미는 다음과 같다.

- `--repo-root`: 등록할 위키 저장소 경로
- `--name`: `config.ini`에서 사용할 위키 이름
- `--kind`: `personal`, `team`, `template` 중 저장소 성격
- `--default`: 위키를 따로 지정하지 않았을 때 사용할 기본 저장소로 설정
- `--read-only`: `writable=false`로 등록
- `--replace-skills`: 이미 다른 저장소를 가리키는 전역 스킬 심볼릭 링크를 새 저장소 링크로 교체

설치 도구는 저장소 루트에 `AGENTS.md`가 있는지 확인한 뒤 다음 작업을 수행한다.

1. `config.ini`에 저장소 절대 경로와 속성을 기록한다.
2. 기본 위키가 없거나 `--default`가 지정되면 기본 위키 이름을 기록한다.
3. 저장소의 `.agents/skills/`를 가리키는 전역 심볼릭 링크를 `~/.agents/skills/`에 만든다.

### 3. 설치 상태 검사하기

```bash
python3 tools/llm_wiki.py doctor
```

검사는 기본 위키 설정, 등록된 저장소 경로, 세 전역 스킬의 `SKILL.md`가 모두 사용 가능한지 확인한다.

등록 상태를 따로 확인할 수도 있다.

```bash
python3 tools/llm_wiki.py list
python3 tools/llm_wiki.py resolve
```

### 4. Codex에 새 스킬 반영하기

Codex가 이미 실행 중이었다면 새 대화를 시작한다. 새 스킬이 나타나지 않으면 Codex를 다시 시작한다.

## 실행 시 동작 원리

전체 흐름은 다음과 같다.

```text
사용자 질문
  -> Codex가 사용 가능한 스킬의 이름과 설명을 확인
  -> 질문과 일치하는 wiki-search, wiki-write 또는 wiki-update 선택
  -> 선택한 스킬의 SKILL.md 전체 지침 읽기
  -> config.ini에서 대상 위키와 절대 경로 확인
  -> 설정된 저장소의 wiki/와 logs/ 검색
  -> 관련 후보의 원문을 직접 읽어 검증
  -> 출처 경로와 제목을 포함해 답변 또는 문서 변경
```

스킬은 지식 데이터베이스 자체가 아니라 작업 절차다. `SKILL.md`에는 언제 실행할지, 어떤 파일을 읽을지, 결과를 어떻게 검증하고 표시할지가 적혀 있다. 실제 지식은 위키 저장소의 Markdown 파일에 있다.

`wiki-search`는 “예전에 정리한 것”, “지난번 결정”, “기존 기획”처럼 저장된 맥락이 필요한 표현을 만나면 암묵적으로 선택될 수 있다. 명시적으로 `$wiki-search`를 호출할 수도 있다.

검색 시 의미 기반 인덱스나 `.wiki-cache/`가 있으면 우선 활용하고, 없거나 결과가 약하면 파일명·제목·요약·별칭·태그·본문의 키워드 검색과 확장 검색을 사용한다. 검색 결과의 경로나 점수만 믿지 않고 관련 원문을 다시 읽는 것이 핵심이다.

## `AGENTS.md`와 전역 스킬의 차이

- 저장소의 `AGENTS.md`는 해당 저장소 안에서 작업할 때 적용되는 운영 규칙이다.
- 저장소의 `.agents/skills/`는 저장소 내부에서 발견할 수 있는 구체적인 작업 절차다.
- `~/.agents/skills/`의 전역 링크는 다른 프로젝트에서 작업하더라도 위키 스킬을 사용할 수 있게 한다.
- `config.ini`는 전역 스킬이 실제로 검색하거나 수정할 위키 저장소를 찾게 해준다.

따라서 위키 저장소를 Codex의 현재 프로젝트로 열지 않아도, 전역 링크와 설정 파일이 정상이라면 어느 작업 폴더에서든 위키를 사용할 수 있다.

## 여러 위키를 등록할 때

추가 위키는 기본값을 바꾸지 않고 등록할 수 있다.

```bash
python3 tools/llm_wiki.py install \
  --repo-root /absolute/path/to/team-wiki \
  --name team \
  --kind team \
  --read-only
```

기본 위키는 별도로 바꾼다.

```bash
python3 tools/llm_wiki.py set-default personal
```

요청에서 “개인 위키”, “팀 위키” 또는 등록 이름을 지정하면 해당 저장소만 선택한다. 대상을 지정하지 않으면 `[llm-wiki]`의 `default`를 사용한다.

## 기존 스킬 링크 처리 시 주의점

전역 스킬 경로에 같은 이름의 심볼릭 링크가 이미 있으면 설치 도구는 기본적으로 기존 링크를 보존한다.

- 기존 링크가 같은 원본을 가리키면 `skill ok`로 처리한다.
- 다른 원본을 가리키면 `skill kept`로 처리하고 바꾸지 않는다.
- 실제 디렉터리가 이미 있으면 자동으로 덮어쓰지 않고 오류를 낸다.
- 다른 저장소의 스킬 링크로 교체하려면 내용을 확인한 뒤 `--replace-skills`를 사용한다.

```bash
python3 tools/llm_wiki.py install \
  --repo-root . \
  --name personal \
  --kind personal \
  --default \
  --replace-skills
```

`--replace-skills`는 심볼릭 링크만 교체하며, 일반 디렉터리를 강제로 삭제하지 않는다.

## 문제 해결 체크리스트

1. `config.ini`에 기본 위키와 저장소 절대 경로가 있는지 확인한다.
2. 저장소 경로가 실제로 존재하는지 확인한다.
3. `~/.agents/skills/wiki-search/SKILL.md` 등 세 스킬이 읽히는지 확인한다.
4. 전역 심볼릭 링크가 의도한 저장소를 가리키는지 확인한다.
5. `python3 tools/llm_wiki.py doctor`를 실행한다.
6. 새 대화를 시작하고, 필요하면 Codex를 다시 시작한다.
7. 검색 결과가 없으면 문서의 `title`, `summary`, `aliases`, `tags`와 본문 표현을 점검한다.

## 관련 문서

- [저장소 소개와 설치 명령](../../README.md)
- [의미 기반 검색 계약](../../SEARCH.md)
- [OpenAI 공식 Codex 스킬 문서](https://learn.chatgpt.com/docs/build-skills)
