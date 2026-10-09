"""Commit: one vertex of the mini-git commit DAG.

이 모듈은 Mini Git의 핵심 정점(Vertex)인 Commit 객체를 정의합니다.
각 커밋 노드는 고유 해시, 커밋 메시지, 작성자, 생성 시각, 부모 커밋 목록,
그리고 생성 순서 번호를 보유하며 그래프 상의 방향성 비순환 구조(DAG)를 구성합니다.
"""

from __future__ import annotations


class Commit:
    """Mini Git 커밋 그래프의 단일 노드(정점)를 표현하는 클래스.

    A single commit in the commit DAG.
    parents is a list of parent commit hashes (0+ parents -- 0 for a root
    commit, 1 for a normal commit, 2+ for a merge commit).
    order is the creation index, used to seed topological order and as a
    stable tie-breaker when sorting.

    Attributes:
        hash (str): 커밋 식별용 6자리 16진수 고유 해시 문자열.
        message (str): 사용자가 작성한 커밋 설명 메시지.
        author (str): 커밋 작성자 이름 (INIT 시 지정된 사용자).
        timestamp (str): 'YYYY-MM-DD HH:MM:SS' 형식의 생성 일시.
        parents (list[str]): 부모 커밋 해시 목록 (루트는 0개, 일반은 1개, 병합은 2개 이상).
        order (int): 저장소 내에서 부여된 생성 순번 (0부터 1씩 증가하는 정수).
    """

    def __init__(
        self,
        commit_hash: str,
        message: str,
        author: str,
        timestamp: str,
        parents: list[str],
        order: int,
    ) -> None:
        """Commit 노드를 초기화합니다.

        Args:
            commit_hash (str): 커밋 고유 해시 (6자리 hex string).
            message (str): 커밋 메시지.
            author (str): 작성자 이름.
            timestamp (str): 커밋 생성 일시 문자열.
            parents (list[str]): 부모 커밋들의 해시 문자열 리스트.
            order (int): 생성 순서 인덱스.
        """
        self.hash: str = commit_hash          # 6자리 고유 식별자
        self.message: str = message            # 커밋 로그 메시지
        self.author: str = author              # 작성자 명
        self.timestamp: str = timestamp        # 생성 타임스탬프
        self.parents: list[str] = parents      # 부모 커밋 해시 리스트 (자식 -> 부모 방향 참조)
        self.order: int = order                # 생성 순서 식별자 (안정 정렬 타이브레이커)

    def __repr__(self) -> str:
        """개발 및 디버깅을 위한 커밋 표현식을 반환합니다.

        Returns:
            str: Commit 객체 디버그 문자열.
        """
        return f"Commit({self.hash!r}, {self.message!r})"
