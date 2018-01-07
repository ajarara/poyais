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


def and_parsers(*parsers):
    def parser(string):
        out = []
        idx = 0
        for p in parsers:
            maybe = p(string[idx:])
            if maybe is not None:
                out.append(maybe)
                idx += len(maybe)
            else:
                return None
        return ''.join(out)
    return parser


def or_parsers(*parsers):
    def parser(string):
        for p in parsers:
            maybe = p(string)
            if maybe is not None:
                return maybe

    return parser

