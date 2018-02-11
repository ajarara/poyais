from combinator import make_parser_table
from utility import LanguageNode, LanguageToken

EBNF_SPEC = """
letter = "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j" | "k"
       | "l" | "m" | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v"
       | "w" | "x" | "y" | "z" | "A" | "B" | "C" | "D" | "E" | "F" | "G"
       | "H" | "I" | "J" | "K" | "L" | "M" | "N" | "O" | "P" | "Q" | "R"
       | "S" | "T" | "U" | "V" | "W" | "X" | "Y" | "Z" ;
digit = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
math symbol = "+" | "-" | "/" | "*" ;
whitespace = " " | "\t" | "\n" ;

character = letter | digit | math symbol ;
symbol = ( letter | math symbol ) , { character } ;
sexp = "(" , [ whitespace ], symbol , { whitespace , symbol },
     [ whitespace ], ")" ;

quote = "'" ;
backquote = "`" ;
quoted list = ( quote , "(" , ")" ) | ( quote, sexp ) ;
backquoted list = ( backquote , "(" , ")" ) | ( backquote, sexp ) ;
"""

LISP_PARSER_TABLE = make_parser_table(EBNF_SPEC)
