from collections import namedtuple
from poyais.ebnf import ebnf_lexer
import re


# the fundamental parser unit is constructed from a tag
# and a regex identifying the tag.

# it is just a function that takes a string and returns
# a generator that yields a number of tagged matches:

Tagged_Match = namedtuple('Tagged_Match', ('tag', 'match'))


# to solve grouping, perhaps anonymous rules associated with a group
# built right before parser build time.
# the problem with this is that if we're building an AST 'keyed' by
# identifiers those groups will show up in the AST structure.
# I could just tag them as generated, and inline their results at parse time.

# hmm.. this complicates parser implementation slightly, as now I have
# to create add rules to the parser_table instead of just pointing to
# it from within the parser.

# an alternative I like better is to do recursive calls on groups,
# having them be aware of terminating identifiers like }, ], ) and
# returning.

# to solve an optional, a parser can be or'd with the empty parser
# ie something that always returns the empty string:
#    this idea I like less, but it certainly is simple, because if the
#    optional fails then the syntax is satisfied but doesn't actually
#    move through the token stream

# what about repeats?
# one idea is to take a list of parsers, and them, and continually
# apply the parser until there is no more output. One of the issues is
# nonzero repetition. How does EBNF handle a fixed number of rhs
# elements? I guess that's just a bunch of ands.

# I think the trick behind MetaII is just reification of the parser
# into source code.  If this could be done then this'd be a way to
# generate compiler front ends, for any target language, provided it
# can be expressed in EBNF.

class Node:
    def __init__(self, val, link=None):
        self.val = val
        self.link = link

    def __iter__(self):
        here = self
        yield here.val
        while here.link is not None:
            here = here.link
            yield here.val

    def deep_iter(self, _encountered=set()):
        out = [self.val]
        here = self.link
        while here is not None:
            if isinstance(here.val, Node):
                if here not in _encountered:
                    _encountered.add(here)
                    out.append(here.val.deep_iter(_encountered))
            else:
                out.append(here.val)
            here = here.link
        return tuple(out)


Parser = namedtuple('ResolvedRule', ('identifier', 'parser', 'dependencies'))


def resolve_rule(rule, parser_table):
    # we want to resolve the rule into a parser. this parser looks up
    # identifier parsers at parser time, from the parser_table
    return make_parser(rule, parser_table, 0)


def build_parser_from_lexed_rules(rules):
    parser_table = {}
    return parser_table


def make_tagged_matcher(tag, regex_string):
    # build the regex, then return a function that takes a string,
    # applies the reg to the string, if it succeeds
    # return a tagged match with the tag and the string that matched.
    reg = re.compile(regex_string)

    def parser(string, pos):
        match = reg.match(string, pos)
        if match:
            return (Tagged_Match(tag, match.group()),)
    return parser


def and_parsers(*parsers):
    def parser(string, pos):
        out = []
        idx = pos
        for p in parsers:
            maybe = p(string, idx)
            if maybe:
                for tagged_match in maybe:
                    out.append(tagged_match)
                    idx += len(tagged_match.match)
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
    def parser(string, pos):
        out = []
        maybe = parser(string, pos)
        while maybe:
            out.append(maybe)
            maybe = parser(string, pos + len(maybe))
        return tuple(out)
    return optional_parser(parser)


def optional_parser(parser):
    return or_parsers(
        parser,
        make_tagged_matcher('EMPTY', ''))


def group_parser(*parser):
    pass


COMBINATOR_MAP = {
    '|': or_parsers,
    ',': and_parsers,
    '}': many_parser,
    ']': optional_parser,
    ')': group_parser
}

GROUP_SYMBOLS = {'{', '[', '('}


# hmm.. this anonymous sub_rule extends well beyond groups

# brackets, optionals behave this way as well (in fact implementing
# groups once makes it easy to implement brackets, optionals
# on a subset of rules.


# this is one of those seams where we could transform this into an
# analog of MetaII.  instead of building runtime parsers, we could
# emit code that built these parsers after we did the case dispatch.
def make_parser(rule, parser_table, idx, sub_rule=False,
                combinator_map=COMBINATOR_MAP, group_symbols=GROUP_SYMBOLS):
    stack = []
    dependencies = {}
    tokens = rule.rhs
    combinator_state = None
    while idx < len(tokens):
        tok = tokens[idx]
        if tok.type == 'EBNFSymbol':
            if tok.contents in group_symbols:
                stack.append(
                    make_parser(rule, parser_table, idx + 1,
                                sub_rule=tok.contents))
            elif tok.contents == sub_rule:
                assert sub_rule, (
                    "Unmatched or improperly nested parentheses in rule: "
                    + rule.lhs)
                # we don't have to fail on single token groups, but this
                # makes implementation simpler.
                assert len(stack) > 1, (
                    "Empty or unnecessary group of size 1 in rule: "
                    + rule.lhs)
                assert combinator_state is not None, (
                    "No combinator directive (and, or) in group in rule: "
                    + rule.lhs)
                return Parser('arbitrary',
                              combinator_map[combinator_state](*stack),
                              dependencies)
            elif tok.contents == combinator_state:
                # simply ignore this
                idx += 1
        break
