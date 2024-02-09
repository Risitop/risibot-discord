from collections import namedtuple

DummyMessage = namedtuple('DummyMessage', ['content'])

def fuzzy_match(query: str, target: str) -> bool:
    # Returns True if $query is a (potentially disjoint)
    # subset of $target.
    iq, it = 0, 0
    while iq < len(query) and it < len(target):
        iq += query[iq] == target[it]
        it += 1
    return iq == len(query)