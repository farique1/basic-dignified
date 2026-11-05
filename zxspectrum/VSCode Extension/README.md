# Basic Dignified ZX Spectrum

Spectrum module 1.7.0 editor companion. Adds DZS/AZS highlighting and
Dignified snippets. It does not include Python, the converter, ROMs or EightyOne.
Includes RUN/LIST/NEW/CONTINUE/OUT and BIN highlighting.

Install the VSIX using VS Code's **Extensions: Install from VSIX** command.
Legacy DSP/ASP associations remain supported. ASP also names web files:
select **Sinclair BASIC** manually when appropriate;
existing web projects can override the file association.

Set `spectrum-basic.python`, `spectrum-basic.badigPath` (absolute badig.py path)
and, on Windows, `spectrum-basic.emulatorPath` (EightyOne.exe).
Merge the supplied `tasks.json` tasks into your workspace's `.vscode/tasks.json`;
do not overwrite existing tasks. Run **Tasks: Run Build Task** for TAP/TZX.
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

This VSIX remains an editor companion, not an all-in-one converter. Python,
Basic Dignified, the optional engine and EightyOne are external components.
A genuinely integrated, low-setup VSIX is reserved for final packaging.

To package from this directory: `npm ci` followed by `npm run package`.
Packaging is local; this extension is not published to a marketplace.
No license grant for the original Basic Dignified suite is made by this package.
