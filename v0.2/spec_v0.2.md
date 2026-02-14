# DSL v0.2 Specification

## 1. Scope

This standard defines a lightweight, natural-language–first DSL for expressing **multi-step tasks** with:
- sequential control flow
- explicit variable binding    
- strict input restriction
- typed variable outputs
- structured model responses

The system is:
- general-purpose
- deterministic to parse
- nondeterministic at execution time (LLM-driven)

---

## 2. Core Concepts

### 2.1 Step
A **step** consists of:
1. Instruction text (natural language; required)
2. Zero or more commands    

The first step begins at the start of the document.

A new step begins when command `/THEN` appears as the first non-whitespace token on a line:

```
/THEN
```

---

### 2.2 Variable

A **variable**:
- Has a name matching:
    - letters and underscores
    - may contain digits        
    - may not begin with a digit
- Is referenced using a sigil (default: `@`)
- Persists across all subsequent steps
- May be overwritten by later steps

---
## 3. Step Structure

Within a step:
- Instruction text must appear first.
- Commands are prefixed with `/`.
- Indentation is cosmetic and has no semantic meaning (leading whitespace before commands is ignored).

---
## 4. Commands

Commands are lines whose first non-whitespace token is a command name (for example `/FROM`, `/DEF`, `/OUT`, `/THEN`).

### 4.1 `/FROM`

Declares which variables are accessible to the step.

**Syntax**
```
/FROM @var1, @var2, ...
```

Rules:
- Only variables are allowed in `/FROM` (no specific chat history or resources in v0.2).
- If `/FROM` is present:
    - The step may access only those variables.
- If `/FROM` is absent:
    - All chat history is accessible.
    - All existing variables are accessible.
- If instruction text or any `/AS` payload references `@var` not listed in `/FROM`, it is a **parse-time error**.
- If `/FROM` lists a variable not previously defined, it is a **parse-time error**.
    

---

### 4.2 `/DEF`

Declares a variable to be produced by the step.

**Syntax**

```
/DEF varname /TYPE type /AS description text ...
```
or with alternative ordering:
```
/DEF varname /AS description /TYPE type
```

A `/DEF` block may contain:
- At most one `/AS`
	- The payload provides a natural-language description of the value to be produced.
	- If `/AS` is omitted, defaults to varname

- At most one `/TYPE`
	- If `/TYPE` is omitted, defaults to `nat`
	- Allowed types in v0.2:
		- `nat` — natural-language string
		- `str` — exact string
		- `int` — integer
		- `float` — floating-point number
		- `bool` — boolean

The block ends when another command line begins (`/DEF`, `/FROM`, `/OUT`, `/THEN`, etc.) or at EOF.


---

### 4.3 `/OUT`

Describes the human-facing output intent. Describes what the model should reply.

**Syntax**

```
/OUT description text...
```

Rules:
- Multi-line allowed.
- If omitted, output is unconstrained.

---
## 5. Variable Interpolation

Let `FROM = {v1, ..., vn}` be the set of accessible variables.

Define a variable as **embedded** if `@vi` appears in:
- Instruction text
- Any `/AS` payload

Execution behavior:
- Embedded variables are replaced in-place with their values before sending the prompt to the model.
- Non-embedded variables listed in `/FROM` are automatically appended to the prompt in a generated “Inputs” section.

If a referenced variable is not allowed by `/FROM`, it is a parse-time error.

---

## 6. Model Response Contract

Each step must produce valid JSON.

Required keys:
- `error`
	- one of {0,1}
- `out`
	- natural-language text (`nat`)
	- must be a JSON string

If the step defines at least one `/DEF`, the response must also include variable outputs.

### Schema for variables

```json
{
  "error": 0,
  "out": "...",
  "vars": {
    "x": 55,
    "y": 660
  }
}
```

---
## 7. Error Semantics

### Parse-time errors
- Duplicate `/TYPE` in a `/DEF`
- Duplicate `/AS` in a `/DEF`
- Invalid variable name
- Referencing variable not in `/FROM`
- `/FROM` referencing undefined variable
- Unknown command

Parse-time errors prevent execution.

---
### Runtime errors

A step fails if:
- Model response is not valid JSON
- Required keys missing
- `error = 1`
- `out` is missing, null, or not a JSON string
- A `/DEF` variable is missing from response
- Variable fails type validation
    
On runtime error:
- Execution stops immediately.
- No variables from that step are committed.
- Partially produced values may be logged but not kept.

---

## 8. Type Validation Rules

Type is validated strictly against JSON types.

`out` is always `nat` in v0.2 and must be a JSON string.

### `int`
- Must be JSON number with no fractional part.
- `12.0` is invalid.
- Strings are invalid.

### `float`
- Must be JSON number.
- Integers are allowed (treated as floats).

### `bool`
- Must be JSON `true` or `false`.
    
### `nat`
- Must be JSON string.

### `str`
- Must be JSON string.

No deterministic conversions are performed in v0.2.

---

## 9. Variable Lifetime

- Variables persist across steps.
- Later `/DEF` may overwrite earlier variables.
- Only variables from previous steps may be referenced.
- Forward references are not allowed.

---

## 10. Missing Values

Missing or null values are runtime errors.

There is no optional type in v0.2.

---

## 11. Execution Model Summary

For each step:
1. Validate syntax.
    
2. Determine accessible variables via `/FROM`.
    
3. Perform interpolation for embedded variables.
    
4. Construct model prompt including:
    
    - Instruction text

	- Additional input variables
        
    - `/DEF` requirements
        
    - `/OUT` guidance
	
    - json output format description

5. Send instructions w/ json requirements and wait for return.
        
6. Check json formatting.
    
7. Validate variable types.
    
8. If `error = 0`, commit variables.
    
9. Otherwise stop execution.
