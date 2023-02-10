# Differences from v1.6  
  
## Changes that might break the conversion:  
  
- **General**  
Most assigned identifier names cannot start with numbers or be only numbers.  
  
- **Defines**  
Define variables must now come between parenthesis `()`.  
`PRINT` built in define now is only `[?]`  
  
- **Declares**  
There is no more declaration of standard long named variables.  
Declare only to reserve short names or keep long ones.  
`~` now is used to keep a long name when converting to classic.  
  
- **Functions**  
Now ends with `RET` instead of `RETURN`.  
Functions do not share names with labels anymore.  
  
- **Includes**  
Do not share namespace with other files except for short named variables.  
  
- **Line breaks**  
Line breaks are not supported inside quotations or `REM`s.  
Underscores line break must be separated by spaces from alphanumeric characters.  
  
## (Almost) complete list of changes  
  
**General**  
  
- All spaces are ignored even inside enclosed literals like labels and defines ie: `[ aa ]`.  
- Label report with `>` for jumps and `<` for lines.  
- Recommended use of spaces as indentation for better column error reporting.  
- Update function autocomplete replacing `RETURN` with `RET`.  
- If the `.ini` is not found a new one will be automatically generated and the program will exit.  
- Error now points to the character position (use spaces for indentation or define the tab spaces).  
- Can save lexer and parser token reports.  
- Can export line numbers report.  
- To run batoken.py use  `python -m Modules.msx.msxbatoken` from the badig folder.  
- The Tokenizer can be separated by placing all modules on the same folder as the main file.  
  
**Highlight**  
*Classic/List*  
- List: Differentiate line number addresses from tokens and some labels.  
- Classic: `REM`s highlighting with instruction scope.  
  
*Dignified*  
- Added `RET`.  
- Accepts toggle rems with joined `#a#b` and forbid start with number.  
- Added `EXIT`  
- `[?]` in place of `[?@]` and with define color instead of operator color.  
- Define can be adjacent to `[` with no spaces.  
- Declare now follow all the rules.  
- `input # 1` with separated `#` works correctly.  
- `REM` not highlighting anymore if touching another word character.  
- `AS` no more highlighting even in the middle of a variable like `casa$`.  
- `ENDIF` now scope color of the Dignified exclusive functions.  
- `REM` highlighting with instruction scope.  
- `REM` and `'` not highlighting the next line if ending with `_` or `:`.  
- Removed warning  on `ENDIF` after `DATA` with `_` or `REM` with `_` or `:`.  
- Remtags with indentations now highlighting.  
- Line numbers = error not warnings
   
**Settings**  
- Added TAB length to find the position of the text in columns.  
- Added `-id` to select current working classic system (also on the build).  
- Added JSON with system descriptions.  
- MSX - SlotB changed to ext, exta, extb...(warning if another name).  
- If no path is given the emulator will be executed from the local path.  
- Negative verbose (`-vb -#`) value unify all arguments with `verbose` in the name.  
- `-asc` allows opening classic ASCII code for tokenizing, run and monitor.
  
**Line separating**  
- Dignified separator `_` must be separated from last character if it is a word.  
- Literals (except `DATA`) cannot have `_` at the end to join lines.  
  
**Cleanups**  
- Separate words ending in `X` and `OR` to avoid `XOR` by mistake.  
- Separate hex numbers followed by words beginning with `A` to `F` to avoid mistake.  
- Remove duplicated `:`.  
- Blank lines are always removed except inside rem blocks.  
- All preceding and trailing spaces are removed.  
- There is no more keep general spaces, its remove all or keep one.  
- Indentation is not kept anymore.  
- Lines starting with a number will give an error.  
  
**Remtags**  
- Remtags arguments work even when not on build.  
- Remtags have precedence over command line arguments.  
- Remtags changed. Now have some are built in and a lot are exposed by the modules.  
- `-rtg` or `##BB:help=true` list all available remtags.  
  
**Toggle rems**  
- Can be put together `#a#b#none`.  
- `##` is seen as an exclusive rem, `###` is an error.  
- Cannot start with numbers.  
- Must be declared before it is used.  
- Do not check closing block if told to keep.  
- `#all` keeps everything `#none` remove all. `#none` have precedence.  
  
**Includes**  
- Toggle rems, functions, labels, defines have independent namespaces.  
- Cannot declare same variables on includes.  
- Long names are assigned different short ones across includes to preserve namespace.  
- Warning if same the same hard coded variable is used across includes.  
- Short variables are hardcoded and go cross includes.  
- Declared or converted and reserved long vars have separated namespaces on includes.  
  
**Quotes**  
- Adjacent quotes join automatically even on next line.  
  
**Functions**  
- Can have anything after a function definition.  
- Do not share names with labels anymore.  
- Can take empty arguments.  
- Do not need `arg=arg` on definition anymore.  
- On reports `<` denotes a function definition and `>` a function call.  
  
**Labels**  
- Can have anything after them, loop or regular.  
- Can have anything before loop label close.  
- Do not share names with functions anymore.  
- `EXIT` go to the line after the loop label is closed.  
- On reports `<` denotes a label line, `>` a label jump and `*` a loop labels exit.  
  
**Defines**  
- Define must come before the use on the code.  
- Must use `()` after a define to pass a variable  
- `[?](X,Y)` is the new `LOCATE X,Y:PRINT` define.  
- Definitions can be adjacent to the define instruction.  
- Can define variables in multiple places but they will all be the same.  
- Added `[?](x,y)` for the CoCo.  
- Illegal characters on a define name give a more specific "illegal define name" error.  
- MSX - [?] without variable now adds `0,0` to `locate` to avoid errors.  

**Declares / variables**  
- Do not need `~` to declare variables, just use them.  
- `~` keeps the long named variable when converting.  
- `~` cannot be used on a short named variable.  
- `~` only need to be stated at the first time a variable appears.
- Long named variables are case insensitive.  
- Never assign numbers automatically to short vars.  
- Declare only for assigning explicit short names or reserving them or long names.  
- Declare cannot reserve 1 letter variable.  
- Declare can have a two letter short variable alone to reserve it.  
- Declare can have a long variable alone to reserve it.  
- Declare cannot declare 1 or 2 letter variable as long variables.  
- Declare now take one letter short variable to reserve them.  
- Can be declared anywhere.  
- Hard coded variables are not used by subsequent long variables substitutions.  
- Warning given if short name already assigned is used directly.  
- Warning if short name hard coded and already used by substitution.  
- First 2 chars of kept long vars are taken as hard short var to avoid clash. ie: test = te.  
- It will warn of all the conflicting variable names, long and short.  
- First letters of long vars are treated as hard short vars (because they are operationally the same).  
  
**If**  
- `ENDIF` now removed wherever it appears, can be used anywhere.  
