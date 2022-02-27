from typing import Iterator, List, Tuple


def includes_all_texts(lines: List[str], texts: List[str]) -> bool:
    remaining_text_set = set(texts)
    for L in lines:
        for text in list(remaining_text_set):
            if L.find(text) >= 0:
                remaining_text_set.discard(text)
                if not remaining_text_set:
                    return True
    return False


def includes_any_of_texts(lines: List[str], texts: List[str]) -> bool:
    for L in lines:
        for text in texts:
            if L.find(text) >= 0:
                return True
    return False


def extract_para_iter(lines: List[str], window: int) -> Iterator[Tuple[Tuple[int, int], List[str]]]:
    if window == 1:
        for pos, line in enumerate(lines):
            yield (pos, pos + 1), [line]
    else:
        len_lines = len(lines)
        if len_lines <= window:
            yield (0, len_lines), lines
        else:
            for pos in range(0, len_lines - (window - window // 2), window // 2):
                end_pos = min(pos + window, len_lines)
                yield (pos, end_pos), lines[pos:end_pos]
