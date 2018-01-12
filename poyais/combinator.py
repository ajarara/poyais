from collections import namedtuple
from poyais.ebnf import ebnf_lexer
import re


# the fundamental parser unit is constructed from a tag
# and a regex identifying the tag.

# it is just a function that takes a string and returns
# a generator that yields a number of tagged matches:

LanguageToken = namedtuple('LanguageToken', ('tag', 'match'))


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


Parser = namedtuple('Parser', ('identifier', 'parser', 'dependencies'))


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
            return (LanguageToken(tag, match.group()),)
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
        make_tagged_matcher('EMPTY', ''))


def group_parser(parser):
    return parser


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


def companion_complements(group_symbol, _cache={},
                          _companions=frozenset('}])')):
    if group_symbol not in _cache:
        _cache[group_symbol] = _companions.difference(group_symbol)

    return _cache[group_symbol]


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
