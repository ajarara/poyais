from collections import namedtuple
from ebnf import ebnf_lexer
import re


# the fundamental parser unit is constructed from a tag
# and a regex identifying the tag.

# it is just a function that takes a string and returns
# a generator that yields a number of tagged matches:

Tagged_Match = namedtuple('Tagged_Match', ('tag', 'match'))


# to solve grouping, perhaps anonymous rules associated with a group
# built right before parser build time.

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


def resolve_rule(rule):
    # we want to generate a parser from a series of EBNFTokens
    # if the token we're looking at is an identifier, then
    # we construct a Node that is the value.
    pass


def build_parser_from_lexed_rules(rules):
    parser_table = {}
    return parser_table


def make_tagged_matcher(tag, regex_string):
    # build the regex, then return a function that takes a string,
    # applies the reg to the string, if it succeeds
    # return a tagged match with the tag and the string that matched.
    reg = re.compile(regex_string)

    def parser(string):
        match = reg.match(string)
        if match:
            return (Tagged_Match(tag, match.group()),)
    return parser


def and_parsers(*parsers):
    def parser(string):
        out = []
        idx = 0
        for p in parsers:
            maybe = p(string[idx:])
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
    def parser(string):
        for p in parsers:
            maybe = p(string)
            if maybe:
                return maybe
        else:
            return ()
    return parser
