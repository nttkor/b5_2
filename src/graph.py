"""Graph algorithms over the commit DAG: no graph library used.

- topological_order: parents printed before children (LOG's default order).
- shortest_path: BFS over parent links treated as undirected edges, with a
  lexicographic tie-break.
- ancestors: every commit reachable by following parent pointers.

미션의 제약 조건인 '그래프 전용 라이브러리 사용 금지'를 엄격히 준수하여,
Kahn 알고리즘 기반 위상 정렬, 너비 우선 탐색(BFS) 기반 최단 경로 탐색,
깊이 우선 순회(DFS) 기반 조상 커밋 추적 알고리즘을 밑바닥부터 구현하였습니다.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from .sorting import merge_sort

if TYPE_CHECKING:
    from .commit import Commit


def topological_order(commits_by_hash: dict[str, Commit]) -> list[str]:
    """Kahn's algorithm: every parent appears before its children.

    A commit's parents must already exist at commit time, so creation order
    already happens to satisfy that invariant in this implementation. This
    function still does real in-degree tracking (rather than just returning
    creation order) so it stays correct even for DAGs where that invariant
    doesn't hold -- e.g. imported/replayed history.

    커밋 DAG에서 부모 커밋이 자식 커밋보다 항상 먼저 출력되도록 위상 정렬 순서를 계산합니다.
    방향 간선을 '부모 -> 자식'으로 모델링하여 진입 차수(in-degree)가 0인 루트 커밋부터 큐에 투입합니다.

    Args:
        commits_by_hash (dict[str, Commit]): 해시를 키로, Commit 객체를 값으로 갖는 저장소 딕셔너리.

    Returns:
        list[str]: 위상 정렬된 커밋 해시들의 리스트 (부모 -> 자식 순).

    Complexity:
        - 시간 복잡도: O(V + E) + O(V log V) (초기 정렬 비용).
        - 공간 복잡도: O(V + E) (인접 리스트 및 진입차수 테이블).
    """
    # 1. 부모 -> 자식 방향 인접 리스트 및 자식 노드의 진입 차수(in-degree) 초기화
    children: dict[str, list[str]] = {h: [] for h in commits_by_hash}
    indegree: dict[str, int] = {h: 0 for h in commits_by_hash}

    for h, c in commits_by_hash.items():
        for p in c.parents:
            children[p].append(h)   # 부모(p) -> 자식(h) 간선 등록
            indegree[h] += 1        # 자식(h)의 진입 차수 1 증가

    # 2. 진입 차수가 0인 노드(루트 커밋들)를 생성 순서(order) 기준 안정 정렬하여 큐 시딩
    by_creation = merge_sort(list(commits_by_hash.values()), key=lambda c: c.order)
    ready: list[str] = [c.hash for c in by_creation if indegree[c.hash] == 0]

    # 3. Kahn 알고리즘 실행: 큐에서 정점을 하나씩 꺼내며 연결된 간선 제거
    order: list[str] = []
    i: int = 0
    while i < len(ready):
        h = ready[i]
        i += 1
        order.append(h)
        for child in children[h]:
            indegree[child] -= 1
            if indegree[child] == 0:
                ready.append(child)

    return order


def _undirected_adjacency(commits_by_hash: dict[str, Commit]) -> dict[str, list[str]]:
    """커밋-부모 간선을 양방향(무방향)으로 변환한 인접 리스트를 구성합니다.

    Args:
        commits_by_hash (dict[str, Commit]): 전체 커밋 딕셔너리.

    Returns:
        dict[str, list[str]]: 정점별 인접 이웃 정점 해시 목록 딕셔너리.
    """
    adjacency: dict[str, list[str]] = {h: [] for h in commits_by_hash}
    for h, c in commits_by_hash.items():
        for p in c.parents:
            adjacency[h].append(p)  # 자식 -> 부모 간선
            adjacency[p].append(h)  # 부모 -> 자식 간선
    return adjacency


def _bfs_distances(adjacency: dict[str, list[str]], source: str) -> dict[str, int]:
    """Hop-distance from source to every reachable node.

    주어진 출발 노드(source)로부터 도달 가능한 모든 노드까지의 최단 홉(hop) 거리를 BFS로 계산합니다.

    Args:
        adjacency (dict[str, list[str]]): 무방향 인접 리스트.
        source (str): 거리 계산의 기준이 되는 출발 정점 해시.

    Returns:
        dict[str, int]: 각 도달 가능 정점별 최단 거리 딕셔너리 (dist[node] = 거리).
    """
    dist: dict[str, int] = {source: 0}
    queue: list[str] = [source]
    i: int = 0
    while i < len(queue):
        node = queue[i]
        i += 1
        for neighbor in adjacency[node]:
            if neighbor not in dist:
                dist[neighbor] = dist[node] + 1
                queue.append(neighbor)
    return dist


def shortest_path(commits_by_hash: dict[str, Commit], start: str, end: str) -> list[str] | None:
    """Shortest path treating parent links as undirected edges.

    Returns a list of hashes from start to end, or None if there is no path.

    Tie-break: among all shortest paths, pick the one whose
    "hash1->hash2->..." string is lexicographically smallest. Since every
    shortest path has the same number of hops, comparing the joined strings
    is equivalent to comparing hop-by-hop -- so a greedy walk that always
    steps to the smallest-hash neighbor moving strictly closer to the
    target reproduces exactly that path, in O(V+E) instead of enumerating
    every shortest path and sorting them.

    두 커밋 간의 무방향 최단 경로(간선 수 최소)를 탐색합니다.
    동일한 최단 거리를 가진 경로가 복수 개 존재할 경우, 문자열 "h1->h2->..." 기준
    사전순(Lexicographical order)으로 가장 앞서는 경로를 결정론적으로 선택합니다.

    Args:
        commits_by_hash (dict[str, Commit]): 전체 커밋 딕셔너리.
        start (str): 출발 커밋 해시.
        end (str): 도착 커밋 해시.

    Returns:
        list[str] | None: 출발부터 도착까지의 정점 해시 리스트. 도달 불가능하거나 미존재 시 None.

    Complexity:
        - 시간 복잡도: O(V + E) (BFS 탐색 및 타깃 역추적 단계).
        - 공간 복잡도: O(V + E).
    """
    # 유효성 검사: 존재하지 않는 커밋인 경우 None
    if start not in commits_by_hash or end not in commits_by_hash:
        return None
    # 동일 커밋인 경우 경로 길이는 0 (자기 자신 반환)
    if start == end:
        return [start]

    # 무방향 그래프 인접 리스트 구축
    adjacency = _undirected_adjacency(commits_by_hash)

    # 목적지(end)로부터 각 노드까지의 거리를 BFS로 선계산
    # (출발지에서 목적지로 전진할 때 거리가 정확히 1씩 줄어드는 이웃을 선택하기 위함)
    dist_to_end = _bfs_distances(adjacency, end)
    if start not in dist_to_end:
        return None  # 경로가 존재하지 않는 경우 (분리된 컴포넌트)

    path: list[str] = [start]
    current = start
    while current != end:
        # 목적지로 거리가 1 단축되는 이웃 후보들 중 해시 문자열 사전순으로 가장 작은 것 선택
        candidates = merge_sort(adjacency[current], key=lambda h: h)
        next_hop = None
        for neighbor in candidates:
            if dist_to_end.get(neighbor) == dist_to_end[current] - 1:
                next_hop = neighbor
                break
        current = next_hop  # type: ignore[assignment]
        path.append(current)

    return path


def ancestors(commits_by_hash: dict[str, Commit], start_hash: str) -> set[str] | None:
    """All commits reachable by following parent edges from start_hash (excludes itself).

    Returns None if start_hash is unknown, otherwise a set of hashes.

    특정 커밋 노드로부터 부모 포인터를 역방향으로 재귀 추적하여 도달 가능한 모든 조상 커밋들을 탐색합니다.
    시작 커밋 자신은 결과 집합에서 제외됩니다.

    Args:
        commits_by_hash (dict[str, Commit]): 전체 커밋 딕셔너리.
        start_hash (str): 조상을 탐색할 기준 커밋 해시.

    Returns:
        set[str] | None: 조상 커밋들의 해시 집합. 존재하지 않는 커밋이면 None.

    Complexity:
        - 시간 복잡도: O(V_ancestors + E_ancestors).
        - 공간 복잡도: O(V_ancestors) (방문 집합 및 스택).
    """
    if start_hash not in commits_by_hash:
        return None

    seen: set[str] = set()
    # 시작 커밋의 직계 부모 노드들부터 DFS 스택에 투입 (자기 자신 제외)
    stack: list[str] = list(commits_by_hash[start_hash].parents)

    while stack:
        h = stack.pop()
        if h in seen:
            continue
        seen.add(h)
        if h in commits_by_hash:
            stack.extend(commits_by_hash[h].parents)

    return seen
