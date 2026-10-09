"""하네스 엔지니어링 전용 코드베이스 색인 및 작업 메모리 생성기.

프로젝트 전역을 고속 스캔하여 Fast Lookup Map(빠른 조회 색인표)을 생성합니다.
매 프롬프트마다 전체 디렉터리를 반복 스캔(Full Scan)하는 비효율을 방지하고,
목적 파일로 0초 만에 직행할 수 있도록 구조화된 색인 데이터를 제공합니다.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 주요 파일별 설명 및 역할 메타데이터 (b5_2 Mini Git 전용)
FILE_METADATA = {
    "main.py": ("CLI 진입점", "main() 실행 및 Mini Git 대화형 REPL 구동"),
    "test_mini_git.py": ("전체 자체 검증 테스트", "8개 단위/통합 테스트 (DAG, 위상정렬, BFS 최단경로, 역색인, 병합정렬, REPL)"),
    "src/__init__.py": ("패키지 인터페이스", "핵심 심볼 일괄 익스포트 및 mini_git 호환성 제공"),
    "src/commit.py": ("커밋 노드 엔티티", "Commit (hash, message, author, timestamp, parents, order)"),
    "src/repo.py": ("저장소 상태 관리자", "Repository, RepoError (브랜치, HEAD, 커밋 해시맵, SHA-1 고유 발급)"),
    "src/graph.py": ("그래프 알고리즘 엔진", "topological_order(Kahn), shortest_path(무방향 BFS), ancestors(DFS)"),
    "src/index.py": ("역색인 검색 엔진", "InvertedIndex (소문자 토큰화 키워드 및 작성자별 O(1) 룩업)"),
    "src/sorting.py": ("안정 병합 정렬 엔진", "merge_sort (표준 API 대체 O(N log N) 분할 정복 정렬)"),
    "src/cli.py": ("CLI 컨트롤러", "dispatch, main (shlex 토큰화, 커맨드 라우팅, 에러 처리)"),
    "docs/b5_2_mission.pdf": ("미션 명세서 (원본 PDF)", "원본 보존 (절대 삭제 금지)"),
    "docs/b5_2_mission.md": ("미션 명세서 (MD 변환본)", "기본 명령어, DAG, 위상정렬, BFS, 역색인 요구사항 정의"),
    "docs/b5_2_mission_QA.md": ("미션 심층 질의응답서", "미션 목적, 8대 핵심 Q&A 및 상대 경로 코드 매핑"),
    "docs/b5_2_eval.pdf": ("구술/실기 평가표 (원본 PDF)", "원본 보존 (절대 삭제 금지)"),
    "docs/b5_2_eval.md": ("구술/실기 평가표 (MD 변환본)", "5대 평가 항목 체크리스트, 채점 기준표, PASS 평가"),
    "docs/b5_2_eval_QA.md": ("종합 평가문항 답변서", "5대 평가문항 심층 기술 답변 및 소스코드 1:1 매핑"),
    "docs/CONVENTIONS.md": ("커밋 및 코드 컨벤션", "Conventional Commits 규칙, 코드 스타일 정의"),
    "README.md": ("프로젝트 메인 안내서", "프로젝트 아키텍처, 실행 방법, 명령어 레퍼런스, 상호 링크 허브"),
    "READYOU.md": ("구술 평가 대비 상세 문서", "DAG 구조, 최단 경로, 위상 정렬, 역색인 핵심 원리 대본"),
    "study/README.md": ("프로젝트 종합 가이드", "개요, 상세, 구현 기능 목록, 폴더 트리, 단독 분리형 머메이드 실행도"),
    "study/study.md": ("핵심 개념 백과사전", "DAG, Kahn 위상정렬, BFS 최단경로, 역색인, 병합정렬, SHA-1 CS 총정리"),
    "study/mini_git_presentation.pptx": ("기술 발표 파워포인트", "12개 슬라이드 구성 16:9 와이드스크린 프리젠테이션 파일"),
    "study/presentation.html": ("인터랙티브 웹 슬라이드", "브라우저 전체화면 및 키보드 네비게이션 지원 단독 실행 슬라이드"),
    "study/generate_presentation.py": ("PPTX 자동 생성 스크립트", "python-pptx 기반 12슬라이드 자동 빌더"),
    "GEMINI.md": ("프로젝트 전역 규칙 파일", "7대 핵심 운영 규칙 (AGENTS.md와 100% 동기화)"),
    "AGENTS.md": ("프로젝트 전역 규칙 파일", "7대 핵심 운영 규칙 (GEMINI.md와 100% 동기화)"),
    "src/GEMINI.md": ("src 모듈 전용 규칙", "자료구조 제약, 시간 복잡도, 주석 보존 (AGENTS.md와 동기화)"),
    "src/AGENTS.md": ("src 모듈 전용 규칙", "자료구조 제약, 시간 복잡도, 주석 보존 (GEMINI.md와 동기화)"),
    "docs/GEMINI.md": ("docs 전용 규칙", "PDF 불변, 정합성, 컨벤션 준수 (AGENTS.md와 동기화)"),
    "docs/AGENTS.md": ("docs 전용 규칙", "PDF 불변, 정합성, 컨벤션 준수 (GEMINI.md와 동기화)"),
    "study/GEMINI.md": ("study 전용 규칙", "실구현 일치, 마크다운 표준, 상호 동기화 (AGENTS.md와 동기화)"),
    "study/AGENTS.md": ("study 전용 규칙", "실구현 일치, 마크다운 표준, 상호 동기화 (GEMINI.md와 동기화)"),
    "utils/validate_rules_sync.py": ("규칙 동기화 검증기", "GEMINI.md와 AGENTS.md 100% 일치 자동 검수/동기화"),
    "utils/validate_mermaid_syntax.py": ("Mermaid 문법 검증기", "엣지 라벨 괄호 등 파싱 에러 방지 자동 검사"),
    "utils/inspect_codebase_memory.py": ("하네스 색인 생성기", "Fast Lookup Map 생성 및 파일 트리 색인 자동화"),
    "utils/time_utils.py": ("시간 유틸리티", "KST 타임스탬프 생성 및 ISO 포맷 변환"),
    "utils/README.md": ("유틸리티 패키지 안내서", "재사용 툴 및 하네스 엔지니어링 스크립트 가이드"),
    "utils/scaffold_assignment_harness.py": ("하네스 스캐폴더", "새 과제 디렉터리에 듀얼 규칙, 하네스 도구, 표준 폴더, QA/학습 문서 일괄 구축"),
    "utils/GEMINI.md": ("utils 전용 규칙", "공통 툴 관리 및 듀얼 동기화 규칙 (AGENTS.md와 동기화)"),
    "utils/AGENTS.md": ("utils 전용 규칙", "공통 툴 관리 및 듀얼 동기화 규칙 (GEMINI.md와 동기화)"),
    "harness/README.md": ("하네스 턴키 안내서", "하네스 패키지 구성 명세 및 새 과제 이식 3단계 가이드"),
    "harness/setup_harness.py": ("하네스 자동 설치 러너", "새 과제 디렉터리에 하네스 전체 세트 1초 만에 자동 설치/검증"),
    "harness/PROMPT_TEMPLATE.md": ("프롬프트 템플릿 모음", "새 과제 시작 시 에이전트 전송용 원클릭 마스터 프롬프트"),
    "harness/GEMINI.md": ("harness 전용 규칙", "하네스 패키지 관리 및 듀얼 동기화 규칙 (AGENTS.md와 동기화)"),
    "harness/AGENTS.md": ("harness 전용 규칙", "하네스 패키지 관리 및 듀얼 동기화 규칙 (GEMINI.md와 동기화)"),
}


def generate_fast_lookup_table() -> str:
    """Fast Lookup Map 마크다운 테이블 문자열을 생성합니다."""
    lines = [
        "| 파일 경로 | 설명 | 주요 심볼 / 책임 |",
        "| :--- | :--- | :--- |",
    ]

    for rel_path, (desc, symbols) in sorted(FILE_METADATA.items()):
        full_path = PROJECT_ROOT / rel_path
        status = "✅" if full_path.exists() else "⚠️(미생성)"
        lines.append(f"| `{rel_path}` | {desc} {status} | {symbols} |")

    return "\n".join(lines)


if __name__ == "__main__":
    print("=== [Harness Engineering] Fast Lookup Map ===")
    print(generate_fast_lookup_table())
