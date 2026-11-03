# Basic Dignified: ZX-81

Language support and build tasks for ZX-81 BASIC and Basic Dignified.

Configure `zx81-basic-dignified.badigPath` with the path to this installation's `badig.py`. The default task converts `.DZX` to `.AZX` and `.p`; the run task launches EightyOne using the path in `zx81/emulator_interface.ini`.

The `.p` output is binary and is not associated with a text grammar.

## Setup and Tasks

Install the included VSIX and configure `zx81-basic-dignified.badigPath`. Set `zx81-basic-dignified.pythonInterpreter` if your Python command is not `python`. Copy the supplied `.vscode/tasks.json` into your program workspace's `.vscode` folder.

- **Convert to ASCII:** convert unnumbered `.DZX` to `.AZX` without tokenization.
- **Convert and Tokenize:** convert unnumbered `.DZX` to `.AZX` and `.p` (default build).
- **Convert, Tokenize and Run:** convert `.DZX` and open the `.p` in EightyOne.
- **Classic: Tokenize Only / Tokenize and Run:** tokenize a numbered `.AZX` without Dignified conversion, optionally launching EightyOne.

The Dignified tasks also accept numbered listings in `.DZX` files, including Go81 `p2txt` output: jump targets become labels and a renumbered `.AZX` is generated, then tokenized, without modifying the source. Computed jump targets cannot be renumbered; use a classic task on an `.AZX` copy for those.

## Literal Bytes and Go81 Listings

Both `.DZX` and `.AZX` support `\{XX}` for one literal byte, with exactly two hexadecimal digits in either case. Escapes work in code, strings, and `REM`; they do not change string or comment state. Invalid escapes report the line number.

Valid hexadecimal escapes have a dedicated `constant.character.escape.hex` highlighting scope in code, strings and `REM`, taking precedence over Dignified labels. Both uppercase and lowercase hex digits are accepted.

## Snippets

`for-next`, `print-at`, `loop-label`, `if-goto`, `remtags` and `remx`. The `remx <line>,<count>[,<byte>]` command creates a long `REM` line for machine code, filled with the character `0` by default.

```basic
600 REM \{D8}\{D8}\{D8}END OF GAME\{D8}\{D8}\{D8}
```

Use the classic task for numbered Go81 `p2txt` listings. If a number is immediately followed by `\{7E}`, provide the marker and all five hidden numeric bytes explicitly, for example `0\{7E}\{81}\{00}\{00}\{00}\{00}`. Full `.p` file identity is not guaranteed because the tokenizer rebuilds the system and data areas.

See the [module guide](../../documentation/MODULE_TOOLS.md#zx-81-usage-and-byte-escapes), [installation guide](../../documentation/INSTALLATION.md), and [editor integration guide](../../documentation/IDE_TOOLS.md) for details.