from collections import namedtuple

from typing import List, Tuple

DummyAuthor = namedtuple('DummyAuthor', ['bot'])
DummyMessage = namedtuple('DummyMessage', ['content', 'author'])

def fuzzy_match(query: str, target: str) -> bool:
    # Returns True if $query is a (potentially disjoint)
    # subset of $target.
    iq, it = 0, 0
    while iq < len(query) and it < len(target):
        iq += query[iq] == target[it]
        it += 1
    return iq == len(query)

def extract_pattern_between(query: str, sep_l: str, sep_r: str) -> List[Tuple[int, int]]:
    # Searches for a pattern between two separators, can fetch multiple occurences.
    # My name is [[Risitop]] and I love [[programming]] [[]].
    #              ^      ^               ^          ^    ^
    # -> ["Risitop", "programming", ""]
    idx, nl, nr = 0, len(sep_l), len(sep_r)
    output = []
    while idx + nl < len(query):
        if query[idx:idx+nl] == sep_l:
            idx = idx + nl
            idx2 = idx
            while idx2 + nr < len(query) and query[idx2:idx2+nr] != sep_r: idx2 += 1
            output.append(query[idx:idx2])
            idx = idx2 + nr - 1
        idx += 1
    return output