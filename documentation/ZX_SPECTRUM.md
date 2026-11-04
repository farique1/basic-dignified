# ZX Spectrum module - v1.4.0 preview

This is an **addition** to Fred Rique's original Basic Dignified
documentation. The original MSX/CoCo manuals and suite version (2.2.1)
are preserved. The Spectrum module has its own version and is being
developed incrementally in the `suporte-zx-spectrum` branch of
`wilsonpilon/basic-dignified`.

## Status and scope

### Milestone 1.4.0

Dignified assignments now insert LET at the beginning of a statement,
after a colon or after THEN. Classic `-asc` input still requires explicit LET.
Scalar `+=`, `-=`, `*=`, `/=`, `^=`, `++`, `--` are lowered with a parenthesized
right operand, preserving precedence. Strings support only `+=`.
Array/slice compound targets are rejected instead of evaluating an index twice.
Use explicit assignments for them.

`?` is PRINT. `[?](row,column)` expands to `PRINT AT row,column;`;
the parameter order is Sinclair row/column, not MSX LOCATE x/y.
FUNC/RET use the existing Dignified GO SUB/RETURN lowering with LET inserted
for parameter and result transfers. Parameters/results are global variables,
not local stack frames; this does not add recursive-local semantics.
See [functions.DSP](../examples/zxspectrum/functions.DSP).

Additional native commands/modifiers: AT, TAB, FLASH, BRIGHT, INVERSE, OVER,
PLOT, DRAW, CIRCLE, POKE and CLEAR.
These additions supersede the corresponding baseline limitations below.

### Milestone 1.3.0

Adds DIM, numeric/string arrays and slices, string scalar variables,
DATA expressions, READ, RESTORE, RANDOMIZE and native numeric/string
functions (including RND, PI, LEN, STR$, CHR$, VAL, CODE, trigonometric
functions, PEEK and USR). Functions retain Sinclair semantics.
DEF FN/FN and BIN are not included in this milestone.

Numeric scalars retain long alphanumeric names. String variables, arrays
and FOR/NEXT controls require a single letter (plus `$` for strings).
Use explicit DECLARE aliases for long Dignified names in these categories,
for example `DECLARE title:n` followed by `LET title$="SPECTRUM"`.
Aliases are shared across uses of that declared base name, as in the
original DECLARE mechanism; there is no silent truncation/automatic allocator.

String arrays follow the ROM's fixed-length rules: the last dimension
is the string length, not an extra freely sized string element.
Numeric scalars and arrays of the same letter may coexist in Sinclair BASIC.
See [data.DSP](../examples/zxspectrum/data.DSP).
These additions supersede the corresponding baseline limitations below.

### Milestone 1.2.0

The user manually confirmed that v1.1.0 `hello.tap` loads in EightyOne,
LIST is correct and RUN prints the expected counter and DONE. This is
user-reported emulator validation, not an automated execution test.

Version 1.2.0 adds standard-speed TZX 1.20 output (block 0x10,
1000 ms pauses), alongside unchanged default TAP output. Use
`--tk_format tap`, `--tk_format tzx` or `--tk_format both`.
INI `format` and remtag `TK_FORMAT` accept the same values.
Each tape file is replaced atomically; writing both files is not a
transaction across the pair.

New commands: BORDER, INK, PAPER, PAUSE, BEEP, INPUT, GO SUB/GOSUB,
RETURN, FOR/NEXT, TO and STEP. Use a single-letter FOR control variable.
See [colours.DSP](../examples/zxspectrum/colours.DSP).
The following sections describe the original 1.1.0 baseline; this
milestone extends that subset and supersedes its TZX/loop limitations.

Version **1.1.0** is the first functional milestone, not complete Sinclair
BASIC support. It targets the **ZX Spectrum 48K with the English ROM**.
It converts Dignified source to a numbered listing and optionally creates
a standard ROM-loadable **TAP**. The first example prints a counter three
times using a jump label.

Implemented:

- `PRINT`, explicit `LET`, `IF ... THEN GO TO`, `GO TO`/`GOTO`, `REM`,
  `CLS`, `STOP`.
- Numeric expressions using `+ - * / ^`, comparisons, `AND`, `OR`, `NOT`
  and parentheses. Sinclair semantics apply, not MSX bitwise semantics.
- Long **alphanumeric numeric scalar names**, without the MSX two-character
  aliasing limit. Names are case-insensitive in the Spectrum ROM.
- Labels, DEFINE macros, explicit DECLARE aliases and INCLUDE through
  the shared Dignified pipeline.
- Quoted text, doubled quotes within a string, and the PRINT apostrophe
  separator (newline). An apostrophe is **not** a Spectrum REM.
- TRUE = 1 and FALSE = 0.
- Decimal and scientific literals, five-byte Sinclair numbers, numbered
  BASIC records, TAP header/data blocks and XOR checksums.
- Existing common options such as line start/step and reports.

Not implemented in this preview:

- TZX, autorun, `--em_run` or automatic emulator control.
- String variables, arrays, FOR/NEXT, DATA/READ, DEF FN, Dignified FUNC/RET.
- The remaining native commands/functions, including graphics and sound.
- Implicit LET, compound assignment, the `[?](row,column)` shortcut.
- UDG/graphics escapes, snapshots, a Spectrum DignifieR or editor packages.

Unsupported native words are rejected rather than advertised as working.
The tokenizer is not a complete Sinclair syntax checker: errors in supported
expressions can still be reported by the ROM when the program runs.

## Installation

Use the source archive or clone the Spectrum branch of the fork.
Keep `badig.py`, `support`, `msx` and `zxspectrum` together: the new module
reuses the existing MSX class scaffolding, but overrides the active dialect
and does **not** use MSX tokenization.

The suite's Python 3.8+ requirement is unchanged; no Python packages need
to be installed. Python 3.14 was used for this milestone's automated checks.

From the repository root:

```powershell
python -B badig.py -id zxspectrum --spectrum-version
python -B badig.py -id zxspectrum -h
python -B badig.py examples\zxspectrum\hello.DSP -id zxspectrum --tk_tokenize -rh -ca
```

Outputs:

- `hello.ASP`: numbered classic Sinclair BASIC listing.
- `hello.tap`: tokenized program in a standard tape container.

`.DSP` is the proposed Spectrum Dignified extension adopted by this module;
`.ASP` is its classic text extension. They are distinct from the ZX81
module's extensions.

Without `--tk_tokenize`, only the listing is saved. The Dignified listing
is still checked for the supported subset before being written.
`-rh` disables the original suite's generated REM header; omit it to keep
the header. MSX remains the default system unless `-id zxspectrum` is given.

To select an output folder/name, pass the second positional argument:

```powershell
python -B badig.py examples\zxspectrum\hello.DSP "C:\Spectrum Programs\demo.ASP" -id zxspectrum --tk_tokenize
```

The output folder must already exist. TAP uses the listing's stem and folder.
Do not name the intermediate text output `.tap`, because text and tape must
be different files.

## First program

```basic
REM FIRST SPECTRUM MILESTONE
CLS
LET counter=1
{again}
PRINT "SPECTRUM ";counter
LET counter=counter+1
IF counter<=3 THEN GO TO {again}
PRINT "DONE"
STOP
```

With `-rh -ca`, the label resolves to line 40. The expected program output is:

```text
SPECTRUM 1
SPECTRUM 2
SPECTRUM 3
DONE
```

The Spectrum also displays its normal STOP report after the program.

### Names, macros and strings

Use explicit LET for assignments, including after THEN and colons:

```basic
DEFINE [limit] [3]
DECLARE total_score:t
LET total_score=1
PRINT "SAY ""HELLO"""
IF total_score<[limit] THEN LET total_score=total_score+1
STOP
```

Names such as `counter` and `score2` stay native long numeric names.
Use `DECLARE total_score:t` to map a Dignified snake_case name to an explicit
single-letter alias. Do not rely on automatic underscore removal or implicit
short-name allocation. DECLARE must precede uses, as in the original suite.
`~name` can retain a valid alphanumeric numeric name; it cannot make a
string, array or invalid Sinclair identifier valid.

Keywords must be separate from adjacent identifiers/numbers in classic
text input. For example, use `PRINT counter` rather than `PRINTcounter`.
The generated Dignified listing retains necessary separators even with
`-ss`; strings and REM contents are not scanned for keywords or numbers.

Comments using `##` remain Dignified-only and are removed.
Use `REM` to retain a comment in the Spectrum program.
`-lbr` appends labels using `: REM`, not MSX apostrophe comments.

## CLI, INI and remtags

| Option | Purpose | Default |
| --- | --- | --- |
| `-id zxspectrum` | Select the module before argument/remtag processing | MSX otherwise |
| `--spectrum-version` | Display the independent module version | No conversion |
| `--tk_tokenize` | Create TAP after creating/validating the listing | False |
| `--tk_name "MY TAPE"` | Name inside the tape header | First 10 characters of output stem |
| `-asc` | Tokenize an already numbered classic text file | False |
| `-ls N`, `-lp N` | Initial line and positive line step | 10, 10 |
| `-rh` | Suppress the common REM header | Header enabled |
| `-ca` | Capitalize non-literal source | False |
| `-tr` | Read UTF-8 input instead of the default Latin-1 | False |

`--tk_name` accepts 1..10 printable ASCII characters. Explicit overlong
names are errors, not silently truncated. Only the default stem-derived
name is truncated. The host filename can be longer and contain spaces.

The tokenizer defaults are in `zxspectrum\tokenizer_interface.ini`:

```ini
[CONFIGS]
tokenize = False
name =
```

Options are applied in the suite's usual order: INI, CLI, then remtags.
Examples:

```basic
##BB:tk_tokenize=True
##BB:tk_name=MY TAPE
```

`##BB:arguments=...` can pass ordinary conversion options, but `-id`
must select the module before the source's remtags are read.

Classic input is preserved rather than renumbered:

```powershell
python -B badig.py examples\zxspectrum\hello.ASP -id zxspectrum -asc --tk_tokenize
```

## EightyOne loading

The first supported workflow is **manual**, so it does not change the
emulator's machine/profile behind the user's back.

1. Start EightyOne and select a **Spectrum 48K**, English ROM.
2. Open `hello.tap` in the emulator's tape manager and rewind it.
3. If not using the emulator's own autoload facility, enter `LOAD ""` on the
   Spectrum and start tape playback. Flash loading is an emulator option.
4. After loading, use `LIST` to inspect the program, then enter `RUN`.

The TAP header deliberately disables BASIC autorun in v1.1.0.
Tape autoload in EightyOne and BASIC autorun are different settings.
This module does not expose `--em_run` yet.

Do not assume that opening a TAP argument also changes a ZX81 profile into
a Spectrum profile. The executable is not bundled, and no ROMs are included
in this release.

## Limits and failure handling

- Numbered program lines must increase strictly within 1..9999.
- Line step zero and numbering overflow are errors.
- The shared Dignified generator still has its original 256-character
  text-line limit. The binary record has an independent 16-bit length.
- TAP generation rejects a payload larger than 41612 bytes, based on the
  standard initial 48K PROG/RAMTOP addresses. This is only an upper bound:
  the ROM also needs space for variables, work areas and stacks, so practical
  programs must be smaller.
- ASCII printable text, the Spectrum pound sign and copyright character
  are supported. Other Unicode/graphics characters are not silently replaced.
  Use `-tr` for a UTF-8 source containing pound/copyright characters.
- The new module's validation/configuration/file errors use a nonzero exit
  code. Some errors in the pre-existing shared parser/logger still exit
  with status zero; inspect diagnostics as well as output files.
- The TAP is generated in memory and replaced only after a successful
  temporary-file write. A failed conversion does not refresh an existing
  tape; do not mistake an older output for a newly generated one.

## Verification and roadmap

Run the focused automated tests:

```powershell
python -B -m unittest zxspectrum.test_zxspectrum -v
```

They check fixed byte vectors, Sinclair number representations, labels,
strings/REM, aliases/macros, reports, CLI/remtags, TAP fields/checksums and
negative cases. The original manuals are also compared with the base to
ensure their original lines remain in order.

For this delivery, 16 automated tests passed. Focused MSX/CoCo conversions
and the complete CoCo example matched the original implementation byte for
byte. The supplied MSX example has obsolete remtags in the base branch,
so its unmodified conversion was not counted as a passing regression.

An isolated EightyOne 1.41 session selected the 48K model and recognized
the TAP in its tape manager, but did not provide verified ROM loading or
program execution in this environment. **Manual LOAD/LIST/RUN validation
was pending in 1.1.0.** The user subsequently confirmed successful
LOAD/LIST/RUN for hello.tap before implementation of 1.2.0.
New examples and TZX have automated format/conversion checks; no new
manual emulator validation is claimed for them.

Planned subsequent module previews, subject to adjustment:

| Version | Functional focus |
| --- | --- |
| 1.1.0 | First Dignified -> numbered BASIC -> TAP milestone |
| 1.2.0 | TZX and expansion of native command coverage |
| 1.3.0 | Restricted variable categories, arrays, DATA and native functions |
| 1.4.0 | Dignified conveniences and broader compatibility |
| 1.5.0 | Verified emulator integration and distribution/editor polish |

These are module versions, not replacements for the upstream suite's
version. Versions 1.1.0 through 1.4.0 are implemented.

See [OUTLINE.md](../OUTLINE.md) for the architecture and remaining work,
and [the example sources](../examples/zxspectrum/hello.DSP).

Technical references:

- [Sinclair manual: program structure](https://worldofspectrum.org/ZXBasicManual/zxmanchap2.html)
- [Sinclair manual: expressions and names](https://worldofspectrum.org/ZXBasicManual/zxmanchap7.html)
- [Sinclair manual: memory and numbers](https://worldofspectrum.org/ZXBasicManual/zxmanchap24.html)
- [Spectrum tape formats](https://worldofspectrum.org/faq/reference/formats.htm)
- [EightyOne project](https://sourceforge.net/projects/eightyone-sinclair-emulator/)
