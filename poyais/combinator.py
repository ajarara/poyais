from functools import reduce
import re


# from string import Formatter isn't particularly useful
# or at least not immediately useful.
DEPENDENT = re.compile('{(\S+)}')


# this provides a native syntax to declare what non terminals depend on
# changing dependent will break existing regs, which is a problem.
def get_format_dependencies(string, delim=DEPENDENT):
    for match in delim.finditer(string):
        yield match.groups()


# first we need to represent a parser:
# this should be transparent to end users (ie me)
# all parsers operate on a stream,
# if they cannot 'advance' the stream then they don't return
# if they can, they return the string they matched.
# ideally this should be enough to compose them easily.


def make_parser_from_reg(regex_string):
    # build the regex, then return a function that takes a string,
    # applies it to the string, and returns the consumed string
    reg = re.compile(regex_string)

    def parser(string):
        maybe_match = reg.match(string)
        if maybe_match:
            return maybe_match.group()
    return parser


def and_parsers(parser1, parser2):
    def parser(string):
        maybe_match1 = parser1(string)
        if maybe_match1 is not None:
            maybe_match2 = parser2(string[len(maybe_match1):])
            if maybe_match2 is not None:
                return maybe_match1 + maybe_match2
    return parser


def or_parsers(parser1, parser2):
    def parser(string):
        maybe_match1 = parser1(string)
        if maybe_match1 is not None:
            return maybe_match1
        maybe_match2 = parser2(string)
        if maybe_match2 is not None:
            return maybe_match2
    return parser


def and_parsers_variadic(*parsers):
    # what do we do on the empty list of parsers?
    return reduce(and_parsers, parsers)


def or_parsers_variadic(*parsers):
    return reduce(or_parsers, parsers)
