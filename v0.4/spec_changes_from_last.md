# v0.4 Changes From v0.3

`v0.4` changes the execution model from a flat list of steps to a block-structured
program tree.

## Headline Change

New control-flow syntax:

```txt
Choose path
/DEF should_answer /TYPE bool

/IF @should_answer
/THEN Draft answer
/OUT concise answer
/END
```

## New Concepts

### Program AST

The parser now targets a program AST rather than a flat `List[Step]`.

Minimum node kinds for `v0.4`:

- `StepNode`
- `IfNode`

### Block Scope

`/IF ... /END` creates a block scope.

Variables defined inside the block are branch-local in `v0.4`.

This means:

- they can be used by later nodes inside the same block
- they are not visible after the matching `/END`

This rule is deliberate. It avoids branch-merging semantics until a later version.

## New Syntax

### `/IF`

Starts a conditional block.

Syntax:

```txt
/IF @flag
```

Rules:

- payload must be exactly one sigil-prefixed variable reference
- referenced variable must already exist
- referenced variable must be `bool` at runtime

### `/END`

Closes the nearest open `/IF` block.

Rules:

- stray `/END` is a parse error
- missing `/END` is a parse error

## `/THEN` Semantics

`/THEN` still starts a new step, but now it creates the next sibling step in the
current block.

So inside an `/IF`, `/THEN` starts the next step inside that `if` body.

## Nested Conditionals

Nested `/IF` blocks are allowed in `v0.4`.

## Execution Trace

Execution logs must distinguish at least:

- entered `if`
- skipped `if`
- executed step

## Explicitly Deferred

Not part of `v0.4`:

- `/ELSE`
- merged post-branch variable visibility
- loops
- arbitrary boolean expressions
- `break`, `continue`, or `return`
