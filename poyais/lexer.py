import re


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
        # second 
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
        buf.append(program.readline().strip())
    return " ".join(buf).strip()
