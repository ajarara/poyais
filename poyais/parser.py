from collections import namedtuple
import re

# given a stream of tokens, tag them
# the fact that I identify these by regs mean
# that I should probably write a parser combinator
# because I used regs in the lexer
# and the lexer must be updated in tandem with the parser
# to add new language features.

# but there's definitely value in doing this by hand. I think.
RegTokenPairing = namedtuple('RegTokenPairing', ['reg', 'symbol_type'])


def buildPairing(reg, symbol_type):
    return RegTokenPairing(re.compile(reg), symbol_type)


TYPES = (
    buildPairing(r'^\($', 'open_paren'),
    buildPairing(r'^\)$', 'close_paren'),
    buildPairing("^'$", 'single_quote'),
    buildPairing("^`$", 'backtick'),
    buildPairing('^"[^"]*"$', 'string'),  # does this match the empty string?
    buildPairing(r"[a-zA-z\-][a-zA-z\-0-9]*", 'lisp_symbol'),
)

TokenSymbolPairing = namedtuple('TokenSymbolPairing', ['token', 'symbol_type'])


def parse(lexical_stream):
    for lexical_token in lexical_stream:
        for pairing in TYPES:
            if pairing.reg.match(lexical_token):
                yield TokenSymbolPairing(lexical_token,
                                         pairing.symbol_type)
                continue
