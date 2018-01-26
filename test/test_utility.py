from poyais.utility import (
    memoize, build_idx_line_map, _search, what_is_linum_of_idx,
    Linum)
from hypothesis.strategies import text
from hypothesis import given


def test_build_idx_line_map():
    example = """
    Here's a place where I'd like a sorted listing of all line breaks
    in this string.  This way, given an index, I can bisect into it
    and get a quick answer to where in this program is my index,
    instead of having to seek through each time which is unbelievably
    expensive.

    That was an empty line, but it should've shown up.
    """
    for pos in build_idx_line_map(example):
        assert example[pos] == "\n"


@given(text())
def test_build_idx_line_map_generally(passed):
    for pos in build_idx_line_map(passed):
        assert passed[pos] == "\n"


# this demonstrates that there's no cache invalidation set up but
# this shows that it works programmatically
# another way would be to tag things but now everything using memoize has to be
# aware of memoize
# instead the restriction is you should only memoize on immutable values
def test_memoize_caches():
    state = {
        'network': 'up'
    }

    @memoize
    def potentially_expensive_network_request(key):
        return state[key]

    assert potentially_expensive_network_request('network') == 'up'
    state['network'] = 'down :('
    assert potentially_expensive_network_request('network') == 'up'


def test__search():
    assert _search([], 9543) == 0

    assert _search([15], 14) == 0
    assert _search([15], 30) == 1

    assert _search([1, 2, 3, 4], 3) == 1


def test_end_to_end_what_is_linum():
    example = (
        "Here's a line",
        "Here's another",
        "Here's an empty line coming up",
        "",
        "Isn't that great?")
    full = "\n".join(example)

    assert what_is_linum_of_idx(full, 0) == Linum(1, 0)
    assert what_is_linum_of_idx(full, 15) == Linum(2, 2)
