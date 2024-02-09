import pytest
import random

import risibot.util as util

N_RANDOM_TESTS = 100

def test_dummy_message():
    message1 = util.DummyMessage('', '')
    message2 = util.DummyMessage(content='Test', author=util.DummyAuthor(bot=True))
    assert message1.content == ''
    assert message2.content == 'Test'
    assert message2.author.bot

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

def test_extract_pattern_between():

    chars = "abcdefghijklmnopqrstuvwxyz"
    sepl = '{[<'
    sepr = '>]}'
    for _ in range(N_RANDOM_TESTS):
        nl, nr = random.choice(range(1, 10)), random.choice(range(1, 10))
        sepl = ''.join(random.choice(sepl) for _ in range(nl))
        sepr = ''.join(random.choice(sepr) for _ in range(nr))
        n_targets = random.choice(range(1, 10))
        query, words = "", []
        for _ in range(n_targets):
            current_sep, current_word = 1, ""
            while True:
                action = random.random()
                if action < .05: 
                    query += sepl if current_sep else sepr
                    current_sep = 1 - current_sep
                    if current_sep: break
                else:
                    new_c = random.choice(chars)
                    query += new_c
                    if not current_sep: current_word += new_c
            words.append(current_word)
        result = util.extract_pattern_between(query, sepl, sepr)
        print(query, sepl, sepr, result)
        for wi, ri in zip(words, result):
            assert wi == ri

if __name__ == "__main__":
    test_extract_pattern_between()