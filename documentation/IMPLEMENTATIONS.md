# Implementation Ideas and Known Bugs  
  
Not all topics presented here are going to be implemented. Some are just ideas and brainstorms.  
  
## Known Bugs  
**Highlighting**  
- Toggles, labels, ~, declares, functions and long named variables starting with a number not highlighting as error

**Conversion**  
- Toggles, labels, ~, declares, functions and long named variables starting with a number not giving an error and converting to erratic results.  
- If `ENDIF` after a `:` on another line, `ENDIF` will be removed and the line after it will be joined.  
  
## Changes to this version
*v2.2*
- Removed `systems.json`.  
- The information about the system name and extension are now on the system language module.  
- Special extensions like the `.lst` list extension are now defined on the module that uses them, like the tokenizer, in this case.  
- Changed the terminal panel presentation in the VSCode tasks to `dedicated`.   
- Better handling of file saving (including the `export_file` remtag). Can now use relative paths and paths without files.  
- Fixed bug related to the scope name of the syntax configuration on the Sublime package.  
  
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

**Code cleanup**  
- Put `report_output` inside Main class on badig
- Move changing `#` from toggle rem to file number to the classic module on Pass 1
- Remove file load from the `.ini` file. There is no need really.  
- Use variables for the token names.  
- Remove the double inheritance in the Description class in the main code.  
- Change all saved values to saved tokens like in `hard_long_var` 

**Build**  
- Remtag/settings option to turn on/off "full speed when loading" on openMSX.  
- Or maybe a system to pass custom strings to control any aspect of the emulators o other programs when loading.  
  
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
  
