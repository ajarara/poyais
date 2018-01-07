from poyais.ebnf import split_into_rules, Rule


def test_rule_splitter():
    ex = """
    foo = 'bar', 'bat' | 'baz';
    """
    result = list(split_into_rules(ex))
    assert len(result) == 1
    assert result[0] == Rule('foo', "'bar', 'bat' | 'baz'")
