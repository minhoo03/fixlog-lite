---
name: wiki-search
description: "Search user-configured personal or team Markdown wiki repositories from any Codex project and answer from the most relevant evidence with source links. Use when the user invokes $wiki-search, refers to past conversations or prior decisions, asks about a known project or domain, or when an accurate answer may depend on stored context outside the current repository."
---

# 위키 검색

읽기 전용으로 관련 문서를 찾고 원문을 확인한 뒤 근거와 함께 답한다. 검색 자체에는 사용자 확인을 요구하지 않는다.

## 위키 선택

1. `~/.config/llm-wiki/config.ini`를 읽는다. `LLM_WIKI_CONFIG` 환경 변수가 있으면 그 경로를 우선한다.
2. 사용자가 개인·팀 또는 저장소 이름을 지정했으면 해당 `repo:<name>`만 검색한다.
3. 지정이 없으면 `[llm-wiki]`의 `default` 저장소를 먼저 검색한다. 결과가 약하고 질문이 다른 프로젝트나 공유 지식을 암시하면 나머지 등록 저장소도 읽기 전용으로 검색한다.
4. 설정된 절대 경로를 사용하고 현재 작업 폴더를 위키로 추정하지 않는다.
5. 설정이나 경로가 없으면 위키를 검색했다고 주장하지 말고 `tools/llm_wiki.py install` 설정이 필요하다고 안내한다.

## 검색 절차

1. 질문에서 프로젝트명, 사람, 날짜, 결정, 핵심 개념과 가능한 동의어를 추출한다.
2. 선택한 저장소에 의미 기반 검색기나 `.wiki-cache/` 인덱스가 있으면 먼저 사용한다.
3. 인덱스가 없거나 결과가 약하면 다음을 함께 수행한다.
   - 파일명, 제목, `summary`, `aliases`, `tags` 키워드 검색
   - 질문을 다른 표현과 상위·하위 개념으로 바꾼 확장 검색
   - 관련 로그의 날짜와 연결 문서 검색
4. 경로와 메타데이터만으로 답하지 말고 상위 후보 3~5개의 관련 절과 필요한 전체 문서를 읽는다.
5. `wiki/`의 현재 문서, 승인된 결정, 최신 로그 순으로 신뢰하되 내용이 충돌하면 양쪽 근거와 날짜를 밝힌다.
6. 여러 위키가 연결돼 있으면 저장소별로 검색하고 개인·팀 등 출처 라벨을 유지한다.

## 답변 규칙

- 위키에 있는 사실과 모델의 일반 지식을 구분한다.
- 중요한 주장 뒤에 `저장소: 상대/경로.md#관련-제목` 형식의 출처를 붙인다.
- 문서에서 확인되지 않은 개인적 사실이나 결정을 추측하지 않는다.
- 결과가 없거나 관련도가 낮으면 "위키에서 확인되지 않음"이라고 말하고 필요한 추가 정보를 요청한다.
- 검색 중에는 문서, 인덱스와 Git 상태를 변경하지 않는다.

## 자동 실행 기준

- `$wiki-search`, "위키에서 찾아줘", "/위키검색"은 검색 요청으로 처리한다. `/위키검색`은 자연어 별칭이며 공식 스킬 호출 문법은 `$wiki-search`이다.
- "예전에", "지난번", "우리가 정한", "기존 기획", "왜 이렇게 결정했지" 같은 표현이 있으면 자동 실행한다.
- 특정 프로젝트나 도메인 질문에서 저장된 맥락이 답을 바꿀 수 있으면 자동 실행한다.
- 일반 상식, 단순 계산, 위키와 무관한 질문에는 실행하지 않는다.
