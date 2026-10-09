"""Custom sorting.

The mission bans sorted()/list.sort(). Merge sort is used everywhere a sort
is needed because it is O(n log n) in both the average AND worst case
(unlike quicksort, which degrades to O(n^2) on adversarial input), and it is
stable -- equal-key items keep their original relative order, which matters
for LOG --sort-by=author (commits by the same author should stay in the
order they were made).

미션의 '표준 정렬 API 사용 금지(sorted(), list.sort() 금지)' 제약을 준수하기 위해
분할 정복(Divide and Conquer) 방식의 병합 정렬(Merge Sort)을 직접 구현하였습니다.
"""

from __future__ import annotations
from typing import Any, Callable, Sequence, TypeVar

T = TypeVar("T")


def merge_sort(items: Sequence[T], key: Callable[[T], Any]) -> list[T]:
    """Return a new list sorted ascending by key(item). Stable. Does not mutate items.

    주어진 시퀀스를 키 추출 함수(key)의 반환값 기준 오름차순으로 안정 정렬(Stable Sort)합니다.
    분할 정복 기법을 통해 리스트를 절반으로 재귀 분할한 뒤 병합합니다.

    Args:
        items (Sequence[T]): 정렬할 원소들의 시퀀스 (원본은 변경되지 않음).
        key (Callable[[T], Any]): 각 원소에서 비교 키를 추출하는 콜러블 함수.

    Returns:
        list[T]: 오름차순으로 안정 정렬된 새로운 리스트.

    Complexity:
        - 시간 복잡도: 평균 O(N log N), 최악 O(N log N) (항상 균등 이분할).
        - 공간 복잡도: O(N) (병합 과정에서의 추가 임시 배열 공간).
    """
    # 기저 조건: 원소가 0개 또는 1개이면 이미 정렬된 상태
    if len(items) <= 1:
        return list(items)

    # 분할(Divide): 배열의 중간 지점을 계산하여 좌우 분할
    mid: int = len(items) // 2
    left: list[T] = merge_sort(items[:mid], key)
    right: list[T] = merge_sort(items[mid:], key)

    # 정복 및 결합(Conquer & Combine): 정렬된 두 부분 배열을 안정적으로 병합
    return _merge(left, right, key)


def _merge(left: list[T], right: list[T], key: Callable[[T], Any]) -> list[T]:
    """정렬된 두 하위 리스트를 단일 정렬 리스트로 안정적으로 병합합니다.

    Args:
        left (list[T]): 좌측 정렬 리스트.
        right (list[T]): 우측 정렬 리스트.
        key (Callable[[T], Any]): 비교 키 함수.

    Returns:
        list[T]: 병합된 오름차순 리스트.
    """
    merged: list[T] = []
    i: int = 0
    j: int = 0

    while i < len(left) and j < len(right):
        # '<=' (not '<') on the right side is what keeps the sort stable:
        # a tie always takes the left (earlier) item first.
        # 동일 키일 때 좌측(선행) 원소를 먼저 채택함으로써 안정 정렬(Stability) 보장
        if key(left[i]) <= key(right[j]):
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    # 남아있는 잔여 원소들을 결과에 추가
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged
