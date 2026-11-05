# Spectrum editor templates

Spectrum 1.9.0: DZS/AZS are primary; legacy DSP/ASP remain associated.
Includes RUN/LIST/NEW/CONTINUE/OUT and BIN highlighting.
REMX and graphic/UDG escapes are highlighted in their literal contexts.
Native FN, files/streams and raw bytes in all contexts are highlighted.

Copy the syntax and build files into a Sublime Text user package.
Open the Basic Dignified repository root as the project folder so that
`$project_path` contains `badig.py`. Build with Python 3.8+ on PATH.
The build produces TAP and TZX without opening an emulator.
The default build is for DZS/DSP; select the **Classic AZS** variant for
numbered AZS/ASP. The variant adds `-asc` and preserves line numbers.
The **Dignify AZS** variant instead creates `$file.dignified.DZS` using
the Spectrum DignifieR. Existing output is refused; keep the suite as
the project root so Python can find the module.
Snapshots remain an optional CLI operation with SkoolKit; see the
[Spectrum manual](../../documentation/ZX_SPECTRUM.md#optional-z80-and-sna-snapshots).
Do not replace the original MSX or CoCo packages.
