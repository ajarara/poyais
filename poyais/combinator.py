from collections import namedtuple
# from poyais.ebnf import ebnf_lexer
from poyais.utility import LanguageNode, node_from_iterable
import re


# the fundamental parser unit is constructed from a tag
# and a regex identifying the tag.

# it is just a function that takes a string and returns
# a generator that yields a number of tagged matches:

LanguageToken = namedtuple('LanguageToken', ('tag', 'match'))
UtilityToken = namedtuple('UtilityToken', ('tag', 'match'))


# an alternative I like better is to do recursive calls on groups,
# having them be aware of terminating identifiers like }, ], ) and
# returning to caller.

# to solve an optional, a parser can be or'd with the empty parser
# ie, something that always returns the empty string
# this parser should returns a match that is out of band, so that we can
# reliably filter it from output.


# what about repeats?
# one idea is to take a list of parsers, and them, and continually
# apply the parser until there is no more output. One of the issues is
# nonzero repetition. How does EBNF handle a fixed number of rhs
# elements? I guess that's just a bunch of ands.

def _make_tagged_matcher(match_type, tag, regex_string):
    # build the regex, then return a function that takes a string,
    # applies the reg to the string, if it succeeds
    # return a tagged match with the tag and the string that matched.
    reg = re.compile(regex_string)

    def parser(string, pos):
        maybe = reg.match(string, pos)
        if maybe:
            return LanguageNode(match_type(tag, maybe.group()))
    return parser


def make_tagged_matcher(tag, regex_string):
    return _make_tagged_matcher(LanguageToken, tag, regex_string)


def make_anonymous_matcher(tag, regex_string):
    "For internal use, just for optional_parser implementation"
    return _make_tagged_matcher(UtilityToken, tag, regex_string)


# Many<parsers> -> parser -> Optional<Node>
def and_parsers(*parsers):
    def parser(string, pos):
        out = []
        idx = pos
        for p in parsers:
            maybe = p(string, idx)
            if maybe:
                out.append(maybe)
                idx += len(maybe)
            else:
                # one of the parsers failed. Stop parsing,
                # fail the whole parser.
                return None
        return node_from_iterable(out)
    return parser


# Many<parsers> -> parser -> Optional<Node>
def or_parsers(*parsers):
    def parser(string, pos):
        for p in parsers:
            maybe = p(string, pos)
            if maybe:
                return maybe
        else:
            return None
    return parser


# parser -> parser -> Optional<Node>
def many_parser(parser):
    def p(string, pos):
        out = []
        maybe = parser(string, pos)
        while maybe:
            out.append(maybe)
            maybe = parser(string, pos + len(maybe))
        return node_from_iterable(out)
    return optional_parser(p)


# parser -> parser
def optional_parser(parser):
    return or_parsers(
        parser,
        EMPTY_PARSER)


# parser -> parser
def group_parser(parser):
    return parser


EMPTY_PARSER = make_anonymous_matcher('Empty', '')

COMBINATOR_MAP = {
    '|': or_parsers,
    ',': and_parsers,
    '}': many_parser,
    ']': optional_parser,
    ')': group_parser
}

GROUP_COMPANIONS = {
    '{': '}',
    '(': ')',
    '[': ']'
}


def companion_complements(group_symbol, group_companions=GROUP_COMPANIONS,
                          companions=frozenset('}])')):
    return companions.difference(group_companions(group_symbol))


def make_parser_from_terminal(rule, terminal, state, _cache={}):
    if state['just_encountered_combinator']:
        state['just_encountered_combinator'] = False
    elif state['beginning']:
        state['beginning'] = False
    else:
        errmsg('bad_terminal_placement', rule, terminal)

    # this is the only time I can confidently cache a parser
    if terminal not in _cache:
        out = make_tagged_matcher('terminal', terminal)
        _cache[terminal] = out
        return out
    else:
        return _cache[terminal]


def start_grouping(rule, token_itr, group_type, state):
    state['sub_rule'] = GROUP_COMPANIONS[group_type]
    while True:
        try:
            dispatch(rule, token_itr, state)
        except StopIteration:
            errmsg('unbounded_grouping', rule, state['sub_rule'])


def dispatch(*args):
    pass


def errmsg(err_name, *args):
    return {
        'lord_have_mercy': lambda rule, idx: "\n".join((
            "Rule {} contains an empty symbol. This isn't your",
            "fault, it's mine. Unless you're me.")).format(rule.lhs, idx),

        'improperly_nested': lambda rule, got, expected: "\n".join((
            "Improperly nested grouping operator in rule {}:",
            "Got: {}, Expected: {}")).format(rule.lhs, got, expected),

        'empty_grouping': lambda rule, sub_rule: "\n".join((
            "Rule {} contains an empty grouping ending with {}",)).format(
                rule.lhs, sub_rule),

        'unbounded_grouping': lambda rule, sub_rule: "\n".join((
            "Rule {} missing {}",)).format(rule.lhs, sub_rule),

        'bad_terminal_placement': lambda rule, terminal: "\n".join((
            "Rule {} contains two terminals in a row with no combinator",
            "separating them. Terminal triggering error: {}")).format(
                rule.lhs, terminal),

        }[err_name](*args)
