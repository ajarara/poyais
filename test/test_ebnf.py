from poyais.ebnf import Rule, split_into_rules, lex_rule, EBNFToken, EBNFSymbol


def test_rule_splitter():
    ex = """
    foo = 'bar', 'bat' | 'baz';
    """
    result = list(split_into_rules(ex))
    assert len(result) == 1
    assert result[0] == Rule('foo', "'bar', 'bat' | 'baz'")


def test_rule_lexer():
    rule = Rule('foo', """{ 'bar', "this" },\t"dance" |\nidentifier""")
    got = tuple(lex_rule(rule))
    for token in got:
        assert isinstance(token, EBNFToken)

    assert len(got) == 9
    # this feels brittle.
    for idx in (0, 2, 4, 5, 7):
        assert got[idx].type == EBNFSymbol
