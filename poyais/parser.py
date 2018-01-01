from collections import namedtuple
import re

# given a stream of tokens, tag them
# the fact that I identify these by regs mean
# that I should probably write a parser combinator
# because I used regs in the lexer
# and the lexer must be updated in tandem with the parser
# to add new language features.

# but there's definitely value in doing this by hand. I think.
# an extension to this that I should definitely consider is associating a token
# with the line and character it starts at.
# this allows me to pinpoint parse errors
RegTokenPairing = namedtuple('RegTokenPairing', ['reg', 'symbol_type'])


# I deliberated abstracting away 'match the whole token' by wrapping
# the reg in '^' and '$'. It's a reasonable idea, especially since
# I've got this built already and am not going to use it outside of
# the context of building token recognization.  but I decided against
# it, because it breaks nested tokens.

def buildPairing(reg, symbol_type):
    return RegTokenPairing(re.compile(reg), symbol_type)


# one of the things that bothers me is that using a tuple means
# that I can't reliably test individual elements
# except by going by their indices. That is, if I wanted to test what
# is parsed into an open_paren, I'd have to index into this tuple.
TYPES = (
    buildPairing(r'^\($', 'open_paren'),
    buildPairing(r'^\)$', 'close_paren'),
    buildPairing("^'$", 'single_quote'),
    buildPairing("^`$", 'backtick'),
    buildPairing('^"[^"]*"$', 'string'),  # does this match the empty string?
    buildPairing(r"^[0-9]+$", 'number'),
    buildPairing(r"[a-zA-z\-0-9]+", 'lisp_symbol'),
)

TokenSymbolPairing = namedtuple('TokenSymbolPairing', ['token', 'symbol_type'])


def parse(lexical_stream):
    for lexical_token in lexical_stream:
        yield parse_token(lexical_token)


def parse_token(lexical_token):
    for pairing in TYPES:
        if pairing.reg.match(lexical_token):
            yield TokenSymbolPairing(lexical_token,
                                     pairing.symbol_type)
            continue
