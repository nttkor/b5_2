# Commit & Code Conventions

본 문서는 프로젝트의 커밋 메시지 및 개발 표준 컨벤션을 정의합니다.

---

## 1. 커밋 메시지 컨벤션 (Commit Convention)

커밋 메시지는 `<type>: <description>` 형식을 엄격히 따릅니다.

### 타입 (Types)
- **feat**: 새로운 기능 추가 (예: `feat: add LRU cache eviction logic`)
- **fix**: 버그 수정 (예: `fix: resolve heapify index out of bounds error`)
- **docs**: 문서 수정 또는 추가 (예: `docs: update AGENTS.md rules`)
- **style**: 코드 포맷팅, 세미콜론 누락 등 로직 변경이 없는 수정 (예: `style: format imports and whitespace`)
- **refactor**: 코드 리팩토링 (기능 추가 또는 버그 수정 없음) (예: `refactor: extract helper in hashmap`)
- **test**: 테스트 코드 추가 또는 테스트 리팩토링 (예: `test: add unit test for single entry OOM`)
- **chore**: 빌드 업무, 패키지 매니저 설정, 기타 보조 작업 (예: `chore: update gitignore`)

### 작성 규칙
1. 제목은 50자 이내로 명확하고 간결하게 작성합니다.
2. 마침표(`.`)로 끝맺지 않습니다.
3. 본문이 필요한 경우 제목과 빈 줄 하나를 두고 작성합니다.

---

## 2. 코드 스타일 및 작성 컨벤션 (Coding Standard)

- **Python 버전**: Python 3.8+ (권장: Python 3.12)
- **자료구조 제약**: 내장 컬렉션(`dict`, `set`, `collections`) 사용 금지 (학습 및 미션 요구사항)
- **주석 및 docstring 가이드라인 (Google Style)**:
  - **기존 주석 및 로직 100% 보존**: 기존에 작성된 주석, docstring, 검증된 로직을 임의로 삭제하거나 축약하지 않습니다.
  - **모듈/클래스 docstring**: 역할, 아키텍처 상의 책임, 공간/시간 복잡도, 데이터 구조 불변성 원칙을 최상단에 명시합니다.
  - **함수/메서드 docstring**:
    1. 첫 줄: 함수의 핵심 동작을 간결하게 설명하는 한 줄 요약 (명령조/설명조 일관 유지).
    2. 본문(선택): 알고리즘 특성, 엣지 케이스 처리, 타이브레이크 의도, Doctest 예시.
    3. `Args`: 각 인자의 타입과 의미, 제약조건.
    4. `Returns`: 반환 값의 타입과 구조, 없을 시 None.
    5. `Raises`: 발생 가능한 예외(`RepoError`, `AttributeError` 등)와 발생 조건.
    6. `Complexity`: 시간/공간 복잡도 빅오(Big-O) 표기.
  - **내부 헬퍼/유틸리티 함수 주석**: 축약형 한 줄 주석에 그치지 않고 목적, 파라미터 가정, 호출처 책임을 표준 블록으로 일관성 있게 기술합니다.
- **보안**: CSRF, Argon2id, XSS, 민감정보 노출 방지(`hide_parameters`) 원칙 엄수
