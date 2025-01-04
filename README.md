# The Mistake Farm Programming Language

## Syntax

### General

1. The `randomize()` function runs a random line of code from the program. If it is used in an expression, it uses a random variable.

2. Identifiers cannot have characters that are a part of the Latin alphabet `[a-zA-Z]`.

3. The language is purely functional with no loops.

### Function Definition

Functions are defined using the `function` keyword. All functions are curried.

```markdown
variable (*+5) is function ? ! returns + open * ? ! close 5 close;
```

### Function Calls

Functions are called by placing the arguments within `open` and `close` blocks.

```markdown
?! open + 5 close;
?! open + 5 6 close;  comment Calls ?! with the result of + 5 6, and prints 11.
```

### Variable Declaration

Variables are declared using the `variable` keyword followed by the identifier and the `is` keyword.

```markdown
variable ?? is 5;
```

### Variable Assignment

Variables can only be assigned once. Reassigning a variable or using invalid identifiers is not allowed.

```markdown
variable ?? is 5;
* ?? 5;

comment The below isn't allowed. One name can only be used one time.
variable ?? is 6;

comment The below is also not allowed.
comment Identifiers must not contain characters from the Latin alphabet, to not confuse them with language constructs.
variable evil is string Hey, you can't do that! close;
```

### Arithmetic Operations

Arithmetic operations can be performed using `+`, `*`, and `/`.

```markdown
comment Adding numbers
+ 5 6;

comment Multiplying numbers
* 5 6;

comment Dividing numbers
/ 6 3;
```

### Comments

Comments terminate with a newline and are indicated by the `comment` keyword.

```markdown
comment This is a comment.
```

### Blocks

Blocks are defined using `open` and `close`.

```markdown
open
    variable ! is 5;
    + ! 6
close;
```

### Strings

Strings are defined using the `string` keyword and can accept up to one leading space.

```markdown
?! string Hello, world! What a great comment. close;
?! string  Hello, world! close;
```

### Impure Functions

Impure functions must be declared with the `impure` keyword.

```markdown
variable ?!(*+5) is impure function ? ! returns ?! open (*+5) close;
```