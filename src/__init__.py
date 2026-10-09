"""mini_git: a from-scratch, in-memory Mini Git CLI engine.

이 패키지는 외부 서드파티 라이브러리 없이 순수 Python 표준 라이브러리만으로
Git의 핵심 모델(커밋 DAG, 브랜치 관리, 위상 정렬, BFS 최단 경로, 역색인 검색, 병합 정렬)을
구현한 경량 버전 관리 엔진입니다.
"""

from .commit import Commit
from .graph import ancestors, shortest_path, topological_order
from .index import InvertedIndex
from .repo import RepoError, Repository
from .sorting import merge_sort
from .cli import dispatch, main

__all__ = [
    "Commit",
    "Repository",
    "RepoError",
    "InvertedIndex",
    "ancestors",
    "shortest_path",
    "topological_order",
    "merge_sort",
    "dispatch",
    "main",
]
