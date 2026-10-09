# src 모듈 전용 규칙 (Always-On Rules: GEMINI.md / AGENTS.md)

- **파일 위치**: `src/` 디렉터리 (`GEMINI.md`, `AGENTS.md`)
- **역할**: Mini Git 핵심 그래프 구조 및 알고리즘 엔진 구현을 위한 모듈 레벨 지침.

---

## 1. 핵심 제약 및 구현 원칙

### ① 외부 라이브러리 및 표준 정렬 API 절대 사용 금지
- NetworkX 등 외부 그래프 전용 패키지 사용을 엄격히 금지합니다.
- Python 내장 정렬 API인 `sorted()`, `list.sort()`의 사용을 일체 금지하며, 직접 구현한 `merge_sort`를 사용합니다.

### ② 시간 복잡도 및 아키텍처 준수
- **커밋 엔티티 (`commit.py`)**:
  - `Commit` 노드 구조 유지 (`hash`, `message`, `author`, `timestamp`, `parents`, `order`).
- **저장소 및 형상 관리 (`repo.py`)**:
  - `Repository` 클래스는 상태(커밋 딕셔너리, 브랜치 딕셔너리, HEAD)만 전담 관리.
  - 카운터 + 솔트 기반의 충돌 없는 6자리 SHA-1 고유 해시 발급 보장.
- **그래프 탐색 알고리즘 (`graph.py`)**:
  - `topological_order`: Kahn 알고리즘 기반 진입 차수(in-degree) 추적 위상 정렬 ($O(V+E)$).
  - `shortest_path`: 무방향 간선 BFS 최단 경로 ($O(V+E)$) 및 사전순 그리디 타이브레이크.
  - `ancestors`: 스택 기반 역방향 DFS 조상 탐색 ($O(V_{anc}+E_{anc})$).
- **역색인 검색 엔진 (`index.py`)**:
  - `InvertedIndex`: 커밋 메시지 소문자 토큰화 및 작성자별 사전 색인화로 $O(1)$ 해시맵 검색 달성.
- **안정 병합 정렬 (`sorting.py`)**:
  - `merge_sort`: 최선/평균/최악 $O(N \log N)$ 분할 정복 알고리즘 및 안정 정렬(Stability) 보장.
- **CLI 인터페이스 (`cli.py`)**:
  - `shlex` 기반 따옴표 인자 파싱, 대소문자 무관 커맨드 라우팅 및 표준 에러 메시지 준수.

### ③ 주석 및 코드 보존
- 기존 주석 및 설계 로직 100% 보존.
- 모든 함수와 클래스에 `Args`, `Returns`, `Raises`, `Complexity` 상세 docstring 유지.

### ④ 프롬프트 실행 완료 후 결과 및 검수/테스트 보고 (Mandatory)
- 프롬프트 실행 완료 후 소스 코드 변경 및 모듈 수정 내역을 상세히 보고한다.
- 작업 완료 즉시 자체 테스트 스위트(`python3 test_mini_git.py`) 검수를 수행하고 테스트 결과(통과/실패 내역)를 함께 보고한다.
- 보고 시 KST 로컬 시각 및 수정된 파일의 `file://` 마크다운 링크를 포함한다.

### ⑤ 상호 동기화 관리
- `src/GEMINI.md`와 `src/AGENTS.md`는 항상 100% 동일하게 유지합니다.
