# About

Poyais is the beginnings of a Scheme implementing [r7rs](r7rs.com) targeting the JVM written in Python.

# Why?

Why not?

# No really, why?

I went through BYOL, and gave up right before functions were implemented. I say it like that because it really wasn't Build Your Own Lisp, it was follow these instructions and try not to deviate much from them.

In particular, a parser combinator was given for free, most of the code was resistant to change, and any additions I made myself made lasting complication in terms of integrating the rest of the feature set.

# A couple notes for future me
Java handles the funargs problem by making inner classes (analogous to closures) depend only on final variables outside of their scope, so that when they are returned, the class can be self contained on the stack without having to keep track of references. 

How does this guarantee that references between stack frames are cohesive, that modifying one through a reference guarantees the modification is visible from somewhere else that also has that reference?

``` java
final Integer foo = new Integer(10);  // Integer is boxed, so mutable
class Foo {
    public Integer foo_assignment;
    Foo () {
        foo_assignment = foo;
    }
}
class Bar {
    public Integer bar_assignment;
    Bar () {
        bar_assignment = foo;
    }
}
```

Now when this compiles what we conceptually get is:
``` java
class Foo {
    public integer foo_assignment;
    Foo () {
        foo_assignment = new Integer(10);
    }
}

class Bar {
    public integer bar_assignment;
    Bar () {
        bar_assignment = new Integer(10);
    }
}
```

But this isn't the same meaning. Am I wrong?



It's a little strange to see r7rs mention scheme as never destroying lisp objects but having mutation in the language. What does destroy really mean here?

