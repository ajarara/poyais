from poyais.combinator import make_parser_from_reg, and_parsers, or_parsers
from hypothesis.strategies import text
from hypothesis import given
import string


@given(text(alphabet=string.ascii_letters))
def test_make_parser_returns_fun(literal_reg):
    func = make_parser_from_reg(literal_reg)
    assert func(literal_reg)


@given(text(alphabet=string.ascii_letters),
       text(alphabet=string.ascii_letters))
def test_and_parsers_joins_parsers(reg1, reg2):
    p1 = make_parser_from_reg(reg1)
    p2 = make_parser_from_reg(reg2)

    got = and_parsers(p1, p2)(reg1 + reg2)

    assert (got == '' and reg1 == '' and reg2 == '') or got


@given(text(alphabet=string.ascii_letters),
       text(alphabet=string.ascii_letters))
def test_or_parsers_acts_as_either(reg1, reg2):
    either_empty = (reg1 == '' or reg2 == '')
    p1 = make_parser_from_reg(reg1)
    p2 = make_parser_from_reg(reg2)

    got1 = or_parsers(p1, p2)(reg1)
    assert (got1 == '' and either_empty) or got1

    got2 = or_parsers(p1, p2)(reg2)
    assert (got2 == '' and either_empty) or got2
