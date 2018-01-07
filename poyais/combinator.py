from collections import namedtuple
import re


# the fundamental parser unit is constructed from a tag
# and a regex identifying the tag.

# it is just a function that takes a string and returns
# a generator that yields a number of tagged matches:

Tagged_Match = namedtuple('Tagged_Match', ('tag', 'match'))

# from string import Formatter isn't particularly useful
# or at least not immediately useful.
DEPENDENT = re.compile('{(\S+)}')


# given a string like this:
# r'\({sexp}+'
# this provides a native syntax to declare what non terminals depend on
# changing dependent will break existing regs, which is a problem.
def get_format_dependencies(string, delim=DEPENDENT):
    for match in delim.finditer(string):
        yield match.groups()



# we can break down any expression into its dependencies
# and literal matches (like parens, backticks, etc)
# the problem here is that a bunch of lisp syntax rides regex syntax
# so we need to identify what are regs and what are actual tokens
# ie arithmetic, parens are the big culprits here.

# we'll be using ebnf, particularly 
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
