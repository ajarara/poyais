from poyais.utility import (
    traverse, LanguageNode, LanguageToken,
    node_from_iterable,
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

    assert _search([1, 2, 3, 4], 3) == 2


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


def test_node_from_iterable_empty():
    assert node_from_iterable(()) is None


def test_node_from_iterable():
    matches = ('qux', 'quz', 'tmj')
    got = make_language_token_node('terminal', matches)
    here_idx = 0
    while got is not None:
        # this is pretty moot, we make it a language token
        # in our helper method call.
        assert isinstance(got.value, LanguageToken)
        assert got.value.match == matches[here_idx]
        here_idx += 1
        got = got.link


def test_traverse():
    matches = ('foo', 'bar')
    ex = make_language_token_node('tag', matches)

    got = traverse(ex)
    assert isinstance(got, list)
    for idx, hopefully_token in enumerate(got):
        assert isinstance(hopefully_token, LanguageToken)
        assert hopefully_token.match == matches[idx]


def test_traverse_on_AST():
    # we want depth first
    matches = (('+',), '5', '6')
    for match in matches:
        pass


def test_make_ast_from_iterable():
    got = make_ast_from_iterable('foo', (('lambda', '+'), '5', '3'))
    assert isinstance(got.value, LanguageNode)
    # just deeply check
    assert got.value.value.match == 'lambda'
    assert got.value.link.value.match == '+'  # :disappointed:
    assert got.link.value.match == '5'
    assert got.link.link.value.match == '3'


def test_make_ast_nested_empty():
    got = make_ast_from_iterable('bar', ('hey', ((),), 'moooooon'))
    assert got.value.match == 'hey'
    assert got.link.value.value is None
    assert got.link.value.link is None
    assert got.link.link.value.match == 'moooooon'
    assert got.link.link.link is None


def make_ast_from_iterable(tag, tokens, idx=0):
    if idx < len(tokens):
        curr = tokens[idx]
        # some implicit behavior here, if there's an empty
        # tuple it'll consider that None
        if isinstance(curr, tuple):
            # recurse into curr
            return LanguageNode(
                make_ast_from_iterable(tag, curr, 0),
                make_ast_from_iterable(tag, tokens, idx + 1))
        elif isinstance(curr, str):
            return LanguageNode(
                LanguageToken(tag, curr),
                make_ast_from_iterable(tag, tokens, idx + 1))


def make_language_token_node(tag, it):
    return node_from_iterable(
        tuple(LanguageToken(tag, match) for match in it))
