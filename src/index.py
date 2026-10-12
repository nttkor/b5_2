"""Inverted index: keyword -> commit hashes, author -> commit hashes.

Without this, SEARCH would have to scan every commit's message (O(commits))
on every call. With it, SEARCH does one dict lookup (O(matches)) because the
work of scanning each message happens once, at commit time, instead of once
per search.

이 모듈은 커밋 생성 시점에 토큰화된 키워드 및 작성자별로 커밋 해시 목록을
사전 색인화(Pre-indexing)하여 저장하는 역색인(Inverted Index) 자료구조를 제공합니다.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .commit import Commit


class InvertedIndex:
    """커밋 키워드 및 작성자별 해시 목록을 매핑하는 역색인 클래스.

    Attributes:
        by_keyword (dict[str, list[str]]): 소문자 정규화된 토큰별 커밋 해시 리스트.
        by_author (dict[str, list[str]]): 작성자 이름별 커밋 해시 리스트.
    """

    def __init__(self) -> None:
        """빈 역색인 테이블을 초기화합니다."""
        self.by_keyword: dict[str, list[str]] = {}
        self.by_author: dict[str, list[str]] = {}

    def add(self, commit: Commit) -> None:
        """새로 생성된 커밋을 역색인에 등록합니다.

        [토큰화 및 포스팅 리스트 정책 요약]
        1. 정규화 및 분할: 커밋 메시지를 소문자로 정규화(`.lower()`)한 후 공백 문자 기준으로 분할(`.split()`)합니다.
        2. 식별자 보존: 구두점을 제거하지 않아 `fix(auth):`, `v1.0.0`, `#123` 등 고유 식별자 토큰을 보존합니다.
        3. 중복 토큰 필터링: 한 커밋 메시지 내에 동일 단어가 중복 등장하더라도 해당 커밋 해시는 포스팅 리스트에 단 1회만 등록(Unique)됩니다.
        4. 순서 보장: 포스팅 리스트는 커밋이 저장소에 추가된 시간/생성 순서(`order` 순)를 엄격히 유지(Append-only)합니다.
        아울러 작성자 이름(대소문자 유지)별 포스팅 리스트 역시 생성 순서대로 매핑됩니다.

        Args:
            commit (Commit): 역색인에 등록할 커밋 노드 객체.

        Complexity:
            시간 복잡도: O(W) (W는 커밋 메시지의 단어 수).
        """
        # 동일 커밋 내 중복 단어는 1회만 색인 등록하여 포스팅 리스트 내 해시 유일성 보장
        seen_tokens: set[str] = set()
        for token in commit.message.lower().split():
            if token not in seen_tokens:
                seen_tokens.add(token)
                self.by_keyword.setdefault(token, []).append(commit.hash)

        # 작성자별 역색인 목록에 추가 (생성 순서 유지)
        self.by_author.setdefault(commit.author, []).append(commit.hash)

    def search_keyword(self, keyword: str) -> list[str]:
        """특정 키워드가 포함된 커밋들의 해시 목록을 조회합니다.

        Args:
            keyword (str): 검색할 단일 키워드 (대소문자 무관).

        Returns:
            list[str]: 해당 키워드를 포함하는 커밋 해시들의 리스트 (복사본).

        Complexity:
            시간 복잡도: 평균 O(K) (K는 매칭된 커밋 수, 해시맵 O(1) 조회).
        """
        return list(self.by_keyword.get(keyword.lower(), []))

    def search_author(self, author: str) -> list[str]:
        """특정 작성자가 생성한 커밋들의 해시 목록을 조회합니다.

        Args:
            author (str): 검색할 작성자 이름 (대소문자 정확히 일치).

        Returns:
            list[str]: 해당 작성자가 생성한 커밋 해시들의 리스트 (복사본).

        Complexity:
            시간 복잡도: 평균 O(K) (K는 해당 작성자의 커밋 수, 해시맵 O(1) 조회).
        """
        return list(self.by_author.get(author, []))
