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
quoted list = ( quote , "(" , ")" ) | ( quote, sexp ) ;
backquoted list = ( backquote , "(" , ")" ) | ( backquote, sexp ) ;
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

## should we return linked lists generally from our parsers?
I think the answer is no. The only time we want to return (and expect) a Node is from a parse_table call. That should be an element in the output AST, but the others should be a tuple of tokens. 

That's... confusing. Now we have to do a type dispatch.

Well.. 


# case dispatch
Now the cases we must consider are when:
* We hit a terminal
  * Conditions we need:
    * We hit a terminal
  * What we do:
    * We wrap the terminal in a parser
    * Unset just_encountered\_combinator
    
* We hit a grouping start
  * Conditions we need:
    * Either there is nothing on the parser stack or we just encountered either "|" or ","
  * What we do:
    * We recurse, passing in the iterator we were passed, and expect to see a grouping end corresponding with the one we just saw.
    
* We hit a grouping end
  * Conditions we need:
    * Start corresponds to the end, groups are properly nested.
    * At least one parser on the stack
    * Either:
      * One parser on the stack, no combinator state
      * Many parsers on the stack, some combinator state
  * What we do:
    * If there is only one parser on the stack, just return it.
    * If there are many parsers on the stack, flatten them, return that.
    
* We hit a combinator
  * Conditions we need:
    * At least one parser on the stack
    * A parser after it (needs to be evaluated first)
    * just_encountered\_combinator is unset
  * What we do
    * If combinator_state is the same, set just\_encountered\_combinator
    * If combinator_state is None, set it,
    * If combinator_state is different (ie 'and' is state and we found 'or'), flatten the parsers on the stack wrt the combinator\_state, then set combinator\_state to be the new one

* we hit an identifier
  * Conditions we need:
    * We hit an identifier
  * What we do:
    * More complicated. We need to relay that this is a sub rule. One way is to tag the results of these so that later stages nest them. Alternatively we can just nest them immediately, but this approach is gonna be complicated. We could do this by wrapping our parsed rule in a utility token...
    

* we hit the end
  * What we need:
    * There's at least one parser on the stack.
    * Either:
      * Combinator_state is unset, there's only one parser on the stack
      * Combinator\_state is set, there's more than one parser on the stack
    * grouping_start is unset

# transformed results
Optionals and identfiers needing out of band matches seems inevitable. We can use them at parse time for results and filter them out at the top level.

Really we only need to filter out optionals. The identifiers we'd like to keep, because they are definitely useful for other stages of our compiler.

In any case, any parser returns a Node whose value is either a success or another Node. The link is always a Node, if it's not none.
