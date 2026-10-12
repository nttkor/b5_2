"""Repository: branches, HEAD, and the commit store (hash -> Commit).

이 모듈은 Mini Git의 상태 관리 코어인 Repository 클래스와 전용 예외 RepoError를 정의합니다.
커밋 저장소(해시맵 기반 인메모리 스토어), 브랜치 포인터, 현재 체크아웃된 브랜치(HEAD),
현재 작성자 정보 및 고유 해시 생성 파이프라인을 캡슐화합니다.
"""

from __future__ import annotations

import hashlib
from datetime import datetime

from .commit import Commit
from .index import InvertedIndex


MAX_COLLISION_RETRIES: int = 1000  # 해시 충돌 발생 시 최대 재시도 임계값


class RepoError(Exception):
    """Raised for invalid mini-git operations (unknown branch/commit, bad state).

    미초기화 상태 접근, 미식별 브랜치 전환, 존재하지 않는 커밋 참조 등
    Mini Git 도메인 규칙 위반 시 발생하는 사용자 정의 예외 클래스입니다.
    """


class Repository:
    """Mini Git의 인메모리 저장소 및 형상 상태 관리 클래스.

    Attributes:
        commits (dict[str, Commit]): 커밋 해시 -> 불변 Commit 노드 매핑 딕셔너리.
            한 번 저장된 Commit 객체는 내용이 절대 변경되지 않는 불변(Immutable) 상태를 유지합니다.
        branches (dict[str, str | None]): 브랜치 이름 -> 최신 커밋 해시 매핑 딕셔너리.
        current_branch (str | None): 현재 체크아웃된 활성 브랜치 이름.
        current_user (str | None): 현재 세션의 작업자 이름.
        index (InvertedIndex): 키워드 및 작성자 검색을 위한 역색인 인덱서.
        _next_order (int): 단조 증가 커밋 생성 번호 (정렬 시 안정성 보장용).
        initialized (bool): 저장소 초기화 완료 여부 플래그.
        seed (int | None): 테스트 재현성을 위한 결정론적 해시 시드 오프셋.
    """

    def __init__(self, seed: int | None = None) -> None:
        """빈 Mini Git 저장소 인스턴스를 생성합니다.

        Args:
            seed (int | None): 테스트 재현성을 위한 고정 시드 오프셋 (기본값: None).
        """
        self.commits: dict[str, Commit] = {}
        self.branches: dict[str, str | None] = {}
        self.current_branch: str | None = None
        self.current_user: str | None = None
        self.index: InvertedIndex = InvertedIndex()
        self._next_order: int = 0
        self.initialized: bool = False
        self.seed: int | None = seed

    def init(self, user_name: str, seed: int | None = None) -> None:
        """새 저장소를 초기화하고 main 브랜치와 작업자를 설정합니다.

        이미 저장소가 초기화된 상태에서 init을 재호출할 경우,
        기존 커밋 히스토리와 브랜치 포인터, 역색인은 모두 완전히 리셋됩니다.

        Args:
            user_name (str): 초기 사용자 이름.
            seed (int | None): 테스트 재현성을 위한 고정 시드 오프셋 (지정 시 갱신).
        """
        self.commits = {}
        self.branches = {"main": None}  # 초기에는 커밋이 없으므로 None
        self.current_branch = "main"    # 기본 브랜치로 main 지정
        self.current_user = user_name
        self.index = InvertedIndex()
        self._next_order = 0
        self.initialized = True
        if seed is not None:
            self.seed = seed

    def branch(self, name: str) -> None:
        """현재 HEAD 커밋을 가리키는 새로운 브랜치 참조를 생성합니다.

        이미 존재하는 브랜치명을 다시 생성할 경우, 현재 활성 브랜치의 HEAD 커밋으로
        포인터를 갱신(덮어쓰기/Fast-forward)하는 명시적 정책을 따릅니다.

        Args:
            name (str): 생성할 새 브랜치 이름.

        Raises:
            RepoError: 저장소가 초기화되지 않은 경우.
        """
        self._require_init()
        # 현재 활성 브랜치가 가리키는 최신 커밋 해시를 복제
        self.branches[name] = self.branches[self.current_branch]

    def switch(self, name: str) -> None:
        """HEAD 포인터를 지정한 기존 브랜치로 이동합니다.

        Args:
            name (str): 전환할 대상 브랜치 이름.

        Raises:
            RepoError: 저장소 미초기화 또는 대상 브랜치가 존재하지 않는 경우.
        """
        self._require_init()
        if name not in self.branches:
            raise RepoError(f"Unknown branch: {name}")
        self.current_branch = name

    def commit(self, message: str) -> Commit:
        """현재 활성 브랜치(HEAD)를 부모로 삼아 새로운 커밋을 생성하고 등록합니다.

        Args:
            message (str): 커밋 설명 메시지.

        Returns:
            Commit: 생성된 Commit 노드 객체.

        Raises:
            RepoError: 저장소가 초기화되지 않은 경우.
        """
        self._require_init()
        parent = self.branches[self.current_branch]
        parents: list[str] = [parent] if parent else []
        timestamp: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 단조 카운터 및 솔트 기반 고유 6자리 해시 발급
        commit_hash: str = self._new_hash(message, timestamp)

        # 신규 커밋 객체 생성
        c = Commit(
            commit_hash=commit_hash,
            message=message,
            author=self.current_user,  # type: ignore[arg-type]
            timestamp=timestamp,
            parents=parents,
            order=self._next_order,
        )

        self._next_order += 1
        self.commits[commit_hash] = c
        self.branches[self.current_branch] = commit_hash  # 활성 브랜치의 HEAD 갱신
        self.index.add(c)                                 # 역색인에 커밋 정보 즉시 등록
        return c

    def get_commit(self, commit_hash: str) -> Commit:
        """해시로 커밋을 조회합니다.

        Args:
            commit_hash (str): 조회할 커밋 해시.

        Returns:
            Commit: 일치하는 커밋 노드 객체.

        Raises:
            RepoError: 커밋이 저장소 내에 존재하지 않는 경우.
        """
        if commit_hash not in self.commits:
            raise RepoError(f"Unknown commit: {commit_hash}")
        return self.commits[commit_hash]

    def _new_hash(self, message: str, timestamp: str) -> str:
        """충돌이 발생하지 않는 유일한 6자리 SHA-1 커밋 해시를 생성합니다.

        Counter + salt guarantees uniqueness even if two commits share
        message/timestamp/order (salt only advances on an actual clash).
        테스트 재현성을 위해 seed가 설정된 경우 base salt 오프셋으로 반영됩니다.

        Args:
            message (str): 커밋 메시지.
            timestamp (str): 생성 타임스탬프.

        Returns:
            str: 6자리 16진수 고유 해시 문자열.

        Raises:
            RepoError: MAX_COLLISION_RETRIES를 초과하여 고유 해시 발급에 실패한 경우.
        """
        salt: int = 0
        base: int = self.seed if self.seed is not None else 0
        while salt < MAX_COLLISION_RETRIES:
            # 순번, 솔트, 메시지, 시각을 결합하여 바이트 스트림 생성
            effective_salt = salt + base
            raw: bytes = f"{self._next_order}:{effective_salt}:{message}:{timestamp}".encode("utf-8")
            digest: str = hashlib.sha1(raw).hexdigest()[:6]
            if digest not in self.commits:
                return digest
            salt += 1

        raise RepoError(f"Failed to generate unique hash after {MAX_COLLISION_RETRIES} retries")

    def _require_init(self) -> None:
        """저장소 초기화 여부를 검사하고 미초기화 시 예외를 발생시킵니다.

        Raises:
            RepoError: 저장소가 아직 init되지 않은 경우.
        """
        if not self.initialized:
            raise RepoError("Repository not initialized. Run INIT <user_name> first.")
