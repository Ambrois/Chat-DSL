# DSL v0.4 Draft

## 1. Scope

`v0.4` keeps the `v0.3` step semantics and typed outputs, but changes the language
from a flat sequence of steps into a block-structured program.

The main new feature is conditional execution with nested blocks.

## 2. Core Execution Model

A DSL document parses into a `Program` containing ordered nodes.

Minimum node kinds:

- `StepNode`
- `IfNode`

Each node has:

- a stable node id
- a start line number
- node-specific payload

## 3. Step Nodes

A `StepNode` preserves the existing `v0.3` step behavior:

- instruction text is required
- `/FROM`, `/DEF`, and `/OUT` remain step-local directives
- typed variable validation is unchanged

## 4. If Nodes

### Syntax

```txt
/IF @flag
/THEN first guarded step
/THEN second guarded step
/END
```

### Meaning

If the referenced boolean variable is `true`, execute the child block.

If it is `false`, skip the child block.

## 5. Control-Flow Rules

### 5.1 `/IF`

- must appear where a node can begin
- payload must be exactly one sigil-prefixed variable reference
- variable must already be visible at that point in the program

### 5.2 `/END`

- closes the nearest open `/IF`
- unmatched `/END` is a parse error
- EOF with any unclosed `/IF` is a parse error

### 5.3 `/THEN`

- starts a new sibling step inside the current block
- at top level, it behaves like `v0.3`
- inside an `/IF`, it starts the next step inside that conditional body

## 6. Visibility Rules

`v0.4` uses strict block-local visibility for conditional branches.

Variables defined:

- before an `/IF` are visible inside it
- inside an `/IF` are visible to later nodes in that same block
- inside an `/IF` are not visible after `/END`

This is a semantic rule, not just a runtime convention.

## 7. Runtime Rules

When executing an `IfNode`:

1. resolve the guard variable from the current context
2. require the runtime value to be a boolean
3. execute child nodes only when the value is `true`
4. do not leak branch-local variables to the outer scope

## 8. Trace Requirements

Execution logs must be rich enough to show:

- node kind
- source line
- whether a node executed or was skipped
- for `if` nodes, the evaluated guard and branch decision

## 9. Deferred Features

The following are intentionally out of scope for `v0.4`:

- `/ELSE`
- branch merging
- loop nodes
- expression evaluation
- condition combinators like `AND` or `OR`
