from poyais.combinator import (
    make_tagged_matcher, and_parsers, or_parsers, make_parser_from_rule
)
from hypothesis.strategies import text, lists, sampled_from
from poyais.utility import LanguageToken
from poyais.ebnf import ebnf_lexer
from hypothesis import given
import string
# import pytest


@given(text(alphabet=string.ascii_letters))
def test_make_parser_returns_fun_returns_match(literal_reg):
    func = make_tagged_matcher('foo', literal_reg)

    tm = func(literal_reg, 0)
    assert isinstance(tm, LanguageToken)
    assert tm.match == literal_reg


@given(text(alphabet=string.ascii_letters),
       text(alphabet=string.ascii_letters))
def test_and_parsers_joins_parsers(reg1, reg2):
    p1 = make_tagged_matcher('foo', reg1)
    p2 = make_tagged_matcher('bar', reg2)

    combined = and_parsers(p1, p2)
    language_tokens = combined(reg1 + reg2, 0)

    assert isinstance(language_tokens.value, LanguageToken)
    tok = language_tokens.value

    assert tok.tag == 'foo'
    assert tok.match == reg1

    next_tok = language_tokens.link.value

    assert next_tok.tag == 'bar'
    assert next_tok.match == reg2


@given(text(alphabet=string.ascii_letters),
       text(alphabet=string.ascii_letters))
def test_or_parsers_acts_as_either(reg1, reg2):
    p1 = make_tagged_matcher('foo', reg1)
    p2 = make_tagged_matcher('bar', reg2)

    func = or_parsers(p1, p2)
    tm1 = func(reg1, 0)
    # I think the fact that we have to check only startswith makes it
    # clear that if we've got an 'or' of parsers that aren't mutually
    # exclusive we won't try the second one if the first one succeeds.
    assert reg1.startswith(tm1.match)

    tm2 = func(reg2, 0)
    assert reg2.startswith(tm2.match)


WHITESPACE = (" ", "\t", "\n")

WHITESPACE_STRAT = sampled_from(WHITESPACE)


@given(lists(elements=WHITESPACE_STRAT, min_size=1))
def test_or_parser_acts_as_either_whitespace(ls):
    parsers = tuple(make_tagged_matcher('whitespace', tok) for tok in ls)
    p = or_parsers(*parsers)
    for space in ls:
        assert p(space, 0) is not None


@given(lists(elements=WHITESPACE_STRAT, min_size=1))
def test_and_parser_needs_all_whitespace(ls):
    p = and_parsers(
        *tuple(make_tagged_matcher('whitespace', tok) for tok in ls))
    assert p(''.join(ls), 0) is not None


def test_or_and_and_comb():
    # at this point I'm thinking it's probably a good idea
    # to write an anonymous parser. that'll make testing these
    # slightly less frictionless but more importantly
    # I could see their use in compound statements with arbitrary
    # syntax that we don't care about at the AST level
    p1 = make_tagged_matcher('flavor1', 'honey')
    p2 = make_tagged_matcher('flavor2', 'apple')
    p3 = make_tagged_matcher('end',     'pie')

    honeypie = and_parsers(p1, p3)
    applepie = and_parsers(p2, p3)
    anypie = or_parsers(honeypie, applepie)

    assert concat_tm_matches(honeypie('honeypie', 0)) == 'honeypie'
    assert concat_tm_matches(applepie('applepie', 0)) == 'applepie'

    assert concat_tm_matches(anypie('honeypie', 0)) == 'honeypie'
    assert concat_tm_matches(anypie('applepie', 0)) == 'applepie'


def test_and_or_or_comb():
    p1 = make_tagged_matcher('base', 'peach')
    p2 = make_tagged_matcher('avant_garde', 'broccoli')
    p3 = make_tagged_matcher('dessert', 'cobbler')
    p4 = make_tagged_matcher('plural', 'es')

    peach_or_broc = or_parsers(p1, p2)
    dessert_or_plural = or_parsers(p3, p4)

    yums = and_parsers(peach_or_broc, dessert_or_plural)

    for yummy in ('peachcobbler', 'broccolicobbler',
                  'peaches', 'broccolies'):
        assert concat_tm_matches(yums(yummy, 0)) == yummy


# now for the hard stuff
@given(lists(elements=WHITESPACE_STRAT, min_size=1))
def test_non_dependent_rule(ls):
    s = ''.join(ls)
    ex = tuple(ebnf_lexer(r'whitespace = "\n" | "\t" | " ";'))[0]
    d = {}
    parser = make_parser_from_rule(d, ex)
    assert parser(s, 0) is not None


def concat_tm_matches(tms):
    return ''.join(x.match for x in tms)
