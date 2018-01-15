from poyais.ebnf import Rule, split_into_rules, lex_rule, EBNFToken, EBNFSymbol
from poyais.ebnf import TERMINAL, IDENTIFIER


def test_rule_splitter():
    ex = """
    foo = 'bar', 'bat' | 'baz';
    """
    result = list(split_into_rules(ex))
    assert len(result) == 1
    assert result[0] == Rule('foo', "'bar', 'bat' | 'baz'")


def assert_all_tokens(tokens):
    for token in tokens:
        assert isinstance(token, EBNFToken)


def assert_indices_all(tokens, ebnf_type, indices):
    for idx in indices:
        assert tokens[idx].type == ebnf_type


def test_rule_lexer():
    rule = Rule('foo', """{ 'bar', "this" },\t"dance" |\nidentifier""")
    got = tuple(lex_rule(rule))
    assert len(got) == 9

    # this feels brittle.
    assert_all_tokens(got)
    assert_indices_all(got, EBNFSymbol, (0, 2, 4, 5, 7))


def test_rule_lexer_real_use_case():
    rule = Rule('whitespace', '" " | "\t" | "\n"')
    got = tuple(lex_rule(rule))
    assert len(got) == 5

    assert_all_tokens(got)
    assert_indices_all(got, TERMINAL, (0, 2, 4))
    assert_indices_all(got, EBNFSymbol, (1, 3))


def test_rule_identifier_whitespace():
    rule = Rule('character', """letter | digit | math symbol""")
    got = tuple(lex_rule(rule))
    assert len(got) == 5

    assert_all_tokens(got)
    assert_indices_all(got, IDENTIFIER, (0, 2, 4))
    assert_indices_all(got, EBNFSymbol, (1, 3))

    for idx in (1, 3):
        assert got[idx].contents == "|"
