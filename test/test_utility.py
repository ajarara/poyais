from poyais.utility import memoize, build_idx_line_map
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
