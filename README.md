# The Mistake Language

## Overview

Mistake is an imperative, functional, object-oriented, message-passing language.
Through the use of human language, it is easy to write for beginners.

All language constructs are in the user's language because it makes programs self-documenting and readable. This document is in American English.

## Core data types

These are some core data types:

* `function`
* `string`
* `number`

Users can also create classes.

In Mistake, all numbers are double precision floating point numbers.

# Syntax reference

## Meta-syntax

Note that keywords must be translated to the user's preferred language. In this document, we assume American English.

`blah` matches `blah`, but also `Blah` and `bLaH`. All keywords are case-insensitive in Mistake.

`[blah]` also matches blah

`[blah]?`  matches blah or nothing

`[blah]...` matches one or more blah s in between spaces

`[blah]?...` matches zero or more blahs in between spaces

`<something>` is a class of character
For the avoidance of doubt, a character is a Unicode grapheme.

## Classes of characters

* <identifier> is any character that is not whitespace or in the Latin alphabet (a to z). Identifiers must contain at least one non-numeric character to distinguish them from number literals.
    * `-67.42!` is an identifier.
    * `-67.42` is a number.
    * `67.42.128.6` is an identifier, not an invalid number.
* `<expression>` is, well, an expression.
* `<string>`  is a set of characters. See the specific syntax element for what the string is terminated by.
* `<lifetime>` is a number that ends in s, l or u (meaning seconds, lines and a timestamp respectively).
    * Timestamps are given in milliseconds since Jan 1, 2020 (which is the Mistake epoch).
* Anything else refers to another syntax element.

## Lines

A "line" is one statement in the imperative section.

## Comments

Comments end at the end of a line (at a `\n`).

Comments may exist anywhere. Comment bodies may contain anything.

Comments are simply ignored.

```
comment <string>
```

## Statements

An entire Mistake file is just a set of statements. A top-level statement is said to be in the "imperative section".

```
[<statement>]...?
```

### Expression statements

A statement can be an expression terminated by end. Whatever the expression returns is simply discarded.

```
<expression> end
```

### Class statements

Classes are impure.

```
class [<identifier>] [inherits <identifier>]? has [<statement>]...? end
```

### Variable statement

public is only valid in a class statement.

[public] variable <identifier> [lifetime <lifetime>]? [type <string>] is <expression> end

### Jump statements

Note that jump statements are only valid in the imperative section.

```
jump <expression> <expression> end
```

## Expressions

### Functions

```
[impure] function [<identifier>]... returns <expression> close
```

### Open blocks

```
open [<statement>]...? <expression> close
```

### Function application

```
<identifier> <expression>
```

Note that `; 1 2 3 4` is `;(1)(2)(3)(4)`, not `;(1(2(3(4)))`.

### String expressions

String expressions are terminated with close. This means that string expressions can't have "close" in them.

```
string <string> close
```

Strings in Mistake can have escape sequences. For familiarity, Mistake uses a familiar syntax for escape sequences:

```
string Bits &amp; bytes close
```

Note that Mistake strings may contain arbitrary bytes.

```
string Bits &#0; bytes close
```

### Match expressions

```
match <identifier> cases [case <expression> then <expression>]...? otherwise <expression> close
```

### Member expressions

member <identifier> of <identifier>

### New expressions

new <identifier>

### Unit expressions

```
unit
```

### Number literal

A number literal is a number like `-6` or `420.68` or `82`.

## Builtin functions

Functions that don't return anything return unit.

Operators

* `+`, `-`, `/`, `*` are math operations.
    * For numbers, they do what you expect.
    * For strings:
        * `+`  joins them together.
        * `-`  does nothing.
        * `/`  divides the string (e.g `/ string Hello close 5`  is "H").
        * `*`  multiplies the string (e.g `* string Hello close 5`  is "HelloHelloHelloHelloHello").
    * For lists, it does the same as strings.
    * For everything else, it does nothing.
* `=`, `≠` are equals and not equals
* `>`, `<`, `≥`, `≤` do what you expect them to:
    * `>`  evaluates to true if its second argument is greater than its first
    * `<`  evaluates to true if its second argument is less than its first
    * `≥`  evaluates to true if its second argument is greater than or equal to its first
    * `≤`  evaluates to true if its second argument is less than or equal to its first
* `->` gets the "length" of something.
    * For strings, it is the length of the string in bytes.
    * For match objects, it is the amount of matches.
    * For numbers, it is the length of the number printed out in Base 10.
    * For unit, it is 0.
    * For lists, it is the length of the list.
    * For tasks, it is the amount of seconds the task has been running.
    * And so on. For things which don't have an obvious "length", it is 0.
* `??` formats something as a string, like `?!` does.

Other functions

* `?!` prints its only argument. Impure.
* `!` creates a mutable box.
    * `?`  gets the contents of a mutable box.
    * `<`  sets them. Impure.
* `!=!`  creates a channel.
    * `<<`  writes to a channel. Impure.
        * If the argument passed is not a channel, it does nothing.
    * `>>` reads from a channel, blocking and returning what it got. Also impure.
        * If the argument passed is not a channel. it returns unit.
* `|>|` pushes its only argument to the stack. Impure.
* `|<|` pops the top of the stack and calls its argument with the value. Where there is no value, the function does nothing. Impure.
* `!!` asserts that a value is truthy (not `false` or `unit`). If the value is not truthy, crashes the program.
* `[/]` runs a callback in an amount of seconds. Returns a task object. When killed before the callback has run, the callback is never run. When killed while the callback is running, the callback is killed. Note that Mistake uses decimal seconds.

## Networking

All networking functions are impure.

* `<=#=>` creates a TCP server. `<=?=>` creates a UDP server.
    * `==>#` binds the server to the port set by its argument. Returns `true` if successful and `false` otherwise.
    * `==>?` binds the server to the hostname set by its argument. Returns `true` if successful and `false` otherwise.
    * `==>!` sets the server's callback. 
        * Returns a task object representing the server. When it is killed, the server stops listening and any existing server callbacks are killed.
        * For TCP servers, the server callback is called asynchronously with a TCP socket object. Callbacks may be impure.
        * For UDP servers, the server callback is called asynchronously with a string object containing the message content. Callbacks may be impure.
* `<=#=` creates a TCP socket. `<=?=` creates a UDP socket.
    * If a connection could not be made, returns `unit` instead.
    * `<<` on a TCP and UDP socket sends a string. Blocking.
        * Returns `true` if successful and `false` otherwise.
    * `>|<` closes the socket on both TCP and UDP sockets.
    * `>>` on TCP sockets receives a string. **Blocking**. On a UDP socket, does nothing.

## The basics of Mistake

### Terminology

The "imperative section" is the top-level of a file. Each statement is evaluated individually, one after the other.
See the syntax reference for details.

### Types

Mistake has a few datatypes:

* number
* string
* boolean
* unit (which is like null/None/undefined/etc)

Comments

```
comment Comments terminate with a newline.
sylw Wrth gwrs, gallwch chi siarad eich iaith eich hun os yw'n defnyddio'r wyddor Ladin.
comment The interpreter should check the user's locale.
```

### Functions

To call a function in Mistake, just write the function name and then its parameters.

```
+ 5 6 end  comment Is 11.
```

### Variables

```
variable ?? is 5 end
?! ?? end  comment Prints 5. ?! prints its argument to the console.
```

In Mistake, variables can only be assigned to once.

```
variable ?1 is 5 end
variable ?1 is 6 end  comment Throws a compilation error.
```

`_` is a special identifier. You can assign to it multiple times:

```
variable _ is 5 end
variable _ is 6 end
```

However, you can't use it as a normal variable. It discards whatever is written to it.

```
?! _  comment Throws a compilation error.
```

### Open / close statements

Open blocks create a new scope. The last expression in an open block is returned from the block.

```
variable 5+6 is open
  variable ! is 5 end
  
  comment The last thing is returned.
  comment So, the last thing does not have an "end" after it.
  + ! 6
close end

?! 5+6 end
?! !  comment Throws a compilation error, because ! isn't in this scope!
```

### Function application

In Mistake, all functions are curried.
For example, `+ 5` returns a function that, when called with a number, will add 5 to it and return it.

```
variable +5 is + 5 end

comment The below prints 11.
?! open +5 6 close end
```

### Strings and string manipulation

For example:

```
comment The below prints "Hello, world! What a great comment."
?! string Hello, world! What a great comment. close end
```

Note that you can't write "close" in a string.
Luckily, Mistake supports escape sequences.

```
?! open + string Please clos&#101; the door. close end
```

You can use other mathematical operations with strings too:

```
?! open * string Hello close 5 end  comment This print HelloHelloHelloHelloHello
?! open / string Hello close 5 end  comment This prints H
```

### Variable lifetimes

Mistake has lifetimes. You can specify how long a variable lasts in either seconds or lines.

```
variable ??2 lifetime 20s is 5 end          comment lasts for 20 seconds
variable ??3 lifetime 1l is 5 end           comment lasts for 1 line

comment Lasts until 2069.
comment Timestamps are given in milliseconds relative to the Mistake epoch,
comment which is January 1, 2020.
comment Note that Mistake uses decimal seconds.
variable ??4 lifetime 1343656342u is 5 end

comment Trying to access an expired variable crashes the program.
?! ??3 end  comment Crashes - it expired 1 line ago.
```

### Defining new functions

In Mistake, functions are just values.
You can use the function keyword to create one. Here's a function that discards its only parameter and returns 5:

```
function _ returns 5 close
```

You can write curried functions like this:

```
function $1 $2 returns 5 close
```

Which is syntactic sugar for:

```
function $1 returns function $2 returns 5 close close
```

Assign functions to variables to use them again later.

```
comment JavaScript does this, so it must be good.
comment (*+5) takes two numbers, multiplies them together and adds 5.
variable (*+5) is function ? ! returns + open * ? ! close 5 close end

comment Impure functions must say "impure".
comment Otherwise, they must have no side effects.
comment This is so that the compiler can theoretically apply theoretical optimisations to theoretical functions.
variable ?!(*+5) is impure function ? ! returns ?! open (*+5) close close end
```

### The stack

In order to present a familiar interface to those coming from stack-based languages, Mistake provides a global stack.

```
comment Trying to get closer to hardware implementations, you are able to use a "stack" to run functions as well.
comment "push" is a function that pushes the parameter onto the top of the stack
comment "stack" is a function that takes in a function, and calls said function with the data at the top of the stack.
comment "stack" also removes the data from the top of the stack.

comment Pushes 5 onto the stack, then 7.
|>| 5 end
|>| 7 end

comment Adds 7 and 5
?! |<| |<| + end

comment Multiplies 5 and the data at the top of the stack
comment As there is no data, the multiplication function will simply not be called in order to soften your mistake
|<| * 5 end
```

Note that the stack may only be used in impure functions.

### Jumps

In Mistake, there are no imports.
However, you can jump to lines of other programs.
Here's a file:

```
comment This is utils.mistake

variable (&&) is 5 end

comment jump can only be used at the top-level, in the imperative section.
jump $<" $<? end
```

And another file:

```
comment This is main.mistake

comment [?] is a function that, when called, returns the current line.
variable $<" is string main.mistake end
variable $<? is + open [?] unit close 1 end
jump string utils.mistake close end

comment Okay, utils.mistake should've jumped back now.
?! (&&)  comment Prints 5
```

Jumps may only be used in the imperative section.

> Note that different Mistake programs may use different calling conventions.

Lines in Mistake are different to what you may expect them to be.
In Mistake, a "line" is anything that ends in "end". An entire class definition is one "line". A comment is not a line.
For example:

```
open 
  ?! open [?] unit close end comment Prints 1
  ?! open [?] unit close end comment Still prints 1
  ?! open [?] unit close end comment We're still on line 1!
close end
```

Lines start from 1.

### Pattern matching

```
variable # is 5 end

comment The below prints "# is 5 :)".
?! match # cases
  comment @ is what is being matched on.
  comment Each case statement is evaluated and cast to a boolean.
  comment Note that everything that is not either "false" or "unit" is truthy.  

  case = 5 @ then string # is 5 :) close
  otherwise string # is not 5 :( close
close end
```

### Channels and asynchronous programming

Mistake supports asynchronous programming for building Web Scale:tm: applications. 
Let's create a channel:

```
variable [] is !=! end

You can send a message to a channel with <<.

<< [] 5 end
```

However, our message is simply lost. If nothing is listening on the channel, Mistake will just discard the message. Let's write a function to listen to messages on the channel with <<:

```
variable <[] is function _ open
  variable $ is << [] end
  ?! $ end
  <[] unit end
close end
```

If we called this function now, the program would hang forever as `<<` simply waits for a new message indefinitely. Let's instead run this function asynchronously, with `<+>`.

```
variable ?< is open <+> <[] close end
```

`<+>` returns a task object that we can later cancel. Mistake will wait for all tasks to complete before exiting, so if we don't cancel the task it will simply hang forever. If we run the statement from earlier:

```
<< [] 5 end  comment Prints 5 to the screen!
```

5 will be printed to the screen! Now that our task has served its purpose, we can kill it with `!+!`.

```
!+! ?< end
```

### Typing

Some programmers feel that types make programming easier. Luckily, the built in Mistake type solver can figure out most of your types.

```
variable ? is + 5 6 end
```

The built-in type solver would infer `?` as being a number. You can state this explicitly:

```
variable ? type number is + 5 6 end
```

However, type hints are just for you. They aren't checked at runtime.

### Mutable boxes

Sometimes you want mutability. That's fine. Use `!` to create a mutable box:

```
variable [] is ! 5 end  comment Creates a mutable box with initial value 5
```

Use `?` and `<` to read and write to a mutable box respectively:

```
?! open ? [] close end  comment Prints 5
< [] 6 end              comment Sets the box's content to 6
?! open ? [] close end  comment Now prints 6
```

Note that `<` is impure.

### Classes

Mistake is an enterprise language, which is why it has classes. Here's a simple counter class:

```
class #++ has
  variable [#] is 0 end

  public variable ++ is impure function $ returns open
    comment I can access my class variables here!

    comment Add $ to the counter:
    < [#] open + open ? [#] close $ close end

    comment And return it:
    ? [#]
  close close end
 end
```

Create a new instance of it with `new`:

```
variable [#] is new #++ end  comment We can reuse [#] because class creates a new scope
```

And access members on it with `member ... of ...`

```
member ++ of [#] 55 end

?! member [#] of [#] end  comment Can't do this -- isn't public variable
```

Classes can also be subclassed:

```
class 5++ inherits #++ has
  public variable +5 is impure function _ returns open
    comment Still can access all of #++'s variables
    ++ 5
  close close end
end
```

### Web Scale™

Mistake supports building highly scalable web applications with green threading.

```
variable =#= is <=#=> unit end

comment Listen on localhost:8080, aborting if that port is taken already.
!! open ==># =#= 8080 close end
!! open ==>? =#= string localhost close close end

==>! impure function <=> returns open
  ?! open << <=> close end
  >> <=> string Fuck off close end
  >!< <=>
close close end

comment Close the server in 10 decimal seconds, or about eight normal seconds
[/] 10 function _ returns open
  !+! <=> end
close close end

comment Mistake will wait for all tasks to complete before shutting down.
```

### Parsing

Mistake supports regex. The `/?/` function can be used to search through a string.

```
variable <> is /?/ string /^Hello (\w+)?/ close string Hello, Sarah! close end
?! "" end  comment Prints "matchlist"
```

Use `/>/` to get the nth match of a matchlist, starting from `1`.

```
variable "" is />/ <> 1 end
?! "" end  comment Prints "match"
```

Because there were no more than `1` match, `/>/ <> 2` would return unit.
Use `/>"/` to get the string that was matched.

```
?! open />"/ "" close end comment Prints "Hello, Sarah"
```

Use `/>?/` to get a specific capture group, or unit if no such capture group exists or was not matched. Again, starts from 1.

```
?! open />?/ 1 close end comment prints "Sarah"
```

You can also search for binary values.

```
variable <0> is /?/ string &#0; close string /\x00/ close end
```