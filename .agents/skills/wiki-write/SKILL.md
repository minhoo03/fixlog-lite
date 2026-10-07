---
name: wiki-write
description: "Create a durable Markdown page or append-only log in a user-configured wiki repository from any Codex project. Use when the user invokes $wiki-write, asks to save or document knowledge, or a conversation produces a reusable decision, plan, preference, or conclusion worth proposing for the personal or team wiki."
---

# 위키 작성

## 승인 확인

- 사용자가 `$wiki-write`, "위키에 저장해", "/위키작성"처럼 명시적으로 요청하면 작성 승인을 받은 것으로 간주한다. `/위키작성`은 자연어 별칭이며 공식 스킬 호출 문법은 `$wiki-write`이다.
- 대화 내용이 보존할 가치가 있어 이 스킬이 암묵적으로 선택됐다면, 대화를 방해하지 않는 마무리 시점에 저장을 한 번 제안하고 승인 전에는 파일을 수정하지 않는다.

## 위키 선택

1. `~/.config/llm-wiki/config.ini`를 읽는다. `LLM_WIKI_CONFIG` 환경 변수가 있으면 그 경로를 우선한다.
2. 사용자가 개인·팀 또는 저장소 이름을 지정했으면 해당 `repo:<name>` 섹션을 선택한다.
3. 지정이 없으면 `[llm-wiki]`의 `default` 저장소를 사용한다. 공개 범위가 달라질 수 있어 대상이 불명확하면 쓰기 전에 개인·팀 중 어디에 저장할지 묻는다.
4. 설정된 절대 경로를 위키 루트로 사용한다. 현재 작업 폴더를 위키로 추정하지 않는다.
5. 설정이나 경로가 없으면 파일을 만들지 말고 `tools/llm_wiki.py install` 설정이 필요하다고 안내한다.

## 작성 절차

1. 선택한 위키 루트의 `AGENTS.md`와 `templates/`를 읽는다.
2. 제목, 별칭, 태그와 핵심 개념으로 기존 문서를 먼저 검색한다.
3. 강하게 일치하는 기존 문서가 있으면 새 문서를 만들지 말고 `$wiki-update` 절차로 병합한다.
4. 새 문서라면 다음 기준으로 위치를 고른다.
   - 재사용 가능한 지식: `wiki/topics/<slug>.md`
   - 프로젝트 상태나 기획: `wiki/projects/<slug>.md`
   - 중요한 결정: `wiki/decisions/YYYY-MM-DD--<slug>.md`
   - 시간순 원본 기록: `logs/YYYY/MM/YYYY-MM-DD--<slug>.md`
5. 알맞은 템플릿을 사용하고 `summary`, `aliases`, `tags`를 본문과 같은 언어로 충실히 작성한다.
6. 하나의 중심 주제만 다루고, 사실과 해석을 구분하며, 관련 문서를 상대 링크로 연결한다.
7. 생성한 문서를 다시 읽어 메타데이터와 경로를 검증한다.

## 로그 규칙

- 로그는 당시 맥락을 보존하는 기록으로 작성하고, 이후 정정이나 결론은 새 로그 또는 정리된 위키 문서로 연결한다.
- 사소한 대화 전체를 저장하지 말고 핵심 맥락, 결과와 후속 행동만 남긴다.

## Git 처리

- 사용자가 커밋하지 말라고 했으면 커밋하지 않는다.
- 그 외에는 선택한 위키가 Git 저장소일 때 `git -C <wiki-root>`를 사용해 이번 작업에서 만든 관련 위키 파일만 스테이징하고 `docs(wiki): add <title>` 형식으로 한 번 커밋한다.
- 관련 없는 변경은 포함하지 않고 원격 푸시는 하지 않는다.
