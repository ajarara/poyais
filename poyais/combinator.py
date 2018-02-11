from poyais.utility import (
    LanguageNode, LanguageToken, node_from_iterable, what_is_linum_of_idx,
    len_of_token_or_node,)
from collections import namedtuple
from poyais.ebnf import ebnf_lexer
import re


# the fundamental parser unit is constructed from a tag
# and a regex identifying the tag.

# it is just a function that takes a string and returns
# a generator that yields a number of tagged matches:
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
    def parser(string, pos):
        if string.startswith(regex_string, pos):
            return match_type(tag, regex_string)
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
            if maybe is not None:
                out.append(maybe)
                idx += len_of_token_or_node(maybe)
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
            if maybe is not None:
                return maybe
        else:
            return None
    return parser


# parser -> parser -> Optional<Node>
def many_parser(parser):
    def p(string, pos):
        out = []
        idx = pos
        maybe = parser(string, pos)
        while maybe is not None:
            out.append(maybe)
            idx += len_of_token_or_node(maybe)
            maybe = parser(string, idx)
        return node_from_iterable(out)
    return optional_parser(p)


# parser -> parser
def optional_parser(parser):
    return or_parsers(parser, EMPTY_PARSER)


# parser -> parser
def group_parser(parser):
    return parser


EMPTY_PARSER = make_anonymous_matcher('empty', '')

COMBINATOR_MAP = {
    '|': or_parsers,
    ',': and_parsers,
}

GROUP_MAP = {
    '}': many_parser,
    ']': optional_parser,
    ')': group_parser
}

GROUP_COMPANIONS = {
    '{': '}',
    '(': ')',
    '[': ']'
}


def make_parser_from_terminal(rule, terminal, _cache={}):
    # this is the only time I can confidently cache a parser
    if terminal not in _cache:
        out = make_tagged_matcher('terminal', terminal)
        _cache[terminal] = out
        return out
    else:
        return _cache[terminal]


def flatten_parsers(rule, stack, curr_combinator):
    if curr_combinator:
        return COMBINATOR_MAP[curr_combinator](*stack)
    elif len(stack) == 1:
        return stack[0]
    else:
        raise AssertionError('TODO')


def delay_and_raise(parser_table, identifier):
    def parser(string, pos):
        print("identifier invoked")
        return LanguageNode(parser_table[identifier](string, pos))
    return parser


def dispatch(parser_table, rule, token_itr, sub_rule=None,
             comb_map=COMBINATOR_MAP, group_map=GROUP_MAP,
             group_comp=GROUP_COMPANIONS):
    stack = []
    curr_combinator = None
    while True:
        try:
            got = next(token_itr)
        except StopIteration:
            return flatten_parsers(
                rule, stack, curr_combinator)
        if got.type == 'terminal':
            stack.append(
                make_parser_from_terminal(rule, got.contents))
        elif got.type == 'EBNFSymbol':
            # now we have to dispatch on contents
            # this is the worst it'll get, I promise.
            contents = got.contents
            if contents in group_comp:
                stack.append(
                    dispatch(parser_table, rule, token_itr,
                             group_comp[contents]))
            elif contents == sub_rule:
                flattened = flatten_parsers(
                    rule, stack, curr_combinator)
                return group_map[sub_rule](flattened)
            elif contents in comb_map:
                if curr_combinator is None:
                    curr_combinator = contents
                elif curr_combinator != contents:
                    stack = [comb_map[curr_combinator](*stack)]
                    curr_combinator = contents
            else:
                raise AssertionError(
                    errmsg('improperly_nested', rule, contents, sub_rule))
        elif got.type == 'identifier':
            stack.append(delay_and_raise(parser_table, got.contents))


def make_parser_from_rule(parser_table, rule):
    return dispatch(parser_table, rule, iter(rule.tokens), {})


def make_parser_table(ebnf_string):
    out = {}
    for lexed_rule in ebnf_lexer(ebnf_string):
        out[lexed_rule.identifier] = make_parser_from_rule(out, lexed_rule)
    return out


def errmsg(err_name, *args):
    return {
        'lord_have_mercy': lambda rule, idx: "\n".join((
            "Rule {} contains an empty symbol. This isn't your",
            "fault, it's mine. Unless you're me.")).format(rule.lhs, idx),

        'improperly_nested': lambda rule, got, expected: "\n".join((
            "Improperly nested grouping operator in rule {}:",
            "Got: {}, Expected: {}")).format(rule.lhs, got, expected),

        'unexpected_grouping_op': lambda rule, got: "\n".join((
            "Unexpected grouping operator '{}' in rule: {}")).format(
                rule.lhs, got),

        'empty_grouping': lambda rule, sub_rule: "\n".join((
            "Rule {} contains an empty grouping ending with {}",)).format(
                rule.lhs, sub_rule),

        'unbounded_grouping': lambda rule, sub_rule: "\n".join((
            "Rule {} missing {}",)).format(rule.lhs, sub_rule),

        'bad_terminal_placement': lambda rule, terminal: "\n".join((
            "Rule {} contains two terminals in a row with no combinator",
            "separating them. Terminal triggering error: {}")).format(
                rule.lhs, terminal),

        'unknown_node': lambda program_string, idx, match: "\n".join((
            "Encountered unknown match: {} while parsing ({}, {})")).format(
                match, what_is_linum_of_idx(program_string, idx), idx)

        }[err_name](*args)
