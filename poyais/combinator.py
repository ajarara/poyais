from collections import namedtuple
# from poyais.ebnf import ebnf_lexer
from poyais.utility import memoize
import re


# the fundamental parser unit is constructed from a tag
# and a regex identifying the tag.

# it is just a function that takes a string and returns
# a generator that yields a number of tagged matches:

RuleMatch = namedtuple('LanguageToken', ('tag', 'match'))
UtilityMatch = namedtuple('UtilityToken', ('tag', 'match'))


def node_from_iterable(it):
    got = reversed(it)
    here = None
    for thing in got:
        here = Node(thing, here)
    return here


class Node:
    def __init__(self, value, link=None):
        self.value = value
        assert link is None or isinstance(link, Node)
        self.link = link

    def __iter__(self):
        here = self
        while here is not None:
            yield here.value
            here = here.link

    @memoize
    def __len__(self):
        return len(self.value) + (
            len(self.link) if self.link else 0)

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

# I think the trick behind MetaII is just reification of the parser
# into source code.  If this could be done then this'd be a way to
# generate compiler front ends, for any target language, provided it
# can be expressed in EBNF.


def _make_tagged_matcher(match_type, tag, regex_string):
    # build the regex, then return a function that takes a string,
    # applies the reg to the string, if it succeeds
    # return a tagged match with the tag and the string that matched.
    reg = re.compile(regex_string)

    def parser(string, pos):
        maybe = reg.match(string, pos)
        if maybe:
            return match_type(tag, maybe.group()),
    return parser


def make_tagged_matcher(tag, regex_string):
    return _make_tagged_matcher(RuleMatch, tag, regex_string)


def make_anonymous_matcher(tag, regex_string):
    "For internal use, just for optional_parser implementation"
    return _make_tagged_matcher(UtilityMatch, tag, regex_string)


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
                return ()
        return tuple(out)
    return parser


def or_parsers(*parsers):
    def parser(string, pos):
        for p in parsers:
            maybe = p(string, pos)
            if maybe:
                return maybe
        else:
            return ()
    return parser


# passes on 0 matches, see optional_parser
def many_parser(parser):
    def p(string, pos):
        out = []
        maybe = parser(string, pos)
        while maybe:
            out.append(maybe)
            maybe = parser(string, pos + len(maybe))
        return tuple(out)
    return optional_parser(p)


def optional_parser(parser):
    return or_parsers(
        parser,
        EMPTY_PARSER)


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


@memoize
def companion_complements(group_symbol, companions=frozenset('}])')):
    return companions.difference(group_symbol)


# this is one of those seams where we could transform this into an
# analog of MetaII.  instead of building runtime parsers, we could
# emit code that built these parsers after we did the case dispatch.
def make_parser(rule, parser_table, idx, sub_rule=False,
                combinator_map=COMBINATOR_MAP,
                group_companions=GROUP_COMPANIONS):
    stack = []
    dependencies = set()
    tokens = rule.rhs
    combinator_state = None
    while idx < len(tokens):
        tok = tokens[idx]
        if tok.type == 'EBNFSymbol':
            symbol = tok.contents
            assert symbol, _err_msg(
                'lord_have_mercy', rule, idx)
            if sub_rule is not None:
                assert symbol not in companion_complements(sub_rule), (
                    _err_msg('improperly_nested', rule, symbol,
                             group_companions[sub_rule]))

            if symbol in group_companions:
                moved, parser = make_parser(
                    rule, parser_table, idx + 1,
                    sub_rule=group_companions[symbol])
                idx = moved
                stack.append(parser)
            # if we've hit the end of our sub_rule, apply it
            # to our accumulated stack, return it to caller
            elif symbol == sub_rule:
                assert stack, (
                    _err_msg('empty_grouping', rule, sub_rule))
                if len(stack) == 1:
                    return idx, stack[0]
                return idx, Parser('arbitrary',
                                   combinator_map[combinator_state](*stack),
                                   dependencies)
            # at this point, we've handled all the grouping logic
            elif symbol == combinator_state:
                # defer joining the parsers on the stack
                # as late as possible (this reduces the number
                # of functions significantly)
                idx += 1
            elif combinator_state is None:
                combinator_state = symbol
                idx += 1
            elif symbol != combinator_state:
                stack.append(Parser(
                    'arbitrary',
                    combinator_map[combinator_state](*stack),
                    dependencies))
                idx += 1
                combinator_state = symbol
            else:
                assert False, "unreachable code. No context for you."
        elif tok.type == 'terminal':
            stack.append(
                # need to rethink some data types.
                make_matcher(tok.contents))
        elif tok.type == 'identifier':
            dependencies.add(tok.contents)
            # problem here... mutual recursion fails this.
            stack.append(parser_table[tok.contents])
        else:
            assert False, (
                "unreachable code again. This is a nonzero amount of context")


def _err_msg(err_name, *args):
    return {
        'lord_have_mercy': lambda rule, idx: "\n".join((
            "Rule {} contains an empty symbol. This isn't your",
            "fault, it's mine. Unless you're me.")).format(rule.lhs, idx),
        'improperly_nested': lambda rule, got, expected: "\n".join((
            "Improperly nested grouping operator in rule {}:",
            "Got: {}, Expected: {}")).format(rule.lhs, got, expected),
        'empty_grouping': lambda rule, sub_rule: "\n".join((
            "Rule {} contains an empty grouping ending with {}".format(
                rule.lhs, sub_rule)))
        }[err_name](*args)
