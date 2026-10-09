"""Assert-based self-check test suite.

Run:
    python3 test_mini_git.py

이 테스트 스크립트는 Mini Git의 핵심 기능(병합 정렬, 커밋 그래프, 위상 정렬,
BFS 최단 경로, 사전순 타이브레이크, 조상 탐색, 역색인 검색, CLI 디스패치 및 에러 처리)을
전수 자동 검증합니다.
"""

from __future__ import annotations

import sys
from pathlib import Path

# 루트 디렉터리 경로 등록 및 mini_git 패키지 별칭 등록 (호환성 보장)
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import src as mini_git  # noqa: E402
sys.modules["mini_git"] = mini_git

from src.commit import Commit  # noqa: E402
from src.graph import ancestors, shortest_path, topological_order  # noqa: E402
from src.repo import RepoError, Repository  # noqa: E402
from src.sorting import merge_sort  # noqa: E402
from src.cli import dispatch  # noqa: E402


def test_merge_sort_is_correct_and_stable() -> None:
    """병합 정렬의 정확성 및 안정 정렬(Stable Sort) 속성을 검증합니다."""
    items = [(3, "a"), (1, "x"), (1, "y"), (2, "b"), (1, "z")]
    result = merge_sort(items, key=lambda t: t[0])
    assert [t[0] for t in result] == [1, 1, 1, 2, 3]
    # stability: the three key==1 items must keep their original order
    assert [t[1] for t in result if t[0] == 1] == ["x", "y", "z"]


def test_repo_flow_and_log_order() -> tuple[Repository, Commit, Commit, Commit]:
    """저장소 초기화, 브랜치 분기, 커밋 생성 및 위상 정렬 기본 순서를 검증합니다."""
    repo = Repository()
    repo.init("Alice")
    root = repo.commit("Initial commit")

    repo.branch("feature")
    repo.switch("feature")
    login = repo.commit("Add login feature")

    repo.switch("main")
    payment = repo.commit("Add payment feature")

    assert repo.branches["main"] == payment.hash
    assert repo.branches["feature"] == login.hash
    assert login.parents == [root.hash]
    assert payment.parents == [root.hash]

    # parents-before-children topological order; ties broken by creation order
    order = topological_order(repo.commits)
    assert order == [root.hash, login.hash, payment.hash]

    # single author -> stable sort keeps creation order
    by_author = merge_sort(list(repo.commits.values()), key=lambda c: c.author)
    assert [c.hash for c in by_author] == [root.hash, login.hash, payment.hash]

    return repo, root, login, payment


def test_path_and_ancestors(
    repo: Repository, root: Commit, login: Commit, payment: Commit
) -> None:
    """무방향 간선 기반 최단 경로 및 조상 커밋 추적 기능을 검증합니다."""
    # only path from login to payment goes through root (tree, no merges yet)
    path = shortest_path(repo.commits, login.hash, payment.hash)
    assert path == [login.hash, root.hash, payment.hash]

    assert shortest_path(repo.commits, root.hash, root.hash) == [root.hash]
    assert shortest_path(repo.commits, "nope", root.hash) is None

    assert ancestors(repo.commits, payment.hash) == {root.hash}
    assert ancestors(repo.commits, root.hash) == set()


def test_search_uses_inverted_index(
    repo: Repository, root: Commit, login: Commit, payment: Commit
) -> None:
    """역색인을 통한 키워드 및 작성자 검색 정확성을 검증합니다."""
    assert repo.index.search_keyword("login") == [login.hash]
    assert repo.index.search_keyword("nonexistent") == []
    assert repo.index.search_author("Alice") == [root.hash, login.hash, payment.hash]


def test_shortest_path_lexicographic_tiebreak() -> None:
    """최단 거리가 동일한 복수 경로 중 사전순 타이브레이크 규칙을 검증합니다."""
    # Diamond: a0 -> {b1, c1} -> d2 (two equal-length paths a0->b1->d2 and
    # a0->c1->d2). "b1" < "c1", so a0->b1->d2 must win.
    a0 = Commit("a0", "root", "Alice", "t0", [], 0)
    b1 = Commit("b1", "left", "Alice", "t1", ["a0"], 1)
    c1 = Commit("c1", "right", "Alice", "t2", ["a0"], 2)
    d2 = Commit("d2", "merge", "Alice", "t3", ["b1", "c1"], 3)
    commits = {c.hash: c for c in (a0, b1, c1, d2)}

    assert shortest_path(commits, "a0", "d2") == ["a0", "b1", "d2"]


def test_unique_hash_on_identical_inputs() -> None:
    """동일한 메시지와 시간에도 해시 유일성이 보장되는지 검증합니다."""
    repo = Repository()
    repo.init("Bob")
    first = repo.commit("same message")
    second = repo.commit("same message")
    assert first.hash != second.hash


def test_error_handling_and_cli_dispatch() -> None:
    """CLI 디스패치 및 에러 처리 표준(대소문자 무관, 미초기화, 미식별 인자)을 검증합니다."""
    repo = Repository()

    # 미초기화 상태 접근 시 에러 검증
    try:
        repo.commit("should fail")
        assert False, "RepoError expected"
    except RepoError as e:
        assert "Repository not initialized" in str(e)

    # CLI 대소문자 무시 INIT 실행
    out = dispatch(repo, ["init", "Alice"])
    assert "Initialized repository." in out
    assert repo.current_user == "Alice"

    # 존재하지 않는 브랜치 전환 시 RepoError
    try:
        repo.switch("no-such-branch")
        assert False, "RepoError expected"
    except RepoError as e:
        assert "Unknown branch: no-such-branch" in str(e)

    # 존재하지 않는 커밋 조회 시 RepoError
    try:
        repo.get_commit("nonexistent")
        assert False, "RepoError expected"
    except RepoError as e:
        assert "Unknown commit: nonexistent" in str(e)

    # 잘못된 인자 개수 처리
    assert dispatch(repo, ["INIT"]) == "Invalid args"
    assert dispatch(repo, ["BRANCH"]) == "Invalid args"
    assert dispatch(repo, ["SWITCH"]) == "Invalid args"
    assert dispatch(repo, ["COMMIT"]) == "Invalid args"
    assert dispatch(repo, ["PATH", "only_one"]) == "Invalid args"
    assert dispatch(repo, ["ANCESTORS"]) == "Invalid args"
    assert dispatch(repo, ["SEARCH"]) == "Invalid args"
    assert dispatch(repo, ["LOG", "--unknown-opt"]) == "Invalid args"


def test_disconnected_path_returns_none() -> None:
    """경로가 없는 분리된 컴포넌트 간 PATH 질의 시 None(No path) 처리를 검증합니다."""
    a = Commit("a", "msg", "User", "t", [], 0)
    b = Commit("b", "msg", "User", "t", [], 1)
    commits = {"a": a, "b": b}
    assert shortest_path(commits, "a", "b") is None


if __name__ == "__main__":
    print("🚀 [Mini Git Test Suite] 단위 및 통합 테스트 시작...")
    test_merge_sort_is_correct_and_stable()
    print("  ✅ 1. 병합 정렬 정렬 정확성 및 안정성 검증 통과")
    r, c1, c2, c3 = test_repo_flow_and_log_order()
    print("  ✅ 2. 저장소 워크플로우 및 위상 정렬 순서 검증 통과")
    test_path_and_ancestors(r, c1, c2, c3)
    print("  ✅ 3. 무방향 최단 경로 및 조상 탐색 검증 통과")
    test_search_uses_inverted_index(r, c1, c2, c3)
    print("  ✅ 4. 역색인 키워드/작성자 검색 검증 통과")
    test_shortest_path_lexicographic_tiebreak()
    print("  ✅ 5. 최단 경로 사전순 타이브레이크 검증 통과")
    test_unique_hash_on_identical_inputs()
    print("  ✅ 6. 커밋 해시 유일성 검증 통과")
    test_error_handling_and_cli_dispatch()
    print("  ✅ 7. CLI 디스패치 및 에러 처리 표준 검증 통과")
    test_disconnected_path_returns_none()
    print("  ✅ 8. 비연결 그래프 No path 검증 통과")
    print("🎉 All 8 tests passed successfully!")
