# About

Poyais is the beginnings of a Scheme implementing [r7rs](https://r7rs.org) targeting the JVM written in Python.

# Why?

Why not?

# How?
Aim is to take an EBNF specification to a compiler. What is currently included is a relatively clean EBNF tokenizer, and a parser combinator.

After finishing the combinator I've decided to put a hold on this project, perhaps permanently to experiment with Kotlin's type system. This implementation so far has most of the mental overhead of a type system with none of the benefits. 

Here's an incomplete spec for scheme following ISO/EIC 14977's definition of EBNF.
``` ebnf
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
sexp = "(" , [ whitespace ] , symbol , { whitespace , symbol }, [ whitespace ], ")" ;
quote = "'" ;
backquote = "`" ;
quoted list = ( quote , "(" , ")" ) | ( quote, sexp ) ;
backquoted list = ( backquote , "(" , ")" ) | ( backquote, sexp ) ;
```

Later on it might be necessary to define 'define' and 'syntax-rule' which would only require editing this spec. A scheme level reader macro seems unlikely, but it's definitely possible to extend syntax here as a substitute, provided the new definitions are handled in the AST generation code.

