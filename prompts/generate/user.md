## Command

`{{command}}`

## Syntax specification

```python
{{syntax_spec}}
```

## Value types and the values they stand for

```json
{{probe_values}}
```

## Bounds

- A repeatable argument may appear at most {{max_arity}} time(s).
- At most {{max_count}} optional elements may be combined in a single invocation. An optional
  element is any argument group whose arity is `?` or `*`: an optional flag, and also an
  optional operand such as a file argument the command can run without. So at a limit of 1, an
  invocation holds either one optional flag or one optional operand, never both; a mandatory
  operand (arity `1` or `+`) always appears and does not count. (This is the rule v1 enforces.)
- These flags are excluded entirely: {{skip_flags}}
- Standard input variation: {{stdin_variation}} — every `stdin` value must be one of: {{stdin_values}}.
- File content variation: {{content_variation}} — every file's `content` must be one of: {{content_values}}.
- `stdin` and `content` are required and may never be null.

## Now produce the output

One JSON object per line, in the format given above, for `{{command}}`.
