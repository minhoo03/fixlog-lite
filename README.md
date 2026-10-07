# Fixlog Lite

개발 중 만난 문제와 해결 과정, 중요한 결정과 재사용 가능한 지식을 Codex와 함께 기록하고 검색하는 개인 Markdown 위키다. `llm-wiki-template`의 구조와 스킬을 기반으로 운영한다.

## 구조

```text
.
├── wiki/
│   ├── topics/       # 재사용 가능한 지식과 개념
│   ├── projects/     # 프로젝트별 현재 상태와 기획
│   └── decisions/    # 결정, 근거, 영향
├── logs/             # 날짜순 원본 기록; 원칙적으로 수정하지 않음
├── templates/        # 문서 작성용 Markdown 템플릿
├── .agents/skills/   # Codex용 작성·업데이트·검색 워크플로
├── tools/             # 전역 스킬 설치와 위키 경로 관리 도구
├── AGENTS.md         # 항상 적용할 위키 운영 규칙
└── SEARCH.md         # 의미 기반 검색 구현 계약
```

## 핵심 원칙

- `wiki/`는 현재 신뢰할 수 있는 정리된 지식이다.
- `logs/`는 당시의 맥락을 보존하는 추가 전용 기록이다.
- 문서는 가능한 한 하나의 주제만 다룬다.
- 제목뿐 아니라 `summary`, `aliases`, `tags`를 작성해 의미 기반 검색 품질을 높인다.
- 검색 답변에는 항상 근거 문서의 상대 경로와 제목을 표시한다.
- 임베딩과 검색 캐시는 `.wiki-cache/`에 만들고 Git에는 포함하지 않는다.

## Codex 전역 설정

위키 저장소를 Codex의 주 프로젝트로 열 필요는 없다. 저장소를 한 번 등록하면 어느 작업 폴더에서든 전역 스킬이 설정된 위키의 절대 경로를 찾아 사용한다.

```bash
python3 tools/llm_wiki.py install \
  --repo-root . \
  --name personal \
  --kind personal \
  --default

python3 tools/llm_wiki.py doctor
```

설치 도구는 다음 두 항목을 만든다.

- `~/.agents/skills/`: 이 저장소의 세 스킬을 가리키는 전역 심볼릭 링크
- `~/.config/llm-wiki/config.ini`: 개인·팀 위키의 이름, 절대 경로, 쓰기 권한

Codex가 이미 실행 중이었다면 새 대화를 시작하거나 앱을 다시 열어 새 스킬을 불러온다.

## Codex에서 사용

- `$wiki-write`: 대화나 메모를 새 문서 또는 로그로 정리
- `$wiki-update`: 기존 문서에 내용을 병합하고 변경을 커밋
- `$wiki-search`: 관련 문서를 찾아 출처와 함께 답변

`/위키작성`, `/위키업데이트`, `/위키검색`도 자연어 별칭으로 알아듣도록 설계했지만, Codex의 공식적인 명시 호출 문법은 `$스킬이름`이다. 명령을 직접 입력하지 않아도 Codex는 과거 결정이나 기존 지식을 묻는 질문이면 위키 검색 스킬을 선택할 수 있다. 대화 중 장기 보관 가치가 있는 내용이 나오면 저장 전에 사용자에게 제안한다.

여러 위키를 등록한 경우 질문이나 요청에서 `개인 위키`, `팀 위키`처럼 대상을 지정한다. 지정하지 않으면 기본 위키를 사용한다.

```bash
python3 tools/llm_wiki.py install \
  --repo-root /absolute/path/to/team-wiki \
  --name team \
  --kind team

python3 tools/llm_wiki.py list
python3 tools/llm_wiki.py set-default personal
```

## 새 위키 만들기

이 템플릿을 새 저장소로 복제한 뒤 저장소 이름과 원격 주소를 정하고 위 설치 명령으로 등록한다. 개인 위키와 팀 위키는 같은 구조를 사용하되 Git 권한과 검색 인덱스를 분리한다. 자동 푸시는 기본 동작에 포함하지 않는다.
