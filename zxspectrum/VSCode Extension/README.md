# Basic Dignified ZX Spectrum

Spectrum module 1.6.0 editor companion. Adds DSP/ASP highlighting and
Dignified snippets. It does not include Python, the converter, ROMs or EightyOne.
Includes RUN/LIST/NEW/CONTINUE/OUT and BIN highlighting.

Install the VSIX using VS Code's **Extensions: Install from VSIX** command.
ASP also names web files: select **Sinclair BASIC** manually when appropriate;
existing web projects can override the file association.

Set `spectrum-basic.python`, `spectrum-basic.badigPath` (absolute badig.py path)
and, on Windows, `spectrum-basic.emulatorPath` (EightyOne.exe).
Merge the supplied `tasks.json` tasks into your workspace's `.vscode/tasks.json`;
do not overwrite existing tasks. Run **Tasks: Run Build Task** for TAP/TZX.
The emulator task waits until EightyOne closes and uses an isolated profile copy.
It is a launch integration, not ROM runtime-error monitoring.

To package from this directory: `npm ci` followed by `npm run package`.
Packaging is local; this extension is not published to a marketplace.
No license grant for the original Basic Dignified suite is made by this package.
