from poyais.combinator import (
    make_tagged_matcher, and_parsers, or_parsers, make_parser_from_rule,
    make_parser_table, many_parser, UtilityToken, EMPTY_PARSER
)
from hypothesis.strategies import text, lists, sampled_from
from poyais.ebnf import LexedRule, Rule, lex_rule
from poyais.utility import LanguageToken, LanguageNode
from hypothesis import given
import pytest
import string
# import pytest


@given(text(alphabet=string.ascii_letters))
def test_make_parser_returns_fun_returns_match(literal_reg):
    tag = 'foo'
    func = make_tagged_matcher(tag, literal_reg)

    tm = func(literal_reg, 0)
    assert isinstance(tm, LanguageToken)
    assert tm.match == literal_reg
    assert tm.tag == tag


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


# don't.. don't feed many_parser the empty parser.
@pytest.mark.skip("sadness")
@given(text(alphabet=string.ascii_letters, min_size=1))
def test_many_parser(word):
    # why is there an infinite loop here when hypothesis tests but
    # manual tests work?
    p1 = make_tagged_matcher('word', word)
    many = many_parser(p1)
    assert many(word + word + word, 0) is not None


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


def test_non_dependent_grouped_rule():
    rule = make_lexed_rule('groupd', '( "this", " and ", "that") | "neither"')
    parser = make_parser_from_rule({}, rule)
    assert parser("this and that", 0) is not None
    assert parser("neither", 0) is not None


@given(text(alphabet=string.ascii_letters + string.digits))
def test_empty_parser(s):
    for idx in range(len(s)):
        got = EMPTY_PARSER(s, idx)
        assert got is not None
        assert isinstance(got, UtilityToken)
        assert got.tag == 'empty'
        assert got.match == ''


# now for the hard stuff
@given(lists(elements=WHITESPACE_STRAT, min_size=1))
def test_non_dependent_rule(ls):
    s = ''.join(ls)
    rule = make_lexed_rule('whitespace', '"\n" | "\t" | " "')
    parser = make_parser_from_rule({}, rule)
    assert parser(s, 0) is not None


def test_simple_optional_rule_success():
    parser = make_parser_from_rule_string('["bicycle"]')
    got = parser("bicycle", 0)
    assert got is not None
    assert isinstance(got, LanguageToken)
    assert got.match == "bicycle"


@pytest.mark.skipped("Problem with optional parser")
def test_simple_optional_rule_failure():
    parser = make_parser_from_rule_string('["bicycle"]')
    got = parser("something else", 0)
    assert got is not None
    assert isinstance(got, UtilityToken)
    assert got.tag == 'empty'


@pytest.mark.skip("waiting on simpler rule")
def test_additional_optional_rule():
    parser = make_parser_from_rule_string('["optionally: "], "here"')
    got = parser("optionally: here", 0)
    assert got is not None
    assert isinstance(got, LanguageNode)
    assert str(got) == 'optionally: here'
    got2 = parser("here", 0)
    assert got2 is not None
    assert isinstance(got2, LanguageNode)
    assert str(got2) == 'here'


def test_identifiers():
    spec = """
        simple = "w", "o", "r", "d";
        complex = { simple };
    """
    parser_table = make_parser_table(spec)
    assert str(parser_table['simple']('word', 0)) == 'word'
    assert str(parser_table['complex']('wordword', 0)) == 'wordword'


def test_make_parser_table():
    rules = "this = 't' | 'h' | 'i' | 's';"
    table = make_parser_table(rules)
    assert 'this' in table
    this_p = table['this']
    
    assert this_p('t', 0)
    assert this_p('h', 0)
    assert this_p('i', 0)
    assert this_p('s', 0)
    assert this_p('w', 0) is None


def concat_tm_matches(tms):
    return ''.join(x.match for x in tms)


def make_lexed_rule(identifier, rule_as_string):
    return LexedRule(identifier, lex_rule(Rule(identifier, rule_as_string)))


ARBITRARY_TAG = 'arbitrary'


def make_parser_from_rule_string(rule_string, tag=ARBITRARY_TAG):
    rule = make_lexed_rule(tag, rule_string)
    return make_parser_from_rule({}, rule)
