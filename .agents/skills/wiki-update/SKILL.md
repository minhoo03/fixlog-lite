---
name: wiki-update
description: "Find and safely merge new information into an existing page in a user-configured wiki repository from any Codex project. Use when the user invokes $wiki-update, asks to revise, correct, consolidate, or refresh personal or team knowledge, or approves a proposed update to a relevant existing page."
---

# 위키 업데이트

## 승인 확인

- `$wiki-update`, "위키를 업데이트해", "/위키업데이트" 같은 명시적인 요청은 문서 수정과 집중된 Git 커밋에 대한 승인으로 간주한다. `/위키업데이트`는 자연어 별칭이며 공식 스킬 호출 문법은 `$wiki-update`이다. 사용자가 커밋 금지를 말하면 수정만 한다.
- 대화 중 갱신 필요성을 발견했을 뿐이면 대상 문서와 변경 요지를 먼저 제안하고 승인 전에는 수정하지 않는다.

## 위키 선택

1. `~/.config/llm-wiki/config.ini`를 읽는다. `LLM_WIKI_CONFIG` 환경 변수가 있으면 그 경로를 우선한다.
2. 사용자가 개인·팀 또는 저장소 이름을 지정했으면 해당 `repo:<name>` 섹션을 선택한다.
3. 지정이 없으면 `[llm-wiki]`의 `default` 저장소를 사용한다. 공개 범위가 달라질 수 있어 대상이 불명확하면 수정 전에 확인한다.
4. 설정된 절대 경로를 위키 루트로 사용하고 현재 작업 폴더를 위키로 추정하지 않는다.
5. 설정이나 경로가 없으면 수정하지 말고 `tools/llm_wiki.py install` 설정이 필요하다고 안내한다.

## 업데이트 절차

1. 선택한 위키 루트에서 `summary`, `aliases`, `tags`, 제목과 본문을 함께 검색해 가장 관련 있는 문서를 찾는다.
2. 후보가 여러 개이고 병합 대상에 따라 의미가 달라지면 사용자에게 짧게 확인한다.
3. 대상 문서 전체와 연결된 결정 또는 최근 로그를 읽어 기존 맥락을 보존한다.
4. 새 정보가 기존 내용과 충돌하면 최신이라고 임의 판단하지 말고 날짜와 근거를 비교한다. 해결되지 않으면 충돌을 문서에 명시하거나 사용자에게 확인한다.
5. 기존 `id`와 `created`를 유지하고 `updated`를 오늘 날짜로 바꾼다.
6. 본문뿐 아니라 `summary`, `aliases`, `tags`, `status`, `related`도 현재 내용에 맞게 갱신한다.
7. 중복 절을 합치고 이미 무효화된 정보는 삭제 이유나 대체 문서를 확인할 수 있게 정리한다.
8. 수정 후 문서 전체를 다시 읽어 새 정보가 자연스럽게 통합됐는지 검증한다.

## 로그와 결정

- `logs/`는 오탈자 수정이나 민감정보 제거 요청 외에는 덮어쓰지 않는다. 로그의 후속 내용은 새 로그로 작성하거나 `wiki/`의 정리된 문서에 반영한다.
- 기존 결정을 뒤집으면 예전 결정 파일을 삭제하지 않는다. 상태를 `superseded`로 바꾸고 새 결정 문서를 연결한다.

## Git 처리

- 사용자가 커밋하지 말라고 했거나 Git 저장소가 아니면 커밋하지 않는다.
- 그 외에는 `git -C <wiki-root>`를 사용해 이번에 수정한 관련 위키 파일만 스테이징하고 `docs(wiki): update <title>` 형식으로 한 번 커밋한다.
- 관련 없는 변경은 포함하지 않고 원격 푸시는 하지 않는다.
