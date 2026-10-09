"""REPL for mini-git: parses input, dispatches to the Repository, prints results.

이 모듈은 Mini Git의 CLI 인터페이스를 담당합니다.
shlex를 통한 안전한 따옴표 인자 파싱, 대소문자 비구분 명령어 라우팅,
출력 형식 정규화 및 표준 에러 메시지 처리를 수행합니다.
"""

from __future__ import annotations

import shlex
from typing import Sequence

from .graph import ancestors as compute_ancestors
from .graph import shortest_path, topological_order
from .repo import RepoError, Repository
from .sorting import merge_sort
from .commit import Commit

PROMPT: str = "mini-git> "


def format_commit_line(commit: Commit) -> str:
    """커밋 노드의 표준 출력 문자열(2줄 포맷)을 생성합니다.

    Args:
        commit (Commit): 포맷팅할 커밋 노드.

    Returns:
        str: 커밋 정보 및 메시지 문자열.
    """
    return f"commit {commit.hash} ({commit.author}, {commit.timestamp})\n{commit.message}"


def _run_log(repo: Repository, args: Sequence[str]) -> str:
    """LOG 명령어를 실행하고 정렬 기준에 따른 로그 문자열을 반환합니다.

    Args:
        repo (Repository): 저장소 객체.
        args (Sequence[str]): 명령어 인자 목록 (옵션 플래그 포함).

    Returns:
        str: 커밋 로그 결과 문자열 또는 에러 메시지.
    """
    sort_by: str | None = None
    for arg in args:
        if arg.startswith("--sort-by="):
            sort_by = arg.split("=", 1)[1]
        else:
            return "Invalid args"
    if sort_by not in (None, "date", "author"):
        return "Invalid args"

    if sort_by is None:
        # 기본 순서: 부모가 자식보다 먼저 나오는 위상 정렬 순서
        commits = [repo.commits[h] for h in topological_order(repo.commits)]
    elif sort_by == "date":
        # 타임스탬프 기준 오름차순 정렬
        commits = merge_sort(list(repo.commits.values()), key=lambda c: c.timestamp)
    else:
        # 작성자 이름 기준 안정 정렬
        commits = merge_sort(list(repo.commits.values()), key=lambda c: c.author)

    if not commits:
        return "No commits yet."
    return "\n".join(format_commit_line(c) for c in commits)


def _run_search(repo: Repository, args: Sequence[str]) -> str:
    """SEARCH 명령어를 역색인 기반으로 실행하고 결과를 반환합니다.

    Args:
        repo (Repository): 저장소 객체.
        args (Sequence[str]): 검색 키워드 또는 작성자 옵션 인자.

    Returns:
        str: 검색된 커밋 목록 문자열 또는 에러 메시지.
    """
    if len(args) != 1:
        return "Invalid args"
    arg = args[0]
    if arg.startswith("--author="):
        hashes = repo.index.search_author(arg.split("=", 1)[1])
    else:
        hashes = repo.index.search_keyword(arg)

    if not hashes:
        return "Found 0 commits."
    lines = [f"- {h}: {repo.commits[h].message}" for h in hashes]
    return f"Found {len(hashes)} commit(s):\n\n" + "\n".join(lines)


def dispatch(repo: Repository, tokens: Sequence[str]) -> str:
    """파싱된 토큰 목록을 해석하여 적절한 저장소/알고리즘 작업을 디스패치합니다.

    명령어는 대소문자를 구분하지 않으며, 각 명령어에 따른 인자 개수 및 유효성을 검증합니다.

    Args:
        repo (Repository): Mini Git 저장소 인스턴스.
        tokens (Sequence[str]): 토큰화된 명령어 및 인자 리스트.

    Returns:
        str: 명령어 실행 결과 텍스트.
    """
    if not tokens:
        return ""
    cmd = tokens[0].upper()
    args = tokens[1:]

    # 1. 저장소 초기화
    if cmd == "INIT":
        if len(args) != 1:
            return "Invalid args"
        repo.init(args[0])
        return (
            f"Initialized repository.\n"
            f"Current branch: {repo.current_branch}\n"
            f"Current user: {repo.current_user}"
        )

    # 2. 브랜치 생성
    if cmd == "BRANCH":
        if len(args) != 1:
            return "Invalid args"
        repo.branch(args[0])
        return f"Created branch: {args[0]}"

    # 3. 브랜치 전환
    if cmd == "SWITCH":
        if len(args) != 1:
            return "Invalid args"
        repo.switch(args[0])
        return f"Switched to branch: {args[0]}"

    # 4. 커밋 생성
    if cmd == "COMMIT":
        if len(args) != 1:
            return "Invalid args"
        c = repo.commit(args[0])
        return f"[{repo.current_branch} {c.hash}] {c.message}"

    # 5. 커밋 로그 출력
    if cmd == "LOG":
        return _run_log(repo, args)

    # 6. 두 커밋 간 최단 경로 탐색
    if cmd == "PATH":
        if len(args) != 2:
            return "Invalid args"
        repo.get_commit(args[0])
        repo.get_commit(args[1])
        path = shortest_path(repo.commits, args[0], args[1])
        return "Path: " + " -> ".join(path) if path else "No path"

    # 7. 특정 커밋의 모든 조상 탐색
    if cmd == "ANCESTORS":
        if len(args) != 1:
            return "Invalid args"
        repo.get_commit(args[0])
        found = compute_ancestors(repo.commits, args[0])
        if not found:
            return f"No ancestors for {args[0]}."
        ordered = merge_sort(list(found), key=lambda h: repo.commits[h].order)
        lines = [f"- {h}: {repo.commits[h].message}" for h in ordered]
        return f"Ancestors of {args[0]}:\n" + "\n".join(lines)

    # 8. 역색인 기반 검색
    if cmd == "SEARCH":
        return _run_search(repo, args)

    return f"Unknown command: {tokens[0]}"


def main() -> None:
    """Mini Git 대화형 REPL 루프를 실행합니다.

    표준 입력으로부터 명령을 읽어 실행하고 결과를 표준 출력으로 전달합니다.
    'exit' 또는 'quit' 입력 시 종료됩니다.
    """
    repo = Repository()
    while True:
        try:
            line = input(PROMPT)
        except EOFError:
            break
        line = line.strip()
        if not line:
            continue
        if line.lower() in ("exit", "quit"):
            break
        try:
            tokens = shlex.split(line)
        except ValueError:
            print("Invalid args")
            continue
        try:
            result = dispatch(repo, tokens)
        except RepoError as exc:
            result = str(exc)
        if result:
            print(result)


if __name__ == "__main__":
    main()
