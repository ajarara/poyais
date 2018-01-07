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
    # applies it to the string, and returns the section of it that it
    # consumes.
    # to the regex looking for a match

    reg = re.compile(regex_string)

    def parser(string):
        return reg.match(string)

    return parser


def and_parsers(parser1, parser2):
    def parser(string):
        maybe_match1 = parser1(string)
        if maybe_match1:
            # advance beyond the match
            maybe_match2 = parser2(string[maybe_match1.end():])
            if maybe_match2 is not None:
                return maybe_match1.group() + maybe_match2.group()

    return parser


def or_parsers(parser1, parser2):
    def parser(string):
        maybe1 = parser1(string)
        if maybe1:
            return maybe1.group()
        maybe2 = parser2(string)
        if maybe2:
            return maybe2.group()

    return parser
