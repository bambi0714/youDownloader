# Repository & Agent Guidelines

이 문서는 이 저장소에서 작업하는 사람과 OpenAI Codex 에이전트가 따라야 할 공통 규칙입니다.

---

## Project Structure & Modules
- Core logic lives in `core/`; `downloader.py` integrates `yt_dlp` and ffmpeg paths.  
- UI components are in `ui/` (`browser.py`, `download_popup.py`, `progress_window.py`) and are launched by `main.py`.  
- Data models and option builders are in `models/` (e.g., `dataformat.py`, `download_options.py`).
- Conventions, docs for study sit in `docs/` and release notes sit in `CHANGELOG.md`.
- Temporary assets can go in `tmp.txt` or a dedicated `tmp/` folder if added.


## Setup, Build, Test, and Run
- Install dependencies: `python -m venv .venv && source .venv/bin/activate` (or `.\.venv\Scripts\activate` on Windows) then `pip install -r requirements.txt`.  
- Run the app locally: `python main.py` (opens the PySide6 GUI).  
- Optional build (PyInstaller, adjust paths as needed):  
  ```bash
  pyinstaller --onefile --windowed --add-binary "ffmpeg/ffmpeg.exe;ffmpeg" --name "YouTubeDownloader" main.py
  ```  
- No automated test suite exists yet; for smoke checks, launch the GUI and verify download, progress, and subtitle paths.

## Coding Style & Naming
- Python 3.x, 4-space indent, prefer type hints (`Optional` / `| None`, dataclasses), and f-strings for logging.  
- Keep functions short; move shared logic to `core/` and UI-specific code to `ui/`.  
- Use snake_case for variables/functions, PascalCase for classes, and keep module names lowercase.  
- If adding lint/format tools, prefer Black/Ruff defaults; commit their configs if introduced.

## Testing Guidelines
- When adding tests, place them under `tests/` mirroring module paths; name files `test_<module>.py` and functions `test_<behavior>()`.  
- Aim for coverage on downloader option building, ffmpeg path handling, and GUI signals that trigger downloads (can be headless via Qt test doubles).  
- Document any manual test steps in PRs until automated coverage is added.

## Commit & Pull Request Guidelines
- Use Conventional Commits (e.g., `feat: add subtitle-only mode`, `fix: handle invalid playlist url`). Use `feat!` for breaking changes.  
- Branch naming typically follows release matrix (see `doc/convention.md`):  
  - `dev/feature-*` → `feat:` PRs, `dev/fix-*` → `fix:` PRs; merge to `main` for releases.  
- Pull requests should include a short summary, before/after behavior, manual test notes, and screenshots/gifs of UI changes when applicable.  
- Link issues or todos, update `CHANGELOG.md` when release-relevant, and keep PRs small and focused.

## Communication & Language (for Codex and Contributors)
- 설명, 요약, 코드 리뷰 코멘트는 기본적으로 한국어로 작성해줘.
- 함수/변수/클래스 이름, 외부 라이브러리 이름은 영어를 그대로 사용합니다.
- 에러 메시지나 로그는 영어 또는 짧은 한국어 설명을 병기해도 된다.

## 7. Task Source: `docs/todo.md`
이 저장소에서의 “할 일” 기준(source of truth)은 `docs/todo.md`입니다.
### 7.1 구조 & 버전 관리
- 파일 위치 :`docs/todo.md`
- 버전 세션 형식:
    ```markdown
    ## v1.0.0 – MVP
    ...
    ---
    ## v1.1.0 – Playlist / UI / Installer
    ...
    ```
- TODO 항목은 체크박스 형식을 사용합니다:
    ```markdown
    - [ ] 할 일 설명
    - [x] 완료된 일 설명
    ```
- 필요 시 태그를 붙일 수 있습니다:
    ```markdown
    - [ ] [area: core] [prio: H] 플레이리스트 전체 다운로드 구현
    - [ ] [area: ui]   [prio: M] 모던한 디자인 리서치 및 적용
    - [ ] [area: build][prio: M] Inno Setup 기반 설치 프로그램 구성
    ```
  - `area` 예시: `core`, `ui`, `models`, `build`, `docs`
  - `prio` 예시: `H` (High), `M` (Medium), `L` (Low)

### 7.2 Codex가 `docs/todo.md`를 사용하는 방법
- 사용자가 다음과 같이 요청하면: `오늘 뭐 하면 좋을지 추천해줘`, `다음 버전 작업 골라줘` `XXX관련 작업부터 진행하자.`
- Codex는 다음 순서를 따릅니다:
  1. 먼저 `docs/todo.md`를 열어 내용과 버전별 TODO를 읽고, 전체 TODO 기반으로 프로젝트를 분석한다.
  2. 프로젝트를 분석한 결과 기반으로 작업한다.
  3. 가장 최신 버전(번호가 가장 큰 `vX.Y.Z`) 섹션을 우선으로 고려하고,
  4. 아직 완료되지 않은 항목(`- [ ]`) 중에서 요청한 조건에 맞는 작업을 고른다.(적절한 난이도의 작업을 추천한다.)
  5. 선택한 작업에 대해 2–3단계짜리 실행 계획을 먼저 제시한 뒤, 실제 코드 변경을 제안/수행한다.
- 체크박스 상태 변경에 대한 규칙:
  - Codex는 docs/todo.md에서 - [ ] → - [x] 변경을 바로 수행하지 않는다.
  - 먼저 “이 항목을 완료 처리해도 되는지”를 설명하고, 사용자의 승인을 받은 뒤에만 체크 상태를 변경한다.
  - 변경 시에는 diff를 함께 보여주는 것을 선호한다.


## 8. How Codex Should Work in This Repository

이 섹션은 OpenAI Codex 에이전트(또는 유사한 도구)를 위한 전용 규칙입니다.

### 8.1 General Behavior

- 큰 작업(새 기능 추가, 구조 리팩터링 등)을 할 때는:
  1. 먼저 **2–3단계짜리 계획(Plan)** 을 간단히 제시하고
  2. 그 다음에 코드를 수정합니다.
- 가능하면 변경 전/후 차이를 설명하고, 핵심 결정(설계 선택 등)에 대해 짧은 이유를 남깁니다.
- 코드/파일을 삭제하거나 대규모 리팩터링을 할 때는:
  - 먼저 변경 제안을 텍스트로 설명한 뒤,
  - 사용자의 승인을 받은 후 실제 변경을 수행합니다.

### 8.2 File & Command Safety

- 이 저장소에서는 **프로젝트 관련 파일**만 수정합니다.
- OS 설정, 전역 Python/패키지, 다른 드라이브의 파일은 건드리지 않습니다.
- 위험한 명령(`rm -rf`, 대규모 이동/삭제, 포맷 등)은 제안만 하고, 사용자에게 명확히 설명한 뒤 승인 없이는 실행하지 않습니다.

### 8.3 Testing & Verification

- 자동 테스트가 아직 부족하므로, 변경 후에는 항상 **수동 테스트 시나리오**를 함께 제안합니다.
  - 예: “단일 영상 다운로드”, “플레이리스트 전체 다운로드”, “잘못된 URL 입력 시 에러 처리” 등.
- 만약 `tests/` 디렉터리가 도입되면:
  - 변경과 연관된 최소한의 테스트를 함께 추가/수정하도록 시도합니다.

### 8.4 Style & Structure

- 새로운 모듈/파일을 추가할 때:
  - 공통 로직은 `core/`, 데이터/옵션 관련은 `models/`, 화면/이벤트는 `ui/`에 위치시키는 것을 우선 고려합니다.
- 이미 존재하는 스타일(네이밍, 인자 순서, 예외 처리 방식 등)을 최대한 따라갑니다.
- UI 변경 시, 가능하다면:
  - 코드 변경과 함께 PR 설명/수동 테스트 절차/스크린샷 텍스트를 어떻게 작성하면 좋을지도 함께 제안합니다.


## 9. Known Constraints & TODO Themes

- No full automated test suite yet.
- ffmpeg/yt_dlp 경로 및 OS별 차이 때문에, 빌드/배포 스크립트는 작업 전에 항상 사용자의 환경을 확인해야 합니다.
- 향후 대표적인 TODO 테마(세부 항목은 `docs/todo.md` 참조):

Codex는 위 제약을 고려하여:
- **환경을 파괴하지 않는 방향으로 변경을 제안**하고,
- 테스트/빌드 명령을 실행하기 전에 항상 계획과 예상 영향을 설명해주는 것을 목표로 합니다.