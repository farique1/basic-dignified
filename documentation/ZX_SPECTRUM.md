# ZX Spectrum Basic

**Module v1.10.0 preview (branch/VSIX; no new tagged release)**

The **ZX Spectrum** module converts **Dignified** code to **Sinclair Basic**
for the **48K English ROM** by default, with an opt-in **128K** token set
selected by `--sp_model 128` (see "128K model" below). Use `-id zxspectrum`
to select the module. The module version is independent of the Basic
Dignified Suite version (2.2.1).

The common [Basic Dignified manual](BASIC_DIGNIFIED.md),
[installation](INSTALLATION.md) and [module tools](MODULE_TOOLS.md) apply
alongside the system-specific rules below. The module supports a documented
subset, not the complete Sinclair language or every 128K/+2/+2A/+3 extension.

## Supported language

The module converts Dignified source to a numbered listing and optionally
creates standard ROM-loadable **TAP/TZX** or optional **Z80/SNA** snapshots.
The first example prints a counter three
times using a jump label.

Implemented:

- `PRINT`, explicit `LET`, `IF ... THEN GO TO`, `GO TO`/`GOTO`, `REM`,
  `CLS`, `STOP`.
- `BORDER`, `INK`, `PAPER`, `PAUSE`, `BEEP`, `INPUT`, `GO SUB`/`GOSUB`,
  `RETURN`, `FOR`/`NEXT`, `TO`, `STEP`, `DIM`, `DATA`, `READ`, `RESTORE`,
  `RANDOMIZE`, `PLOT`, `DRAW`, `CIRCLE`, `POKE`, `CLEAR`.
- `RUN`, `LIST`, `NEW`, `CONTINUE`, `OUT`, and `BIN` literals.
- `AT`, `TAB`, `FLASH`, `BRIGHT`, `INVERSE`, `OVER`, including PRINT modifiers.
- Functions: `RND`, `INKEY$`, `PI`, `POINT`, `SCREEN$`, `ATTR`, `VAL$`,
  `CODE`, `VAL`, `LEN`, `SIN`, `COS`, `TAN`, `ASN`, `ACS`, `ATN`, `LN`,
  `EXP`, `INT`, `SQR`, `SGN`, `ABS`, `PEEK`, `IN`, `USR`, `STR$`, `CHR$`.
- Numeric expressions using `+ - * / ^`, comparisons, `AND`, `OR`, `NOT`
  and parentheses. Sinclair semantics apply, not MSX bitwise semantics.
- Long **alphanumeric numeric scalar names**, without the MSX two-character
  aliasing limit. Names are case-insensitive in the Spectrum ROM.
- Labels, DEFINE macros, explicit DECLARE aliases and INCLUDE through
  the shared Dignified pipeline.
- String scalars, numeric/string arrays and slices; implicit LET, scalar
  compound assignments, PRINT shortcuts and Dignified FUNC/RET.
- Quoted text, doubled quotes within a string, and the PRINT apostrophe
  separator (newline). An apostrophe is **not** a Spectrum REM.
- TRUE = 1 and FALSE = 0.
- Decimal, scientific and binary literals, five-byte Sinclair numbers, numbered
  BASIC records, TAP header/data blocks and XOR checksums.
- Existing common options such as line start/step and reports.
- Graphic blocks **128..143**, UDGs **144..164**, and the **REMX** directive.
- Literal **`\{XX}`** bytes in strings, REM and code; **DEF FN/FN**, source
  LOAD/SAVE/VERIFY/MERGE, LINE, OPEN#/CLOSE#, streams and printer commands.
- [Spectrum DignifieR](DIGNIFIER.md#zx-spectrum-dignifier) for AZS to DZS.
- `--sp_model 128`: the `SPECTRUM` and `PLAY` 128K editor ROM tokens
  (see "128K model" below).

Not implemented in this preview:

- Microdrive/disk extensions and their hardware-dependent
  CAT/FORMAT/MOVE/ERASE commands.
- 128K Z80/SNA snapshots, the +2/+2A/+3 ROM variants, NextBASIC, turbo
  loaders and multi-file tapes.
- Automatic contextual short-name allocation; explicit aliases are required.
- Array/slice compound assignments and recursive local function frames.
- Extracting/detokenizing BASIC from tapes or snapshots.
- Automatic ROM runtime-error monitoring or assertions of emulated output.

Unsupported native words are rejected rather than advertised as working.
The tokenizer is not a complete Sinclair syntax checker: errors in supported
expressions can still be reported by the ROM when the program runs.

## 128K model

`--sp_model 48` (default) or `--sp_model 128` selects the ROM token set;
the equivalent remtag is `SP_MODEL=48|128`. INI < CLI < remtags precedence
applies, same as the other options. An invalid value is an explicit error.

The 128K editor ROM repurposes the last two UDG graphic codes (`%T` and
`%U`, bytes `0xA3`/`0xA4`) as two new keyword tokens:

- `SPECTRUM` takes no arguments; it switches permanently to 48 BASIC
  (there is no way back without a reset). `SPECTRUM 1` is rejected.
- `PLAY stringexpr[,stringexpr[,stringexpr]]` takes 1 to 3 comma-separated
  expressions, one per sound channel. The converter only validates the
  argument count and that none is empty; the note/octave/duration mini
  language inside each string is a ROM runtime concern, exactly like a
  `LOAD`/`SAVE` filename expression is not content-checked.

Both words are reserved identifiers in **either** model (like the existing
`CAT`/`FORMAT`/`MOVE`/`ERASE` disk tokens), so `LET spectrum=1` is rejected
even with `--sp_model 48`; the Spectrum ROM itself would allow it as a
48K variable name, but keeping them reserved avoids depending on a
model-aware grammar in the shared Dignified core. Using `SPECTRUM`/`PLAY`
as a statement, or the UDG forms `%T`/`%U`/`\A3`/`\A4`, requires
`--sp_model 128`; the raw byte escapes `\{A3}`/`\{A4}` still insert those
bytes literally in either model, like any other `\{XX}` byte.

`--sp_model 128` only changes which BASIC tokens are accepted. It does not
enable 128K Z80/SNA snapshots (`--tk_format z80`/`sna`/`all` are rejected
with `--sp_model 128`; snapshots remain 48K-only), paging/AY commands beyond
what `OUT`/`PLAY` already express, a RAM disk, or the +2/+2A/+3 ROM
variants. `--em_run` with `--sp_model 128` copies `eightyone128.ini`
(`MachineName=Spectrum 128`, `spectrum128.rom`) instead of the 48K
template. **Manual loading and execution of `play128.tzx` were confirmed
by the user in EightyOne and Spectaculator on 2026-11-05. Automatic 128K
launch/loading through `--em_run` instead froze EightyOne after its boot
screen**; use manual loading as described below.

The [Spectrum DignifieR](DIGNIFIER.md#zx-spectrum-dignifier) (`-m
zxspectrum.dignifier`) has its own `--sp_model 48|128` flag; it must match
the classic source's token set, since the tool validates the input (and
the DZS it produces) against that model.

## Chained statements, native control commands and BIN

`:` separates statements without adding a BASIC line number:

```basic
counter=1:counter+=2:PRINT counter:STOP
```

becomes `10 LET counter=1:LET counter=counter+(2):PRINT counter:STOP`.
For `IF condition THEN ...`, the entire remaining line stays conditional,
as on the Spectrum; the converter does not split it into unconditional lines.
Colons inside strings are literal text. REM consumes the rest of the line,
including any colons or words that would otherwise be commands.
The existing Dignified core normalizes `::` to `:`; direct classic AZS (or legacy ASP) input
rejects an empty statement. A trailing `:` is rejected in both paths.

| Form | Sinclair behavior |
| --- | --- |
| `RUN` / `RUN expression` | Clears variables/display and starts execution at the beginning or the requested line |
| `LIST` / `LIST expression` | Lists from the beginning or the requested line |
| `NEW` | Deletes the in-memory program and variables; use with care |
| `CONTINUE` | Resumes according to the ROM's saved stop/error state |
| `OUT port,value` | Writes a byte to an I/O port, not to RAM |

RUN/LIST accept one optional numeric expression; in Dignified source, `RUN {label}` and
`LIST {label}` resolve to the numbered destination. They are not GO TO
aliases: in particular, RUN resets variables and clears the display.
NEW and CONTINUE take no
arguments. OUT requires two expressions separated by a top-level comma;
commas inside function calls or strings are not argument separators.
These new commands must start a statement (line start, after `:` or THEN).
Argument counts and balanced parentheses are checked. Complete expression
syntax/types and runtime limits remain the ROM's responsibility, just as
for the existing supported commands. For OUT the ROM accepts ports 0..65535
and byte values -255..255 after its numeric conversion.
These commands execute inside the emulated Spectrum; they are not host
converter/emulator controls. `LIST #stream` remains unsupported.

`BIN` introduces a literal, not a conversion function:

```basic
mask=BIN 00000101:mask+=BIN 10:PRINT mask
```

This prints 7. The source must contain at least one binary digit. The
tokenizer emits token C4, the original digits and marker 0E followed by the
five-byte representation of the binary value: `BIN 1010` caches decimal 10,
not 1010. Values must fit 0..65535; extra leading zeroes are allowed.
Spaces between bits are accepted; tabs are normalized to spaces in classic
input, consistently with other source whitespace.
Invalid digits, fractional/exponent forms, missing digits and overflow
are rejected. Write `-BIN 10` for a negative expression, not `BIN -10`.
Strings and REM text containing BIN are left literal.

Generate the new demonstration with:

```powershell
python -B badig.py examples\zxspectrum\native.DZS -id zxspectrum --tk_tokenize --tk_format both -rh
```

Its expected execution prints `BIN 7`, `CHAIN OK`, `A:B` and
`PRESS A KEY TO LIST`, then pauses for inspection. Press a key to list the
final PRINT/STOP lines; `PRESS A KEY TO RUN` introduces a second pause.
Press another key to RUN the `finish` label: the display is cleared and
`DONE` is printed. The pauses allow inspection before LIST and RUN.
OUT 254,1 selects a blue border without enabling the beeper.
Its TAP/TZX conversion is tested; **manual execution of this new 1.6.0
example remains pending**. The previously reported 16 passes apply only
to the four older demos.

## Characters and REM reservations

**Graphic blocks** use `\80` to `\8F`. **UDGs A..U** use `%A` to `%U`
or `\90` to `\A4`. These escapes are active in strings and REM text;
write `\\` and `%%` for the literal symbols. AZS keeps this readable
notation, while tokenized output contains the actual bytes.
The [complete conversion table](BASIC_DIGNIFIED.md#zx-spectrum-characters)
also describes the Spectrum keyboard and **POKE USR "A"** bitmap method.

**REMX l,n[,c]** is a DZS directive that inserts an absolute REM line
without changing normal line numbers or labels. Omitted c fills with
**character '0'**, not binary zero. A decimal byte or one quoted character/
escape may be supplied. Duplicates and collisions are errors; INCLUDE and
rem toggles work normally. See the [REMX reference](BASIC_DIGNIFIED.md#remx)
for counts, raw bytes and memory limits.

[graphics.DZS](../examples/zxspectrum/graphics.DZS) demonstrates all 16
blocks, UDG selection/definition and a reserved REM.

## Native functions, files and streams

**DEF FN f(x,a$)=expression** defines a native numeric function;
**DEF FN s$(a$)=expression** returns a string. Names/parameters are single
letters, optionally followed by `$`; zero arguments use **()**.
Call **FN f(3,"AB")** inside expressions. The tokenizer adds the ROM's
**0E + five-byte parameter slots** after each definition parameter;
calls do not get these slots. This is separate from Dignified FUNC/RET.
See [fn.DZS](../examples/zxspectrum/fn.DZS).

Source **LOAD/SAVE/VERIFY/MERGE** accept the Sinclair filename forms.
LOAD/SAVE/VERIFY support **DATA a()/a$()**, **CODE** and **SCREEN$**;
**SAVE name LINE {label}** supports autorun. MERGE applies to programs,
not arrays/CODE. Filename expressions, types, ranges and mounted media
remain the ROM's responsibility. These are emulator-side commands, not
host file operations; host TAP/TZX output is unchanged.

**OPEN #4,"S":PRINT #4;"OK":CLOSE #4** uses a stream connected to the screen.
Base channels are **K/S/P**; extended channels need their hardware.
**INPUT #0;LINE a$**, **LIST #2;line**, **LPRINT**, **LLIST** and **COPY**
are accepted. Printer output needs a printer to be visible.
See [streams.DZS](../examples/zxspectrum/streams.DZS); its tape/printer
section follows STOP and is deliberately not executed automatically.

**`\{XX}`** emits a literal byte in code as well as strings/REM. For example,
`\{F5}"HI"` supplies PRINT directly. Raw insertion can bypass structural
checks and create invalid programs; normal syntax is preferred for automatic
numbers/FN slots. See [literal bytes](BASIC_DIGNIFIED.md#literal-bytes).

**AZS to DZS** uses `python -B -m zxspectrum.dignifier input.AZS output.DZS`.
It replaces static line references with labels and keeps conditional
colon chains and literal data. Regular numbering is retained; irregular
numbering with dynamic destinations is rejected. Existing destinations
need **--force**. Read the [DignifieR manual](DIGNIFIER.md#zx-spectrum-dignifier)
before importing externally numbered or machine-code-containing programs.

## Installation

Follow the common [installation instructions](INSTALLATION.md) and use
a source archive or branch containing the Spectrum module.
Keep `badig.py`, `support`, `msx` and `zxspectrum` together: the new module
reuses the existing MSX class scaffolding, but overrides the active dialect
and does **not** use MSX tokenization.

The suite's Python 3.8+ requirement is unchanged; text and tapes need no
additional Python packages. Snapshots require the optional engine below.
Python 3.14 was used for this milestone's automated checks, not a Python 3.8
runtime certification.

From the repository root:

```powershell
python -B badig.py -id zxspectrum --spectrum-version
python -B badig.py -id zxspectrum -h
python -B badig.py examples\zxspectrum\hello.DZS -id zxspectrum --tk_tokenize --tk_format both -rh -ca
```

Outputs:

- `hello.AZS`: numbered classic Sinclair BASIC listing.
- `hello.tap`: tokenized program in a standard tape container.
- `hello.tzx`: the same program in TZX 1.20 standard-speed blocks,
  with one-second pauses.

`.DZS` and `.AZS` are the Spectrum-specific source/text extensions.
They are distinct from the ZX81 module's extensions. Existing `.DSP` and
`.ASP` files remain supported, but are no longer the default example names.

Without `--tk_tokenize` or `--em_run`, only the listing is saved. The Dignified listing
is still checked for the supported subset before being written.
`-rh` disables the original suite's generated REM header; omit it to keep
the header. MSX remains the default system unless `-id zxspectrum` is given.

To select an output folder/name, pass the second positional argument:

```powershell
python -B badig.py examples\zxspectrum\hello.DZS "C:\Spectrum Programs\demo.AZS" -id zxspectrum --tk_tokenize
```

The output folder must already exist. Binary outputs use the listing's stem
and folder. Do not give the intermediate text an extension selected for
binary output; source and destination must be different files.

## Optional Z80 and SNA snapshots

Install the extra **only when snapshots are needed**, using the same Python
interpreter that runs the converter. A virtual environment is recommended:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r zxspectrum\requirements-snapshots.txt
.\.venv\Scripts\python.exe -B badig.py examples\zxspectrum\hello.DZS -id zxspectrum --tk_tokenize --tk_format all -rh -ca
```

The optional requirement is `skoolkit>=8.10,<11`; pip selects a release
compatible with the chosen Python. SkoolKit 8.10 supports Python 3.8;
newer engine releases may require newer Python. Versions 8.10 and 10.1
were exercised here. Existing Python/interpreter choices are not changed
automatically, and generating TAP/TZX never installs or imports SkoolKit.
SkoolKit and its separately installed resources retain their own licenses.

| `--tk_format` / `TK_FORMAT` | Binary outputs |
| --- | --- |
| `tap` (default) | TAP |
| `tzx` | TZX |
| `both` | TAP + TZX, unchanged |
| `z80` | Z80 v3, 48K |
| `sna` | SNA 48K |
| `all` | TAP + TZX + Z80 + SNA |

AZS is still the intermediate text output. For an existing numbered listing,
add `-asc`. The snapshot worker uses a temporary local TAP and the engine's
48K English ROM simulation, stopping immediately after ROM loading, before
executing the user's BASIC. It validates the program bytes, PROG/VARS,
variable terminator, stack space and expected ROM return address. Engine
exit status alone is not treated as proof that loading succeeded.

Z80 and SNA describe the same loaded state. SNA stores the saved PC on the
stack as required by its format; the loader's RETN restores PC/SP. Conversion
rejects states that cannot be represented safely. These are not renamed
tapes, generic 128K snapshots or captures of a running user program.

`--tk_autorun -1` leaves BASIC ready for manual LIST/RUN; `0` or `1..9999`
preserves the ROM's pending autorun selection. Conversion does not execute
arbitrary BASIC to create the snapshot. Open Z80/SNA with the emulator's
snapshot/file-open command, not its tape manager. With `--em_run`, select
`--tk_format z80` or `sna`; tape autoload is disabled in the private profile.
For `both`/`all`, the launcher opens the first output, TAP.

Missing engine, simulation timeout/incomplete loading and invalid state are
explicit nonzero failures. All selected formats are built before any binary
output is replaced, so snapshot-generation failure preserves existing tapes
as well. Each final file is replaced atomically, not as one multi-file
transaction; an OS error during replacement can still leave a partial set.
An AZS listing may already have been written when binary generation fails.

The VS Code task template includes **Spectrum: Install optional snapshot
engine**, an explicit user-run pip task using `spectrum-basic.python`, and
all-format conversion tasks. The VSIX still requires an external Python and
converter; a genuinely integrated, low-setup VSIX is a **future packaging
milestone**, not a feature delivered by this release.

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

LET may be omitted in Dignified source, including after THEN and colons.
Classic `-asc` input must use explicit LET. Explicit LET remains supported:

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
| `--sp_model 48\|128` | Target ROM token set (see "128K model" above) | 48 |
| `--tk_tokenize` | Create selected binary formats after validating the listing | False |
| `--tk_name "MY TAPE"` | Name inside the tape header | First 10 characters of output stem |
| `--tk_format tap\|tzx\|both\|z80\|sna\|all` | Select tapes/snapshots (see table above) | tap |
| `--tk_autorun N` | BASIC starting line; -1 disables | -1; 0 with --em_run |
| `--em_run` | Generate selected output, open EightyOne and wait for it to close | False |
| `--em_path PATH` | EightyOne executable on Windows | Must be configured to run |
| `--em_setting PATH` | 48K INI to copy for the session | Bundled 48K template |
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
format = tap
autorun = -1
```

Options are applied in the suite's usual order: INI, CLI, then remtags.
Examples:

```basic
##BB:tk_tokenize=True
##BB:tk_name=MY TAPE
##BB:tk_format=both
##BB:tk_autorun=0
```

`##BB:arguments=...` can pass ordinary conversion options, but `-id`
must select the module before the source's remtags are read.

Classic input is preserved rather than renumbered:

```powershell
python -B badig.py examples\zxspectrum\hello.AZS -id zxspectrum -asc --tk_tokenize
```

The emulator defaults are in `zxspectrum\emulator_interface.ini`:

```ini
[CONFIGS]
run = False
emulator_path =
setting =
```

Equivalent remtags: `EM_RUN=True|False`, `EM_PATH` and `EM_SETTING`.
INI < CLI < remtags applies to both tools. Invalid boolean/numeric/format
values are explicit errors. `TK_TOKENIZE=False` conflicts with enabled EM_RUN.

## EightyOne loading and launch integration

Manual loading remains available:

1. Start EightyOne and select a **Spectrum 48K** (or **Spectrum 128** with
   `--sp_model 128`), English ROM.
2. Open `hello.tap` in the emulator's tape manager and rewind it.
3. If not using the emulator's own autoload facility, enter `LOAD ""` on the
   Spectrum and start tape playback. Flash loading is an emulator option.
4. After loading, use `LIST` to inspect the program, then enter `RUN`.

The default tape header disables BASIC autorun unless requested.
Tape autoload in EightyOne and BASIC autorun are different settings.

To generate, launch and autoload:

```powershell
python -B badig.py examples\zxspectrum\hello.DZS -id zxspectrum --em_run --em_path "C:\zeddy\EightyOne.exe" -rh -ca
```

`--em_run` enables tokenization and defaults to autorun line 0.
Use `--tk_autorun -1` to load without BASIC autorun, or `--tk_format tzx`
to launch the TZX instead. If both containers are generated, TAP is opened.

The bundled `eightyone48.ini` template selects Spectrum 48K and the installed
`spectrum48.rom`; with `--sp_model 128`, `eightyone128.ini`
(`MachineName=Spectrum 128`, `spectrum128.rom`) is used instead. `--em_setting`
accepts an existing profile only if its HARDWARE/MachineName matches the
selected `--sp_model` exactly (`48K Spectrum` for 48, `Spectrum 128` for 128).
The profile is parsed as Latin-1, copied to a temporary directory, and
autoload/flash-load are enabled in that copy for tapes (disabled for
snapshots). The converter waits for EightyOne, checks its exit status,
then removes the copy. Ctrl+C terminates the child and reports interruption.
The emulator itself may write its own support files; the converter does not
overwrite the original INI. ROMs must already exist in the emulator installation.

**Known 128K launch issue (user report, 2026-11-05):** EightyOne launched
through `--em_run` shows its boot screen and then a black screen, with no
music or response to BREAK until reset. The same `play128.tzx` loads and
plays correctly when EightyOne is opened separately and Spectrum 128 is
selected manually. The cause has not been isolated; this is not a successful
automatic-launch test. `--tk_autorun -1` only disables BASIC autorun, not
the emulator's autoload/flash-load settings.

For now, generate the tape without `--em_run`, then load it manually:

```powershell
python -B badig.py examples\zxspectrum\play128.DZS -id zxspectrum --sp_model 128 --tk_tokenize --tk_format tzx --tk_autorun -1 -rh -ca
```

In the emulator, select Spectrum 128, load the TZX, inspect it with `LIST`
and enter `RUN`. The example plays three channels, prints `DONE`, then
deliberately executes `SPECTRUM` to enter 48 BASIC. In 48 BASIC, the bytes
for `SPECTRUM`/`PLAY` are displayed as UDG T/U rather than keywords; this
is expected, not tape corruption. To remain in 128 BASIC, omit the final
`SPECTRUM` statement before regenerating the tape.

Launch validation does not imply BASIC runtime-error monitoring. An emulator
can close successfully after a ROM error; inspect the Spectrum screen.

Do not assume that opening a TAP argument also changes a ZX81 profile into
a Spectrum profile. The executable is not bundled, and no ROMs are included
in this release.

### Spectaculator and other emulators

The user confirmed manual loading and execution of `play128.tzx`, including
its music and final switch to 48 BASIC, in Spectaculator as well as EightyOne.
This confirms that example's manual TZX workflow, not every format/model.

Generate TAP/TZX without `--em_run`, select the matching 48K or 128K model
in your emulator and open the tape. In Spectaculator, use **File > Open**;
with **Auto load** enabled, opening a tape resets the emulated Spectrum and
starts loading. Otherwise, initiate loading from BASIC and start tape
playback as needed. See its official [tape-loading instructions](https://www.spectaculator.com/docs/spectaculator/9.1/tape/load.html)
and [Auto load settings](https://www.spectaculator.com/docs/spectaculator/9.1/cassette/autoload.html).
Tape autoload and the BASIC autorun line stored in the tape are separate.

If Windows associates `.tzx` files with Spectaculator, you can also request
opening the generated tape from PowerShell:

```powershell
Start-Process -FilePath (Resolve-Path .\examples\zxspectrum\play128.tzx).Path
```

This uses the current Windows file association and the emulator's own
settings; it does not select the model or certify that loading succeeded.
Without that association, open the file from Spectaculator itself.
Do not pass Spectaculator as `--em_path`: the current launcher passes an
EightyOne-specific INI and arguments. Integrated Spectaculator launching,
model selection and lifecycle handling remain future work; no verified
command-line model-selection option was established in this investigation.

## Editor integration and distribution

The release includes source archives, example DZS/AZS/TAP/TZX files,
representative hello and graphics Z80/SNA pairs, an
offline VSIX, and Sublime templates. No marketplace publication is required.

- [VS Code companion](../zxspectrum/VSCode%20Extension/README.md):
  install the VSIX, configure converter/Python/emulator paths, and merge
  the supplied task template into existing workspace tasks.
  The single Spectrum VSIX supports 48K and 128K; set
  `spectrum-basic.model` to `"48"` or `"128"` before running its tasks.
  Snapshot tasks still require 48K. For 128K, use tape conversion and
  manual loading rather than the EightyOne launch task (known bug above).
- [Sublime templates](../zxspectrum/Sublime%20Package/README.md):
  open the repository root as the project folder and use the provided build.

DZS/AZS are primary; legacy DSP and ASP conflict with other products' file
extensions. Select the language
mode or set workspace-specific file associations when needed.
Building the VSIX needs Node/npm (`npm ci`, `npm test`, `npm run package`
in its source directory); text/tape conversion needs no new Python packages.
Snapshot support is installed explicitly, using the configured interpreter.

## Limits and failure handling

- Numbered program lines must increase strictly within 1..9999.
- Line step zero and numbering overflow are errors.
- The shared Dignified generator has its original 256-character text-line
  limit for ordinary statements; REMX is expanded afterwards and may exceed
  it. Binary records still have an independent 16-bit length.
- TAP generation rejects a payload larger than 41612 bytes, based on the
  standard initial 48K PROG/RAMTOP addresses. This is only an upper bound:
  the ROM also needs space for variables, work areas and stacks, so practical
  programs must be smaller.
- ASCII printable text, the Spectrum pound sign and copyright character
  are supported. Other Unicode/graphics characters are not silently replaced.
  Use `-tr` for a UTF-8 source containing pound/copyright characters.
- Spectrum validation/configuration/file errors use a nonzero exit code.
  Since 1.5.1 this also covers fatal shared parser/logger diagnostics after
  Spectrum selection, including missing labels, macros, includes and sources.
  Quiet mode does not turn a failure into success. Existing per-logger
  verbosity behavior is unchanged; some early/file errors can still print.
- Each binary output is generated before replacement and saved only after a successful
  temporary-file write. A failed conversion does not refresh an existing
  tape; do not mistake an older output for a newly generated one.

## Examples and verification

The supplied examples cover [labels](../examples/zxspectrum/hello.DZS),
[colour/sound/loops](../examples/zxspectrum/colours.DZS),
[DATA and arrays](../examples/zxspectrum/data.DZS),
[FUNC/RET](../examples/zxspectrum/functions.DZS),
[native commands/BIN](../examples/zxspectrum/native.DZS) and
[graphics/UDGs/REMX](../examples/zxspectrum/graphics.DZS).
Run automated checks with `python -B -m unittest zxspectrum.test_zxspectrum -v`.
Snapshot/ROM probes are explicitly skipped without optional SkoolKit.

Graphics tests check all 37 character codes and, with the engine installed,
actual display pixels, UDG RAM rows and REM control-byte data after resuming
Z80/SNA. This is not manual EightyOne certification. The native and graphics
demos and snapshot loading still need manual emulator confirmation.
Release history and pending implementation work are kept in
[OUTLINE.md](../OUTLINE.md#pendencias-priorizadas), including manual acceptance
checks, separate from the usage reference. The published
[1.9.0 preview](https://github.com/wilsonpilon/basic-dignified/releases/tag/spectrum-v1.9.0)
also supplies native FN and streams demos. ROM probes exercise numeric/string,
zero/multiple-argument and nested FN calls, verify global-variable isolation,
raw string bytes and screen streams in both snapshot formats. Native tape
operations/printer output still require manual emulator/media verification.

## Technical references

- [Sinclair character set and UDG definition](https://worldofspectrum.org/ZXBasicManual/zxmanchap14.html)
- [Sinclair memory and BASIC record format](https://worldofspectrum.org/ZXBasicManual/zxmanchap24.html)
- [Sinclair command reference](https://worldofspectrum.org/ZXBasicManual/zxmanappc.html)
- [Tape and snapshot formats](https://worldofspectrum.org/faq/reference/formats.htm)
- [SkoolKit documentation](https://skoolkit.ca/docs/skoolkit/index.html)
