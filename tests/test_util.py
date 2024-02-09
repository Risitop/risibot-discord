import pytest
import random

import risibot.util as util

N_RANDOM_TESTS = 100

def test_dummy_message():
    message1 = util.DummyMessage('')
    message2 = util.DummyMessage('Test')
    assert message1.content == ''
    assert message2.content == 'Test'

def test_fuzzy_match_arguments():
    # Test invalid arguments
    with pytest.raises(TypeError):
        util.fuzzy_match()
    with pytest.raises(TypeError):
        util.fuzzy_match('a')
    with pytest.raises(TypeError):
        util.fuzzy_match(1337, 42)

def test_fuzzy_match_algorithm_set_cases():
    # Test expected results
    assert util.fuzzy_match('', '') # Trivial case
    assert util.fuzzy_match('', 'a')
    assert not util.fuzzy_match('a', '')
    assert not util.fuzzy_match('a', 'b')
    assert util.fuzzy_match('chsrb', 'chaos orb')
    assert not util.fuzzy_match('Chsrb', 'chaos orb') # Case sensitive
    assert not util.fuzzy_match('chsrrb', 'chaos orb')
    assert util.fuzzy_match('mirror', 'mirror')
    assert util.fuzzy_match('chaos', 'chaos orb')
    assert util.fuzzy_match('chaos', 'orb chaos')
    assert util.fuzzy_match('ababab', 'abaabaaabababaaab')
    assert util.fuzzy_match('aaaa', 'aaaaa')
    assert not util.fuzzy_match('aaaaa', 'aaaa')

def test_fuzzy_match_algorithm_random_cases():
    # Test random cases results

    chars = "abcdefghijklmnopqrstuvwxyz"

    # Positive cases
    for _ in range(N_RANDOM_TESTS):
        query = ''.join([random.choice(chars) for _ in range(20)])
        target = ""
        nq = 0
        while nq < len(query):
            if random.random() < .2:
                target += query[nq]
                nq += 1
            else:
                target += random.choice(chars)
        assert util.fuzzy_match(query, target)

    # Negative cases
    for _ in range(N_RANDOM_TESTS):
        query = ''.join([random.choice(chars) for _ in range(20)])
        target = ""
        nq = 0
        for _ in range(50):
            if random.random() < .2:
                target += random.choice(query)
            else:
                target += random.choice(chars)
        assert not util.fuzzy_match(query, target)