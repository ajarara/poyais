# About

Poyais is the beginnings of a Scheme implementing [r7rs](https://r7rs.org) targeting the JVM written in Python.

# Why?

Why not?

# How?
Aim is to take an EBNF specification to a compiler. What is currently included is a relatively clean EBNF tokenizer and primitives to combine parsers.

What remains to be written is:
 - A routine to transform a set of tokenized rules derived from EBNF into a parser
 - A routine that transforms the output of a parser into an AST
 - A routine that transforms an AST into JVM bytecode
 
Here's an incomplete EBNF spec for scheme following ISO/EIC 14977
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
quoted_list = ( quote , "(" , ")" ) | ( quote, sexp ) ;
backquoted_list = ( backquote , "(" , ")" ) | ( backquote, sexp ) ;
```

Later on it might be necessary to define 'define' and 'syntax-rule' which would only require editing this spec. A scheme level reader macro seems unlikely, but it's definitely possible to extend syntax here as a substitute, provided the new definitions are handled in the AST generation code.

The parser should emit an AST. In the case of lisp, it's more convenient to flatten everything out, as the code representation is inherently tree like with clear context boundaries, but it's easy to take an AST and DFS it into a flat stream. The same cannot be said for all languages, where that information loss might change the semantics of the program.

# A couple notes for future me

It's a little strange to see r7rs mention scheme as never destroying lisp objects but having mutation in the language. What does destroy really mean here?

Just gonna rubber duck why I'm having issues on finishing the combinator.
- Have primitives like and, or, optional, grouping
- Tuples don't provide a good way to combine parsers. Instead, I should use a tree to relay results to callers, tagged with total length consumed so that subsequent parsers have the info they need to seek into the string.
- This changes the result of groups. We want to lift only these into their calling rules. We only key our tree by identifiers. 
- Currently, we take a group, and before returning it to the caller we glob it up into a single parser.
- This is probably fine, instead we want to reflect the ast in the returned data type. Which means wrapping only the calls to other identifiers in Nodes, everything else can be dropped.
