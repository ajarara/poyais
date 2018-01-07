# About

Poyais is the beginnings of a Scheme implementing [r7rs](r7rs.com) targeting the JVM written in Python.

# Why?

Why not?

# No really, why?

I went through BYOL, and gave up right before functions were implemented. I say it like that because it really wasn't Build Your Own Lisp, it was follow these instructions and try not to deviate much from them.

In particular, a parser combinator was given for free, most of the code was resistant to change, and any additions I made myself made lasting complication in terms of integrating the rest of the feature set.

# A couple notes for future me

It's a little strange to see r7rs mention scheme as never destroying lisp objects but having mutation in the language. What does destroy really mean here?

