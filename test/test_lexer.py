from poyais.lexer import lex


def test_empty_exp():
    empty = ""
    assert list(lex(empty)) == []


def test_lambda_exp():
    lambda_exp = "(lambda () nil)"
    assert list(lex(lambda_exp)) == ["(", "lambda", "(", ")", "nil", ")"]


def test_quoted_list():
    quoted_exp = "'()"
    assert list(lex(quoted_exp)) == ["'", "(", ")"]

    quasi_quoted_exp = "`()"
    assert list(lex(quasi_quoted_exp)) == ["`", "(", ")"]
