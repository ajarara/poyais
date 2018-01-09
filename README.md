# About

Poyais is the beginnings of a Scheme implementing [r7rs](r7rs.com) targeting the JVM written in Python.

# Why?

Why not?

# How?
Aim is to take an EBNF specification to a compiler. What is currently included is a relatively clean EBNF tokenizer and primitives to combine parsers.

What remains to be written is:
 - A routine to transform a set of tokenized rules derived from EBNF into a parser
 - A routine that transforms the output of a parser into an AST
 - A routine that transforms an AST into JVM bytecode


# A couple notes for future me

It's a little strange to see r7rs mention scheme as never destroying lisp objects but having mutation in the language. What does destroy really mean here?

