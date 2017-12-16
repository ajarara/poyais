

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
