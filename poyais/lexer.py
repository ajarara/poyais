import re


# this new lexer is a little sad
# it has no concept of lines
# it is difficult to extend
# it's unclear if tagging should be done here
# or at a later stage.
# it moves throughout the program_string irregularly
# and the only way to avoid this is to introduce some more state

# what would be great is the ability to
# record the location of the start of the token in the program
# and tag it.

# the only strangeness I see is in multiline strings
# I'll support them when Java does >:)


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
        # this bothers me slightly. first for if let
        # second this is a case where we move more than one.
        elif symbol_reg.match(program_string[pos:]):
            match = symbol_reg.match(program_string[pos:]).group()
            pos += len(match) - 1
            yield match
        elif char not in whitespace:
            raise ValueError(
                "Uncaught string at pos " + str(pos))
        pos += 1


def reader(filename):
    buf = []
    with open(filename, mode='r', encoding='utf-8') as program:
        for line in program:
            buf.append(program.readline().strip())
    return " ".join(buf).strip()
