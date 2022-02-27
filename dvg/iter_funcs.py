from typing import Iterable, Iterator, List, Tuple, TypeVar


T = TypeVar("T")


def remove_non_first_appearances(lst: Iterable[T]) -> List[T]:
    s = set()
    r = []
    for i in lst:
        if i not in s:
            r.append(i)
            s.add(i)
    return r


def ranges_overwrapping(range1: Tuple[int, int], range2: Tuple[int, int]) -> bool:
    assert min(range1) >= 0
    assert min(range2) >= 0
    if 0 <= range1[0] <= range2[0]:
        return range2[0] < range1[1]
    else:
        # assert range2[0] <= range1[0]
        return range1[0] < range2[1]


def chunked(it: Iterable[T], chunk_size: int = 10000) -> Iterator[List[T]]:
    found_items = []
    for f in it:
        found_items.append(f)
        if len(found_items) >= chunk_size:
            yield found_items
            found_items = []
    if found_items:
        yield found_items
