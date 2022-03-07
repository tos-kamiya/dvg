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


def chunked_iter(it: Iterable[T], max_chunk_size: int) -> Iterator[List[T]]:
    assert max_chunk_size >= 1
    chunk_size = 10
    chunk = []
    for item in it:
        chunk.append(item)
        if len(chunk) >= chunk_size:
            yield chunk
            chunk[:] = []
            chunk_size = min(max_chunk_size, chunk_size * 3 // 2)
    if chunk:
        yield chunk


def sliding_window_iter(range_length: int, window: int) -> Iterator[Tuple[int, int]]:
    if window == 1:
        for pos in range(range_length):
            yield pos, pos + 1
    elif range_length <= window:
        yield 0, range_length
    else:
        for pos in range(0, range_length - (window - window // 2), window // 2):
            end_pos = min(pos + window, range_length)
            yield pos, end_pos
