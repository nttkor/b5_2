"""Mini Git (b5_2) 기술 발표용 고품질 파워포인트 슬라이드(.pptx) 자동 생성기.

16:9 와이드스크린 규격과 세련된 Tech Dark 테마(#0D1117)를 적용하여,
12개 슬라이드로 구성된 고밀도 기술 프레젠테이션 파일을 생성합니다.
"""

from __future__ import annotations

from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# 1. 색상 팔레트 (GitHub/Codyssey Dark Tech Theme)
BG_COLOR = RGBColor(13, 17, 23)        # #0D1117 Dark Navy
CARD_BG = RGBColor(22, 27, 34)         # #161B22 Card Dark
CARD_BORDER = RGBColor(48, 54, 61)     # #30363D Border
TEXT_WHITE = RGBColor(240, 246, 252)   # #F0F6FC Primary Text
TEXT_MUTED = RGBColor(139, 148, 158)   # #8B949E Muted Text
ACCENT_BLUE = RGBColor(88, 166, 255)   # #58A6FF Cyan Blue
ACCENT_GREEN = RGBColor(63, 185, 80)   # #3FB950 Mint Green
ACCENT_ORANGE = RGBColor(240, 136, 62) # #F0883E Warm Orange
ACCENT_PURPLE = RGBColor(188, 140, 255)# #BC8CFF Violet


def create_base_presentation() -> Presentation:
    """16:9 와이드스크린 프레젠테이션 객체를 생성합니다."""
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    return prs


def add_background(slide, prs):
    """슬라이드 배경을 다크 테마 색상으로 칠합니다."""
    bg_shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height
    )
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = BG_COLOR
    bg_shape.line.fill.background()
    return bg_shape


def add_header(slide, title_text: str, category_text: str = "MINI GIT TECHNICAL DEFENSE"):
    """상단 헤더(카테고리 배지 + 슬라이드 제목)를 추가합니다."""
    # 카테고리 배지
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.35))
    tf_cat = cat_box.text_frame
    tf_cat.word_wrap = True
    p_cat = tf_cat.paragraphs[0]
    p_cat.text = f"● {category_text.upper()}"
    p_cat.font.size = Pt(11)
    p_cat.font.bold = True
    p_cat.font.color.rgb = ACCENT_BLUE

    # 슬라이드 타이틀
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.7), Inches(0.8))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = TEXT_WHITE


def add_card(slide, left: float, top: float, width: float, height: float, title: str, accent_color: RGBColor = ACCENT_BLUE):
    """카드 컨테이너 박스를 그리고 제목을 설정합니다."""
    # 배경 박스
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    card.fill.solid()
    card.fill.fore_color.rgb = CARD_BG
    card.line.color.rgb = CARD_BORDER
    card.line.width = Pt(1)

    # 카드 헤더 바
    top_bar = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left + 0.15), Inches(top + 0.15), Inches(width - 0.3), Inches(0.45))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = RGBColor(33, 38, 45)
    top_bar.line.fill.background()
    tf_bar = top_bar.text_frame
    tf_bar.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_bar = tf_bar.paragraphs[0]
    p_bar.text = title
    p_bar.font.size = Pt(13)
    p_bar.font.bold = True
    p_bar.font.color.rgb = accent_color

    # 본문용 텍스트박스 반환
    body_box = slide.shapes.add_textbox(Inches(left + 0.2), Inches(top + 0.7), Inches(width - 0.4), Inches(height - 0.85))
    tf_body = body_box.text_frame
    tf_body.word_wrap = True
    return tf_body


def append_bullet(text_frame, bold_prefix: str, content: str, pt_size: int = 12):
    """불릿 포인트를 추가합니다."""
    p = text_frame.add_paragraph()
    p.space_after = Pt(8)
    p.level = 0
    
    run_bullet = p.add_run()
    run_bullet.text = "▸ "
    run_bullet.font.bold = True
    run_bullet.font.size = Pt(pt_size)
    run_bullet.font.color.rgb = ACCENT_BLUE

    if bold_prefix:
        run_bold = p.add_run()
        run_bold.text = f"{bold_prefix}: "
        run_bold.font.bold = True
        run_bold.font.size = Pt(pt_size)
        run_bold.font.color.rgb = TEXT_WHITE

    run_text = p.add_run()
    run_text.text = content
    run_text.font.bold = False
    run_text.font.size = Pt(pt_size)
    run_text.font.color.rgb = TEXT_MUTED


def build_deck(output_path: Path):
    """12장 구성의 전체 파워포인트 슬라이드 덱을 빌드합니다."""
    prs = create_base_presentation()
    blank_layout = prs.slide_layouts[6]

    # ==========================================
    # SLIDE 1: 타이틀 표지 (Title Slide)
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    add_background(s1, prs)
    
    # 타이틀 박스
    tbox = s1.shapes.add_textbox(Inches(1.2), Inches(2.0), Inches(11.0), Inches(3.5))
    tf1 = tbox.text_frame
    tf1.word_wrap = True
    
    p0 = tf1.paragraphs[0]
    p0.text = "CODYSSEY AI/SW BASIC  |  DATA STRUCTURES & ALGORITHMS"
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = ACCENT_BLUE
    p0.space_after = Pt(16)

    p1 = tf1.add_paragraph()
    p1.text = "Mini Git — CLI 기반 커밋 그래프 엔진"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE
    p1.space_after = Pt(12)

    p2 = tf1.add_paragraph()
    p2.text = "외장 그래프 패키지 & 표준 정렬 API 없이 밑바닥부터 구현한 분산 버전 관리 시스템 코어"
    p2.font.size = Pt(16)
    p2.font.color.rgb = TEXT_MUTED
    p2.space_after = Pt(28)

    p3 = tf1.add_paragraph()
    p3.text = "발표자: 최성민  |  판정: PASS (8/8 Tests 100% Verified)  |  언어: Pure Python 3.10+"
    p3.font.size = Pt(13)
    p3.font.bold = True
    p3.font.color.rgb = ACCENT_GREEN

    # ==========================================
    # SLIDE 2: 핵심 과제 목표 및 엄격한 제약조건
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    add_background(s2, prs)
    add_header(s2, "01. 프로젝트 목표 & 엄격한 설계 제약사항 (Rules & Constraints)")

    c1 = add_card(s2, 0.8, 1.8, 5.6, 5.0, "🎯 미션 핵심 목표", ACCENT_BLUE)
    append_bullet(c1, "DVCS 코어 체득", "Git의 커밋 그래프 및 해시 무결성 원리를 밑바닥부터 구현")
    append_bullet(c1, "DAG 모델링", "커밋을 방향성 비순환 그래프 정점으로 구성하고 브랜치 포인터 관리")
    append_bullet(c1, "위상 정렬 LOG", "부모 커밋이 자식보다 항상 먼저 출력되는 인과율 보장 로그")
    append_bullet(c1, "무방향 최단 경로", "브랜치 간 최단 경로 탐색 및 사전순 타이브레이크 보장")
    append_bullet(c1, "역색인 검색 엔진", "단일 룩업 O(1) 키워드 및 작성자 검색 파이프라인 구축")

    c2 = add_card(s2, 6.8, 1.8, 5.6, 5.0, "🚫 엄격한 라이브러리 제약조건", ACCENT_ORANGE)
    append_bullet(c2, "그래프 패키지 금지", "NetworkX, igraph 등 외장 그래프 라이브러리 사용 전면 배제")
    append_bullet(c2, "표준 정렬 API 금지", "sorted(), list.sort() 등 Python 내장 정렬 API 일체 사용 금지")
    append_bullet(c2, "순수 자료구조 구현", "인접 리스트, BFS 큐, Kahn 위상 정렬, 분할 정복 병합 정렬 직접 코딩")
    append_bullet(c2, "인메모리 경량화", "네트워크/디스크 영속성 없이 메모리 상의 O(1) 해시맵 상태로 운영")
    append_bullet(c2, "보안 및 에러 표준", "shlex 파싱, 대소문자 무관, RepoError 도메인 예외 체계 확립")

    # ==========================================
    # SLIDE 3: 단일 책임 원칙(SRP) 기반 계층 아키텍처
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    add_background(s3, prs)
    add_header(s3, "02. 시스템 아키텍처 및 책임 분리 설계 (Architecture)")

    c3_1 = add_card(s3, 0.8, 1.8, 3.6, 5.0, "🖥️ Presentation (CLI)", ACCENT_BLUE)
    append_bullet(c3_1, "cli.py", "대화형 REPL 루프 및 입출력 정규화")
    append_bullet(c3_1, "shlex.split", "따옴표 포함 문자열 공백 안전 파싱")
    append_bullet(c3_1, "dispatch()", "명령어 대소문자 무관 라우팅")
    append_bullet(c3_1, "에러 표준화", "Invalid args, Unknown branch/commit")

    c3_2 = add_card(s3, 4.8, 1.8, 3.6, 5.0, "🏛️ State Engine (Domain)", ACCENT_GREEN)
    append_bullet(c3_2, "repo.py", "저장소 형상 상태 단일 진실 공급원")
    append_bullet(c3_2, "branches", "브랜치명 -> 최신 해시 가변 포인터 맵")
    append_bullet(c3_2, "current_branch", "HEAD 심볼릭 체크아웃 브랜치 관리")
    append_bullet(c3_2, "Commit Node", "6자리 해시, 부모 목록, 타임스탬프, order")

    c3_3 = add_card(s3, 8.8, 1.8, 3.6, 5.0, "⚡ Algorithms (Pure Engine)", ACCENT_PURPLE)
    append_bullet(c3_3, "graph.py", "topological_order, shortest_path, ancestors")
    append_bullet(c3_3, "sorting.py", "merge_sort (O(N log N) 안정 정렬)")
    append_bullet(c3_3, "index.py", "InvertedIndex (토큰 및 작성자 역색인)")
    append_bullet(c3_3, "무상태성", "알고리즘 함수는 순수 딕셔너리만 받아 재사용")

    # ==========================================
    # SLIDE 4: 커밋 그래프 위상 — 왜 DAG인가?
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    add_background(s4, prs)
    add_header(s4, "03. 커밋 그래프 자료구조 — 왜 DAG인가? (Directed Acyclic Graph)")

    c4_1 = add_card(s4, 0.8, 1.8, 5.6, 5.0, "⏳ 시간의 인과율과 비순환성 보장", ACCENT_BLUE)
    append_bullet(c4_1, "방향성 (Directed)", "간선은 항상 '자식 노드 -> 부모 노드' 방향으로 연결")
    append_bullet(c4_1, "인과성 (Causality)", "새 커밋 생성 시 부모는 이미 확정된 과거 노드만 지정 가능")
    append_bullet(c4_1, "미래 참조 불가", "미래 커밋은 해시조차 없으므로 부모로 참조 불가 -> 사이클 원천 차단")
    append_bullet(c4_1, "Commit.parents", "0개(루트), 1개(일반), 2개 이상(Merge) 부모 리스트 보유")
    append_bullet(c4_1, "단일 해시맵 O(1)", "Repository.commits[hash]로 임의 커밋 상수 시간 접근")

    c4_2 = add_card(s4, 6.8, 1.8, 5.6, 5.0, "⚠️ 사이클 발생 시 시스템 파멸적 영향", ACCENT_ORANGE)
    append_bullet(c4_2, "무한 루프 발생", "조상 탐색(DFS) 및 최단 경로(BFS) 순회 시 탈출 조건 붕괴")
    append_bullet(c4_2, "위상 정렬 불가능", "진입 차수가 0으로 떨어지지 않아 선후 관계 정의 불가")
    append_bullet(c4_2, "머지 베이스 붕괴", "공통 조상(LCA)을 특정할 수 없어 3-way 병합 불능 상태 초래")
    append_bullet(c4_2, "데이터 무결성", "해시 체인이 상호 참조를 일으켜 암호학적 머클 트리 성질 파괴")

    # ==========================================
    # SLIDE 5: Kahn 알고리즘 기반 부모 우선 LOG
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    add_background(s5, prs)
    add_header(s5, "04. 위상 정렬 LOG — 부모 커밋 선행 출력 알고리즘 (Kahn's Algorithm)")

    c5_1 = add_card(s5, 0.8, 1.8, 5.6, 5.0, "⚙️ Kahn 알고리즘 3단계 절차", ACCENT_GREEN)
    append_bullet(c5_1, "1단계: 진입차수 산출", "부모 -> 자식 간선에 대해 자식 노드의 indegree 계산")
    append_bullet(c5_1, "2단계: 큐 시딩", "부모가 없는 루트 커밋(indegree == 0)들을 큐에 등록")
    append_bullet(c5_1, "결정론적 순서", "동률 시 커밋 생성 순번(order) 기준 안정 정렬하여 시딩")
    append_bullet(c5_1, "3단계: 큐 소비 & 삭감", "큐에서 노드 u 추출 후 자식 v의 indegree를 1 감소")
    append_bullet(c5_1, "자식 큐 투입", "indegree[v]가 0이 되는 순간(모든 부모 처리 완료) 큐에 추가")

    c5_2 = add_card(s5, 6.8, 1.8, 5.6, 5.0, "📊 복잡도 분석 & 엔지니어링 의의", ACCENT_BLUE)
    append_bullet(c5_2, "시간 복잡도", "O(V + E) + O(V log V) — 정점 및 간선 1회 순회로 선형 수행")
    append_bullet(c5_2, "공간 복잡도", "O(V + E) — 인접 리스트 및 indegree 테이블 유지")
    append_bullet(c5_2, "단순 나열과의 차이", "자식이 부모보다 먼저 보이는 일반 최신순 로그의 직관성 한계 극복")
    append_bullet(c5_2, "외부 이력 대비", "생성 순서에 의존하지 않고 진짜 indegree를 추적하여 Replay에도 안전")

    # ==========================================
    # SLIDE 6: 무방향 BFS 최단 경로 (PATH)
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    add_background(s6, prs)
    add_header(s6, "05. 최단 경로 탐색 — 무방향 간선 모델링 & BFS (Shortest Path)")

    c6_1 = add_card(s6, 0.8, 1.8, 5.6, 5.0, "🔄 왜 간선을 무방향으로 간주하는가?", ACCENT_BLUE)
    append_bullet(c6_1, "형제 브랜치 분기", "feature와 main 브랜치 커밋은 공통 조상에서 갈라진 형제 관계")
    append_bullet(c6_1, "단방향 탐색의 한계", "자식 -> 부모만 허용 시 공통 조상 도달 후 다른 브랜치로 역주행 불가")
    append_bullet(c6_1, "양방향 간선 확장", "adjacency[p].append(c) & adjacency[c].append(p)로 그래프 구성")
    append_bullet(c6_1, "브랜치 횡단 경로", "login -> root -> payment 형태의 브랜치 간 실질 거리 측정 가능")

    c6_2 = add_card(s6, 6.8, 1.8, 5.6, 5.0, "🎯 BFS 거리 맵 계산 메커니즘", ACCENT_GREEN)
    append_bullet(c6_2, "비가중치 최단 경로", "모든 간선 가중치=1이므로 다익스트라 대신 BFS가 가장 최적")
    append_bullet(c6_2, "타깃 기점 탐색", "목적지(end)로부터 도달 가능한 모든 노드의 최단 홉 거리(dist_to_end) 계산")
    append_bullet(c6_2, "도달 불가 검증", "start 노드가 dist_to_end 맵에 없으면 즉시 'No path' 반환")
    append_bullet(c6_2, "시간/공간 복잡도", "O(V + E) 선형 시간에 그래프 전체 최단 거리 맵 확보")

    # ==========================================
    # SLIDE 7: 사전순 타이브레이크와 그리디 정당성
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    add_background(s7, prs)
    add_header(s7, "06. 결정론적 타이브레이크 — 사전순 최단 경로 그리디 증명 (Tie-breaking)")

    c7_1 = add_card(s7, 0.8, 1.8, 5.6, 5.0, "💎 다이아몬드 머지 경로 경쟁", ACCENT_PURPLE)
    append_bullet(c7_1, "동일 거리 경쟁", "a0 -> {b1, c1} -> d2 구조에서 a0->b1->d2와 a0->c1->d2는 둘 다 2홉")
    append_bullet(c7_1, "요구 규격", "경로를 'h1->h2->...' 문자열 결합 시 사전순(Lexicographical) 최솟값 선택")
    append_bullet(c7_1, "단순 접근의 비효율", "모든 최단 경로를 백트래킹으로 전수 탐색하여 정렬 시 O(K!) 폭발 위험")
    append_bullet(c7_1, "테스트 검증", "'b1' < 'c1'이므로 a0->b1->d2가 선택됨을 완벽 검증")

    c7_2 = add_card(s7, 6.8, 1.8, 5.6, 5.0, "📐 그리디 역추적 정당성 수학적 증명", ACCENT_GREEN)
    append_bullet(c7_2, "길이의 동일성", "모든 최단 경로는 홉 수(문자열 블록 수)가 D로 완전히 동일함")
    append_bullet(c7_2, "사전순 정의", "길이가 같은 문자열은 맨 처음 달라지는 원소의 크기에 의해 전체 순서 결정")
    append_bullet(c7_2, "탐욕적 선택 속성", "매 걸음마다 dist가 1 줄어드는 이웃 중 해시가 가장 작은 노드 선택")
    append_bullet(c7_2, "최적 부분 구조", "매 스텝의 국소 최적 선택(Local Optimum)이 전체 사전순 최소(Global Optimum)와 일치")
    append_bullet(c7_2, "복잡도 혁신", "경로 전수 열거 없이 O(V + E) 내에 최종 최단 경로를 직접 재구성")

    # ==========================================
    # SLIDE 8: 조상 탐색 (ANCESTORS)
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    add_background(s8, prs)
    add_header(s8, "07. 조상 커밋 추적 알고리즘 — DFS 순회 & 중복 방지 (Ancestors)")

    c8_1 = add_card(s8, 0.8, 1.8, 5.6, 5.0, "🔍 스택 기반 깊이 우선 탐색 (DFS)", ACCENT_BLUE)
    append_bullet(c8_1, "단방향 부모 추적", "시작 노드의 parents 리스트부터 스택에 투입하여 부모의 부모를 재귀 추적")
    append_bullet(c8_1, "자기 자신 제외", "시작 커밋 해시는 결과 집합에 포함하지 않고 순수 조상만 수집")
    append_bullet(c8_1, "미존재 커밋 방어", "저장소에 없는 해시 입력 시 None 반환 및 CLI에서 에러 처리")
    append_bullet(c8_1, "루트 커밋 질의", "부모가 없는 루트 커밋 질의 시 공집합(set()) 정확히 반환")

    c8_2 = add_card(s8, 6.8, 1.8, 5.6, 5.0, "🛡️ 다이아몬드 머지 중복 방문 차단", ACCENT_ORANGE)
    append_bullet(c8_2, "공통 조상 문제", "복수 브랜치가 병합된 경우 동일 조상이 여러 부모 경로를 통해 중복 노출")
    append_bullet(c8_2, "seen 집합 활용", "해시셋(seen: set[str])을 통해 이미 방문한 노드는 스택 확장 생략")
    append_bullet(c8_2, "시간 복잡도", "O(V_ancestors + E_ancestors) — 도달 가능한 부분 그래프 크기에만 비례")
    append_bullet(c8_2, "공간 복잡도", "O(V_ancestors) — 방문 해시셋 및 DFS 호출 스택 크기")

    # ==========================================
    # SLIDE 9: 역색인(Inverted Index) 검색 엔진
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    add_background(s9, prs)
    add_header(s9, "08. 역색인 검색 엔진 — O(1) 초고속 조회 아키텍처 (Inverted Index)")

    c9_1 = add_card(s9, 0.8, 1.8, 5.6, 5.0, "📖 역색인(Inverted Index) 구축 원리", ACCENT_GREEN)
    append_bullet(c9_1, "사전 색인화 (Pre-indexing)", "커밋 생성(Write-time) 시점에 텍스트를 파싱하여 색인 테이블에 등록")
    append_bullet(c9_1, "토큰화 & 소문자 정규화", "message.lower().split()으로 공백 분리 후 키워드 딕셔너리에 추가")
    append_bullet(c9_1, "2종 인덱스 지원", "by_keyword[token] -> [hashes], by_author[name] -> [hashes]")
    append_bullet(c9_1, "불변 리스트 반환", "외부 수정 오염 방지를 위해 조회 시 리스트 복사본 반환")

    c9_2 = add_card(s9, 6.8, 1.8, 5.6, 5.0, "⚡ 순회 검색 vs 역색인 성능 비교", ACCENT_BLUE)
    append_bullet(c9_2, "전체 순회 검색", "매 SEARCH 호출마다 전체 커밋 N개 메시지를 전수 스캔: O(N × L)")
    append_bullet(c9_2, "역색인 검색", "단 1회의 해시 테이블 룩업으로 매칭 해시 추출: 평균 O(1) + O(K)")
    append_bullet(c9_2, "대규모 환경 격차", "커밋 10만 건 환경에서 순회 검색 대비 수천 배 이상의 속도 향상")
    append_bullet(c9_2, "메모리-시간 트레이드오프", "약간의 메모리 인덱스 오버헤드로 읽기 성능을 극대화하는 표준 IR 기법")

    # ==========================================
    # SLIDE 10: 직접 구현한 병합 정렬 (Merge Sort)
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    add_background(s10, prs)
    add_header(s10, "09. 자체 구현 정렬 엔진 — 병합 정렬과 안정성 증명 (Merge Sort)")

    c10_1 = add_card(s10, 0.8, 1.8, 5.6, 5.0, "🔀 분할 정복 병합 정렬 메커니즘", ACCENT_PURPLE)
    append_bullet(c10_1, "제약 준수", "sorted(), list.sort()를 일체 배제하고 merge_sort() 직접 구현")
    append_bullet(c10_1, "재귀 분할 (Divide)", "배열을 중간 지점(mid = len // 2)에서 균등하게 절반 분할")
    append_bullet(c10_1, "결합 (Conquer & Merge)", "두 정렬 리스트의 선두 원소를 투 포인터(i, j)로 비교 병합")
    append_bullet(c10_1, "다양한 키 지원", "key=lambda c: c.timestamp, key=lambda c: c.author 유연한 정렬 지원")

    c10_2 = add_card(s10, 6.8, 1.8, 5.6, 5.0, "📐 복잡도 및 안정 정렬(Stability) 보장", ACCENT_GREEN)
    append_bullet(c10_2, "시간 복잡도 증명", "T(N) = 2T(N/2) + O(N) = O(N log N) (최선/평균/최악 동일)")
    append_bullet(c10_2, "퀵 정렬 대비 우위", "퀵 정렬의 피벗 불균형에 따른 최악 O(N^2) 성능 퇴화 위험 원천 제거")
    append_bullet(c10_2, "안정 정렬(Stable) 원리", "key(left[i]) <= key(right[j]) 비교 시 등호(<=)로 좌측 우선 채택")
    append_bullet(c10_2, "실무적 의미", "동일 작성자 정렬 시 최초 커밋 생성 순번(order)이 100% 보존됨")

    # ==========================================
    # SLIDE 11: 보안 엔지니어링 & 해시 충돌 방지
    # ==========================================
    s11 = prs.slides.add_slide(blank_layout)
    add_background(s11, prs)
    add_header(s11, "10. 시스템 신뢰성 & 보안 엔지니어링 (Security & Reliability)")

    c11_1 = add_card(s11, 0.8, 1.8, 5.6, 5.0, "🔒 6자리 SHA-1 해시 유일성 파이프라인", ACCENT_BLUE)
    append_bullet(c11_1, "해시 생성 포맷", "raw = f'{order}:{salt}:{message}:{timestamp}' 바이트 스트림 생성")
    append_bullet(c11_1, "생일 역설 공간 분석", "16^6 = 16,777,216 공간에서 k ≈ 4,818건 시 50% 확률로 충돌 가능")
    append_bullet(c11_1, "솔트(Salt) 재시도 루프", "충돌 감지 시 salt를 1 증가시켜 즉각 유일 해시 재발급 (중복 확률 0%)")
    append_bullet(c11_1, "테스트 재현성", "단조 카운터 기반으로 일관된 결정론적 테스트 재현성 보장")

    c11_2 = add_card(s11, 6.8, 1.8, 5.6, 5.0, "🛡️ 애플리케이션 레벨 보안 가드레일", ACCENT_ORANGE)
    append_bullet(c11_2, "인젝션 원천 차단", "shlex.split() 렉서 파싱 및 os.system 배제로 셸 메타문자 무력화")
    append_bullet(c11_2, "ReDoS 및 OOM 방어", "정규식 대신 split() 사용, 대용량 토큰 인덱싱 상한선 설계")
    append_bullet(c11_2, "민감정보 파라미터 은닉", "로그 출력 시 API Key, 토큰 마스킹(hide_parameters) 아키텍처 제시")
    append_bullet(c11_2, "도메인 예외 캡슐화", "비정상 조작 시 시스템 크래시 없이 표준 RepoError 메시지 반환")

    # ==========================================
    # SLIDE 12: 대규모 시스템 확장성 & 최종 결론
    # ==========================================
    s12 = prs.slides.add_slide(blank_layout)
    add_background(s12, prs)
    add_header(s12, "11. 대규모 확장성 로드맵 & 최종 평가 결론 (Scalability & Summary)")

    c12_1 = add_card(s12, 0.8, 1.8, 5.6, 5.0, "🚀 10만 건 커밋 대규모 확장 아키텍처", ACCENT_PURPLE)
    append_bullet(c12_1, "인접 리스트 상시 캐싱", "질의 시마다 즉석 생성하던 인접 리스트를 커밋 시점에 증분 캐싱")
    append_bullet(c12_1, "양방향 BFS 도입", "출발점과 도착점 동시 탐색으로 공간 복잡도 O(b^d) -> O(2·b^(d/2)) 축소")
    append_bullet(c12_1, "Commit-Graph 영속화", "실제 Git 2.18+ 규격처럼 바이너리 오프셋 테이블로 디스크 I/O 최적화")
    append_bullet(c12_1, "3-way Merge & Diff", "LCS 동적 계획법 Myers Diff 및 공통 조상(LCA) 기반 병합 확장 완비")

    c12_2 = add_card(s12, 6.8, 1.8, 5.6, 5.0, "🏆 최종 검증 결과 요약", ACCENT_GREEN)
    append_bullet(c12_2, "단위/통합 테스트", "test_mini_git.py 8개 테스트 스위트 100% PASS")
    append_bullet(c12_2, "규칙 동기화 검증", "GEMINI.md <-> AGENTS.md 6개 디렉터리 100% 동기화 PASS")
    append_bullet(c12_2, "다이어그램 문법", "36개 마크다운 내 Mermaid 다이어그램 100% PASS")
    append_bullet(c12_2, "구술 평가 판정", "PASS (경험정도: 능숙한 재구현 가능 / Level 5 확정)")

    # 프레젠테이션 파일 저장
    prs.save(str(output_path))
    print(f"✅ [SUCCESS] 파워포인트 슬라이드 파일 생성 완료: {output_path}")


if __name__ == "__main__":
    out_file = Path(__file__).resolve().parent / "mini_git_presentation.pptx"
    build_deck(out_file)
