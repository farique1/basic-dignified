# Implementation Ideas and Known Bugs  
  
Not all topics presented here are going to be implemented. Some are just ideas and brainstorms.  
  
## Known Bugs  
**Highlighting**  
- Toggles, labels, ~, declares, functions and long named variables starting with a number not highlighting as error

**Conversion**  
- Toggles, labels, ~, declares, functions and long named variables starting with a number not giving an error and converting to erratic results.  
- If `ENDIF` after a `:` on another line, `ENDIF` will be removed and the line after it will be joined.  

## ZX-81 Module Status

The ZX-81 module currently converts `.DZX` to numbered `.AZX`, maps long Dignified variables from `Z` down to `A`, supports `[?](row,column)` as `PRINT AT`, and tokenizes to `.p` in Python. Strings support doubled quotes (`""`) and the backslash-quote spelling in both `.DZX` and `.AZX`; inverse-video and block-graphics escapes are also supported. VS Code/Sublime sources and a VSIX are in `zx81/`.

Literal byte escapes use `\{XX}`, with exactly two hexadecimal digits (case insensitive), in `.AZX` and `.DZX`. They work inside strings and `REM` as well as in code, without changing quote/REM state or being interpreted as tokens or numbers. Malformed escapes report the line number. An immediate `\{7E}` after a numeric literal suppresses its calculated hidden floating-point value; provide the marker and all five value bytes explicitly, for example `0\{7E}\{81}\{00}\{00}\{00}\{00}`. A space before `\{7E}` does not suppress the calculated value. Existing graphics and inverse-video escapes are unchanged.

Remaining work before calling the module complete:
- Implement and document the ZX-81 Unicode map for `-tr`.
- Audit commands/functions and edge cases against the target ROM/BASIC version.
- Test opening and running generated `.p` files in EightyOne, not only creating them.
- Decide whether to support literal apostrophe another way; it is not in the ZX-81 character set and the tokenizer currently rejects it.
- Add user-approved regression samples for strings, DATA/REM, graphics, line limits and error cases.

### ZX-81 Audit: 2026-11-03

The review baseline is Farique's upstream commit `4283702d96bd45fa0fd4f5b2c8ecb64af93705cb`. The regression suite now also covers PowerShell input paths and stale-output removal. Pending and resolved findings are distinguished below; passing tests do not imply that the module is complete.

**High priority: generated program correctness**

- **Resolved: `STEP` keyword in Dignified conversion.** `STEP` is now reserved, so `for g = 20 to 1 step -1` keeps its step. Numbers with an exponent such as `4E4` are also lexed as one number instead of `4` followed by the variable `E4`. Regression tests cover both.
- **Added: numbered `.DZX` listings are renumbered.** Numeric jump targets become labels and the listing goes through the Dignified pipeline into a new `.AZX`. Computed jump targets are rejected because they cannot be renumbered safely.
- **Resolved: floating-point rounding and range.** Hidden numbers use an exact binary exponent; a mantissa rounded up to the next power of two now carries into the exponent, so `1.9999999999` is stored as `2` instead of `1`. Values whose exponent would be `0` (the encoding of zero) or above `255` are rejected. Known values such as `1`, `10` and `16514` keep their previous bytes.

**High priority: trustworthy build results**

- **Resolved for the PowerShell helper: stale binary output.** At the user's request, the helper deletes the destination `.p` before conversion. Regressions cover invalid escapes in both classic and Dignified sources: failure leaves no `.p`, returns nonzero and does not print `Created`. The shared logger still raises `SystemExit(0)` for conversion errors, so direct CLI, Bash and editor-task failure propagation remains a separate pending review.

**Medium priority: helpers and editor integration**

- **Resolved: explicit PowerShell input extensions.** The helper preserves an extension supplied by the caller and appends `.DZX` only when it is absent. Tests cover explicit `.DZX`/`.dzx`, numbered `.AZX` and `.txt`, spaces and dotted names. The helper supplies the `.AZX` destination explicitly to avoid Badig misinterpreting dotted filenames, does not copy an `.AZX` onto itself and rejects binary `.p` input.
- **Resolved in the editor sources: hexadecimal escape scopes.** Both VS Code and Sublime grammars recognize `\{XX}` in code, strings and `REM` before label matching. Valid lowercase and uppercase digits are scoped as hexadecimal escapes; malformed sequences are not. TextMate/Oniguruma checks cover actual VS Code scopes and REM termination; Sublime YAML contexts and regexes are validated with Oniguruma.
- **Bash helper differences.** On case-sensitive filesystems it requires the `.DZX` suffix in uppercase, and it does not accept explicit extensions or delete an old `.p` before converting, as the PowerShell helper does. Numbered `.DZX` listings work, since `badig.py` renumbers them itself. It has not been run on a case-sensitive filesystem in this review.
- **Resolved for this update: packaged extension freshness.** `basic-dignified-zx81-2.0.0.vsix` has been rebuilt with the hexadecimal escape scopes and current README. Package inspection confirms matching grammars, configuration, tasks, snippets and manifest. Continue rebuilding and checking the VSIX whenever its source files change.

**Documentation and follow-up features**

- The [side-by-side graphic reference](../zx81/zx81-graphics-reference.svg) now shows all 22 block/checkerboard glyphs beside their source patterns, literal byte escapes and decimal codes. Both the main language guide and DignifieR guide embed it; the original GIF remains available.
- Preserve the original MSX/CoCo text, examples and walkthroughs when editing documentation. The preservation check compares every original nonblank line in order, ignoring only trailing whitespace.
- Verify opening and running `.p` files in EightyOne, including a descending loop, strings, graphics and the configured emulator path. This review did not perform a GUI execution test.
- Keep Unicode translation (`-tr`), a detokenizer, compact display-file output for 1K machines, and execution monitoring as separate optional projects. Do not imply those features already exist. The current tokenizer always generates an expanded display file.
- **Added: ZX81 Basic DignifieR.** `zx81/zx81bader.py` converts numbered ZX-81 listings to Dignified code, with options in the code and on the command line, including variable renaming.
- **Core issue worked around for ZX-81: phantom `program` variable.** The lexer repeats the internal `PROGRAM` line at the end of the code, and the parser assigns it a short variable, which appears in the `-var` report on every system (`zz:program` on MSX). The ZX-81 lexer drops it, because with only 26 letters it prevented a program from using all of them. The MSX/CoCo behaviour is unchanged.
- **Added: `remx` machine code `REM` lines.** `remx <line>,<count>[,<byte>]` creates a fixed-number `REM` line of up to 49152 bytes. The tokenizer limit is now the real 64 KB address space (48231 bytes of program) instead of a fixed 32 KB.
- **Core issue (open): errors exit with status 0.** The shared logger raises `SystemExit(0)` after a conversion error, so scripts and editor tasks cannot detect a failed build by its exit status. Changing it would affect every system, so it is left for the author to decide.
  
## Changes to this version  
*v2.2.1*  
- Fixed a bug recognizing an `EOF` command or variable as the end of file.
- Changed the way the lexer finds the end of the file. It now looks for the last line instead of adding an arbitrary string at the end.

*v2.2*  
- Removed `systems.json`.  
- The information about the system name and extension are now on the system language module.  
- Special extensions like the `.lst` list extension are now defined on the module that uses them, like the tokenizer, in this case.  
- Changed the terminal panel presentation in the VSCode tasks to `dedicated`.   
- Better handling of file saving (including the `export_file` remtag). Can now use relative paths and paths without files.  
- Fixed a bug related to the scope name of the syntax configuration on the Sublime package.  
- Fixed a bug where `defusr` and `usr` where only being recognized as instructions if followed by a number.  
  
## To Do  
  
**General**  
- Publish the VSCode extensions and the Sublime package on their online stores.  
- Make a tool to upgrade the dignified code from version 1.6 to version 2.0.  
- Make a graphical interface for installation and configs maybe also a complete GUI.  
- Make an installation script.  
  
**Highlighting**  
- Show error if `[` or `]` on define identifier.  
- highlight error if number on next line after `_` and `##`, but ok if no `##` after `_`.  
- Highlight line or block KEEP as error if starting with number.  
- Highlighting from hex numbers bleeding into words if touching and starting with A-F.  

**Language improvements**  
- Numbers next line after a `:` are being kept, remove.
- Make defines take multiple different variables.  
- Give a warning if a variable is passed to a define without one defined.  
- Allow define (identifiers) start with `_` (and update highlighting accordingly)  
- Use more than one KEEP on a line or block (is it already?)  
- Remove `ENDIF`  
  
**Generic improvements**  
- Color the terminal output. Option to disable for cases like Sublime that doesn't support it.  
- Option to control the behavior of the namespaces on the `include`d files. Allowing or denying the mixing of `define`s and labels for instance.  
- If there is a `badig.ini` on the folder of the current project, use it as a project setting.  
- Change the name of `bagid_dignified`, `badig_msx`, `badig_coco` to `language_dignified`, etc
- Load modules on a non hardcoded, dynamic way, based on a name (ie. the `.module` in `tokenizer.module.py`) and find a way to sort the running order, like the tokenizer running before the emulator. They must talk to each other to define the execution order among other things.  
- Get stdout from openMSX on Windows for monitoring and error reporting.  
- Make the code be read as a long string, not as a list. Line numbers are counted by the numbers of line feeds.  
- Make the build system build generic classic and dignified code with `.bad` and `.asc` extensions, identifying the system somehow.  
- Find a way to deal with partials like `##B` or `.` (partials are needed to ensure the capture of a token that has no intermediary match).  
- Make DignifieR work as a module inside Badig.  
- Consider the case of a basic not having some instructions and preventing some features
  - Like not having `:` to separate instructions or `GOSUB` to make functions
- Make Basic Dignified figure out the system based on the file extension, without the need for `-id`
  - Keep `-id` as a way to force the system regardless of the extension
  - Make an ultra compact code focusing on speed and not readability (join lines, remove spaces, remove variables in NEXT, move functions, etc.)  
  - Give the option for the Infolog class to export a log file.  
  
**Code cleanup**  
- Put `report_output` inside Main class on badig
- Move changing `#` from toggle rem to file number to the classic module on Pass 1
- Remove file load from the `.ini` file. There is no need really.  
- Use variables for the token names.  
- Remove the double inheritance in the Description class in the main code.  
- Change all saved values to saved tokens like in `hard_long_var` 

**Build**  
- Remtag/settings option to turn on/off "full speed when loading" on openMSX.  
- Remtag to pass custom strings to control any aspect of the emulators or other programs when loading.  
  
**DignifieR**  
- Unravel `FOR` is working?  
- Check if multi letter command line arguments need to have any letters. `<>` or `[]`?  
- Find out why `LOCATE X,Y:PRINT` commented and upgrade to `[?](x,y)`.  
    
## Done  
  
**General**  
- Make an environment for VS Code with build, highlight and more.  
  
**Highlighting**  
- Define identifier properly handling errors.   
  
**Language improvements**  
- `REM` and `'` literals capitalizing after conversion.  
- `REM` instruction not capitalizing.  
- If the last function definition has no arguments, all functions loose their arguments in the conversion.  
- Make  variables remember the `~` type (keep long format) and use it on the next occurrences without needing to precede all of them.  
- Investigate variable identifiers separated by spaces joining on the conversion

**Generic improvements**  
- Differentiate Linux version along with Mac and Win. I.e.: the way the emulator is called on Python, it is more like Windows.  
- Fixed buggy settings with boolean values.  
- Remove spaces from all file names and paths.  
- Remove `monitor_exec` and `save_list` from `badig.py` and make it a feature only of their modules.  
- Make the `-ini` argument save an `.ini` file with the current command line arguments as defaults.  
- Create settings specific for each system, ie: Strip `THEN` `GOTO`, change `PRINT` to `?`, etc should have system specific config.  
- Make a way to run the emulator from Badig without needing an IDE build, using the standalone emulator build module.  
- Move the paths to the emulators from `subliebuild.ini` to the `.ini` of the eventual emulator specific build module.  
- Make all default programs configurable outside the code, tokenizers, build, DignifieR, etc.  
- Pass arguments from Badig to the tokenizer as `*args` to decouple them.  
- Better control of `show_output` to the console setting on the build.  
- Make an unique module for each emulator.  
- Make the tokenizer work as a module inside Badig.  
- Remove emulator stuff (like some remtags) from the general build script.  
  - There are remtag mentions in `sublimebuild.py` and `badig_dignified.py`  
- Made remtags exposition for the classic dignified module
- Remtags conflict when exposed ones clashes raises an error
- Add load settings `.xml` to config/remtag on openMSX.  
- Added - D_SPCIAL token  
- Classic module expose command line arguments, has `.ini` and is called again to process the args. 
  - The variables are accessible from the classic module from `self.stg.c_stg.VARIABLE`.  
- If monitor default on the emu interface, it will surpass the build except if using remtag.  

**Code cleanup**  
- Make an `IO` class in the tokenizer.  
- Let the classic module deal with all the tokenizer functions. The main script should only call its class.  
- Wrong: `c_litquo` defined on regex groups on classic module but used directly on the code.  
- Import Infolog module on the classic module and let it deal with its own logging.  
- Make a cleaner way of executing the passes of the classic module.  
- Move the translation characters variables to the Description class.  
- Understand better the operation of the `export_list` setting and arguments and make it simpler.  
- No need: Change the passed `tok` to `data` in the Info class on Badig to make the code clear.  
- Remove `-frb` (`is_from_build`). Is it being used anymore? (all occurrences are commented)  
- Move variable identifier description to classic module
- Changed `[?](x,y)` initialization  

**Explain in the manual**  
- Python version 3.10+  
- Remind Badig v2.0 is incompatible with pre v2.0.  
- Remind of possible python / python3 naming confusion.  
- Emulator needs a machine with disk drive.  
- Remember to install Package Control no Sublime.  
- Remind of path changes in `.sublime_build` Dignified and classic.  
- How to setup syntax scopes on sublime to build automatically.  
- Explain how to download the repo.  
- Mention in the manual to put build settings to automatic
  
