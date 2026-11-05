# Basic Dignified ZX Spectrum

VSIX 1.10.1, companion for Spectrum module 1.10.0, for both 48K and 128K.
Adds DZS/AZS highlighting and
Dignified snippets. It does not include Python, the converter, ROMs or EightyOne.
Includes RUN/LIST/NEW/CONTINUE/OUT and BIN highlighting.
REMX, graphic/UDG escapes and bitmap/reservation snippets are included.
Native DEF FN/FN, tape/stream commands and raw bytes in code/strings/REM
are highlighted. The byte and DEF FN snippets use the new syntax.
PLAY and SPECTRUM are highlighted in both Dignified and classic sources.
The DignifieR task uses the suite folder as workspace/cwd and writes
`input.AZS.dignified.DZS`; it refuses existing output. It is not `-asc`.
See the [character table](../../documentation/BASIC_DIGNIFIED.md#zx-spectrum-characters).

Install the VSIX using VS Code's **Extensions: Install from VSIX** command.
Legacy DSP/ASP associations remain supported. ASP also names web files:
select **Sinclair BASIC** manually when appropriate;
existing web projects can override the file association.

Set `spectrum-basic.python`, `spectrum-basic.badigPath` (absolute badig.py path)
and, on Windows, `spectrum-basic.emulatorPath` (EightyOne.exe).
Merge the supplied [`.vscode/tasks.json`](.vscode/tasks.json) tasks into your workspace's `.vscode/tasks.json`;
do not overwrite existing tasks. Run **Tasks: Run Build Task** for TAP/TZX.
The [language configuration](config/language-configuration.json) is shared
by the two Spectrum language modes and loaded automatically by VS Code.
Both `.vscode/` and `config/` are included in the VSIX. Installing the VSIX
does not copy build tasks into your workspace; merge them manually.
Set `spectrum-basic.model` to `"48"` (default) or `"128"` in VS Code
settings before building or using the DignifieR task. The supplied tasks
pass the selection as `--sp_model`; a source `##BB:SP_MODEL=128` remtag
overrides that selection for converter tasks. This is one VSIX for both
models, not separate extensions.

**Known 128K launch bug:** `--em_run` can freeze EightyOne after its boot
screen. Use **Spectrum: Convert TAP and TZX**, select Spectrum 128 in the
emulator, then load the generated tape manually. The user confirmed
`play128.tzx` loading and playing in both EightyOne and Spectaculator.
Do not pass Spectaculator as `spectrum-basic.emulatorPath`: the launcher
uses EightyOne-specific arguments. The example's final `SPECTRUM` command
deliberately switches to 48 BASIC.

The emulator task waits until EightyOne closes and uses an isolated profile copy.
It is a launch integration, not ROM runtime-error monitoring.

Text and TAP/TZX conversion need no extra Python packages. For optional
48K Z80/SNA snapshots, run **Spectrum: Install optional snapshot engine**
from the merged tasks. This explicitly runs
`-m pip install "skoolkit>=8.10,<11"` with `spectrum-basic.python`; use an
absolute virtual-environment Python path to keep installation isolated.
The engine is not installed automatically by opening a source or using tapes.
Use **Spectrum: Convert all formats (optional engine required)** for DZS,
or **Spectrum: Classic to all formats (optional engine required)** for AZS.
The latter also accepts legacy ASP and adds `-asc`; extensions alone do not
select classic parsing. Both tasks create TAP/TZX/Z80/SNA; the normal build
still creates only tapes and needs no engine.
The all-formats tasks require the 48K model; 128K snapshots are explicitly
unsupported and result in an error.

This VSIX remains an editor companion, not an all-in-one converter. Python,
Basic Dignified, the optional engine and EightyOne are external components.
Spectrum 48K/128K share this package; other machines keep their own packages.

To package from this directory: `npm ci` followed by `npm run package`.
Packaging is local; this extension is not published to a marketplace.
No license grant for the original Basic Dignified suite is made by this package.
