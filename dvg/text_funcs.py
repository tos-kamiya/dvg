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
