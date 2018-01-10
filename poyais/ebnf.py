from collections import namedtuple

# LETTER = re.compile("[a-zA-Z]")
# DIGIT = re.compile("[0-9]")

Rule = namedtuple('Rule', ('lhs', 'rhs'))
LexedRule = namedtuple('LexedRule', ('identifier', 'tokens'))


def dispatch_charwise(dispatch, ebnf_string, state):
    linum, idx = 0, 0
    for line in ebnf_string.split("\n"):
        # we increment before so that we correctly handle end of file easily
        while idx < len(line):
            maybe_result = dispatch(line, linum, idx, state)
            if maybe_result:
                yield maybe_result
            idx += 1
        idx = 0
        linum += 1


def split_into_rules(ebnf_string):
    # assigned is set when we've encountered an equal sign, but not a
    # terminator (semicolon). this lets us keep track of which side to
    # send characters to, and to expect an unquoted semicolon or an
    # unquoted equals
    state = {
        'assigned': False,
        'quoted': False,
        'lhs': [],
        'rhs': [],
    }
    return dispatch_charwise(_split_assignments, ebnf_string, state)


# it's a little strange to mutate our inputs and also output rules.
# well... a lot of this is strange.
def _split_assignments(line, linum, idx, state):
    deref = line[idx]
    if state['quoted']:
        assert state['assigned'], errmsg('lhs_quote', linum, idx)

        state['rhs'].append(deref)

        if deref == state['quoted']:
            state['quoted'] = False
    elif state['assigned']:  # we're on rhs
        assert deref != "=", errmsg('rhs_unquoted_equals', linum, idx)

        if deref == ";":
            # completed rule
            lhs, rhs = (''.join(state['lhs']).strip(),
                        ''.join(state['rhs']).strip())
            state['lhs'], state['rhs'] = [], []
            state['assigned'] = False
            return Rule(lhs, rhs)
        state['rhs'].append(deref)
    elif deref == '=':
        state['assigned'] = True
    else:
        assert deref != ";", errmsg('lhs_semicolon', linum, idx)
        state['lhs'].append(deref)


# our token types are
TERMINAL = "terminal"  # associated with literal contents
IDENTIFIER = "identifier"  # associated with literal contents
EBNFSymbol = "EBNFSymbol"  # associated with kind

#   EBNFSymbol (associated with kind)
# this could be improved on.
EBNFToken = namedtuple('EBNFToken', ['type', 'contents'])

EBNFSYMBOLS = frozenset('{[(|,)]}')
QUOTES = frozenset("'\"")


def lex_rule(rule, symbols=EBNFSYMBOLS, quotes=QUOTES):
    rhs = rule.rhs
    quoted = False
    got = []
    for char in rhs:
        if quoted:
            got.append(char)
            if char == quoted:
                quoted = False
                # verbatim, don't strip
                yield EBNFToken('terminal', ''.join(got))
                got = []
        elif char in quotes:
            quoted = char
            if got:
                maybe = "".join(got).strip()
                if is_valid_identifier(maybe):
                    yield EBNFToken('identifier', maybe)
                got = []
            got.append(char)
        elif char in symbols:
            if got:
                maybe = "".join(got).strip()
                if is_valid_identifier(maybe):
                    yield EBNFToken('identifier', maybe)
                got = []
            yield EBNFToken('EBNFSymbol', char)
        else:
            got.append(char)
    if got:
        assert not quoted, errmsg_rule('unquoted terminal', rule)
        yield EBNFToken('identifier', ''.join(got).strip())


def is_valid_identifier(string):
    return string and not string.isspace()


def errmsg(why, linum, idx):
    return {
        'lhs_quote':           "Quote character on left hand side at",
        'lhs_semicolon':       "Semicolon on left hand side at",
        'rhs_unquoted_equals': "Unquoted '=' on right hand side at",
    }[why] + " {}: {}".format(linum, idx)


def errmsg_rule(why, rule):
    return {
        'unquoted terminal':   "Rule contains an unquoted terminal",
    }[why] + ": {} - {}".format(*rule)


def ebnf_lexer(ebnf_string):
    for rule in split_into_rules(ebnf_string):
        yield LexedRule(rule.lhs, tuple(lex_rule(rule)))
