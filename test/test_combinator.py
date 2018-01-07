from poyais.combinator import make_tagged_matcher, and_parsers, or_parsers
from hypothesis.strategies import text
from hypothesis import given
import string


@given(text(alphabet=string.ascii_letters))
def test_make_parser_returns_fun(literal_reg):
    func = make_tagged_matcher('foo', literal_reg)
    
    tm = func(literal_reg)
    assert len(tm) == 1
    assert tm[0].match == literal_reg


@given(text(alphabet=string.ascii_letters),
       text(alphabet=string.ascii_letters))
def test_and_parsers_joins_parsers(reg1, reg2):
    p1 = make_tagged_matcher('foo', reg1)
    p2 = make_tagged_matcher('bar', reg2)

    func = and_parsers(p1, p2)
    tms = func(reg1 + reg2)
    assert tms[0].match == reg1
    assert tms[1].match == reg2


@given(text(alphabet=string.ascii_letters),
       text(alphabet=string.ascii_letters))
def test_or_parsers_acts_as_either(reg1, reg2):
    p1 = make_tagged_matcher('foo', reg1)
    p2 = make_tagged_matcher('bar', reg2)

    func = or_parsers(p1, p2)
    tm1 = func(reg1)
    assert len(tm1) == 1
    assert reg1.startswith(tm1[0].match)

    tm2 = func(reg2)
    assert len(tm2) == 1
    assert reg2.startswith(tm2[0].match)
