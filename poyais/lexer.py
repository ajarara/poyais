import re


# maybe someday I'll add in support for brackets...
def lex(program_string, space_chars={'`', '(', ')', "'"}):
    # thank you norvig
    out = []
    for char in program_string:
        if char in space_chars:
            out.append(' ' + char + ' ')
        else:
            out.append(char)
    return "".join(out).split()

# now that's okay, but it doesn't support strings at all.
# instead we can explicitly define what tokens are, consume them
# and move on throughout the program.
# really the only thing that has state that must be preserved past
# whitespace is a string, and we delimit these by double apostrophes:
#
#   "
#
# so once we encounter these we'll search until the next unescaped string
# but this changes our norvig inspired lexer into an iterator

# the only long lived state that persists across line breaks are string_states.
# during input we'll strip newlines and carriage returns, so no big deal.


def lex(program_string,
        string_delim="'",
        token_chars={'`', '(', ')', "'"},
        whitespace={'\t', ' '},
        symbol_reg=re.compile(r"[a-zA-Z\-][a-zA-Z\-0-9]*")):
    pos = 0
    buf = []
    state_string = False
    state_escaped = False

    while pos < len(program_string):
        char = program_string[pos]
        if state_string:
            if char == '"':
                buf.append(char)
                if state_escaped:
                    state_escaped = False
                else:
                    state_string = False
                    yield "".join(buf)
                    buf = []
            elif char == "\\":
                if state_escaped:
                    buf.append(char)
                else:
                    state_escaped = True
            else:
                buf.append(char)
        elif char == '"':
            state_string = True
            buf.append(char)
        elif char == "\\":
            raise ValueError(
                "Backslash outside of string context at {}".format(pos))
        elif char in token_chars:
            yield char
        elif symbol_reg.match(program_string[pos:]):
            match = symbol_reg.match(program_string[pos:]).group()
            pos += len(match) - 1
            yield match
        elif char not in whitespace:
            raise ValueError(
                "Uncaught string at pos " + str(pos))
        pos += 1
