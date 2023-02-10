# New Modules  

> A complete guide on how to implement new systems is coming soon.  
> This is only a small overview.  
  
Modules for **new systems** should be placed on **folders** named with their **system ID**.  
The **language** module for the **classic** system must be named `badig_SYSTEM-ID.py`.  
The **tools** module for the **classic** system must be named `tools_SYSTEM-ID.py`.  

The **language** module **describes** and adds **control** to the **conversion** fom the **Dignified** to the **classic** versions.  
The **tools** module **control** all **interfaces** associated with **programs** helping the **conversion** like **tokenizers** and **emulators**.  
The **interfaces** directly **control** the **external programs** like **tokenizers** and **emulators**, making a **bridge** between them and Basic Dignified and adding **configurations** and **features**.  

The **MSX folder** opened with its **files** as an example of a **typical** module.

```  
|- documentation  
|- examples  
|- images  
|- coco  
|- msx  
   |- msxbatoken
   |  badig_msx.ini
   |  badig_msx.py
   |  emulator_interface.ini
   |  emulator_interface.py
   |  msxbader.py
   |  openmsx_output.tcl
   |  tokenizer_interface.ini
   |  tokenizer_interface.py
   |  tools_msx.py
|- support  
|  badig.py  
```  
  
A **schematic** of the **relationship** between the **files** of Basic Dignified and the **MSX** module.  
<img src="https://github.com/farique1/basic-dignified/blob/main/images/filerelationsmsx.png" alt="File relations" width="480">  
  
The **description** for the system are on `\support\systems.json`:  
  
```json  
[  
 {  
   "msx": {  
      "name": "MSX",  
      "dig_ext": ".dmx",  
      "asc_ext": ".amx",  
      "bin_ext": ".bmx",  
      "lst_ext": ".lmx"  
   },  
   "coco": {  
      "name": "Color Computer",  
      "dig_ext": ".dcc",  
      "asc_ext": ".acc",  
      "bin_ext": ".bcc",  
      "lst_ext": ".lcc"  
    },  
   "spec": {  
      "name": "ZX Spectrum",  
      "dig_ext": ".dzs",  
      "asc_ext": ".azs",  
      "bin_ext": ".bzs",  
      "lst_ext": ".lzs"  
   },  
   "c64": {  
      "name": "Commodore 64",  
      "dig_ext": ".d64",  
      "asc_ext": ".a64",  
      "bin_ext": ".b64",  
      "lst_ext": ".l64"  
   }  
}  
]  
```  
  
Each system information is composed of:  
- *System ID*  
  - *System name*  
  - *Dignified extension*  
  - *ASCII extension*  
  - *Binary extension*  
  - *List extension*  
  

The structure of the lexer and parser on the main Basic Dignified and MSX module:  

### Lexer  
- **Lex**  
  - Get tokens  
  - Token errors  
  - Adjust token values
  - Get REM blocks and lines  
  - Get quotes  
  - `Classic module`  
    - Process DATA lines

### Parser
- Initialize
  - `Classic module`
    - Add [?] to the DEFINE dictionary
- **Pass 1**  
  - Remove REM TOGGLES
  - Dignified instructions
    - EXIT
    - INCLUDE
    - ENDIF
    - DEFINE
    - DECLARE
    - KEEP
    - FUNC
    - RET
  - Replace DEFINES
  - `Classic module`
    - Convert _ to CALL
    - Convert identifier to _ identifier
- **Pass 2**  
  - Replace function calls
  - Get Labels
    - Jump labels
    - Label lines
    - Loop return
    - Loop EXIT
  - `Classic module`
> - Post pass  
    - Check FUNC and label closing errors
- **Pass 3**  
  - Add INCLUDE
  - `Classic module`
    - Get hard variables
  - Adjust lines
    - Add REM blocks
    - Remove excess NEWLINES
    - Remove excess :
    - Remove NEWLINE after _
    - Remove NEWLINE after :
    - Remove NEWLINE before :
    - Remove NEWLINE after label lines
    - Remove NEWLINE after function definitions
    - Join strings on the same line
    - Join strings on the previous line
- **Pass 4**  
- - Apply header
  - Get labels line numbers and more info
    - Label lines
    - Jump labels
    - EXIT command
  - Get functions line numbers and more info
    - Function definitions
    - Function calls
  - Add line number
  - `Classic module`  
    - Process variables
> - Post pass  
    - Replace jump placeholders for line numbers  
    - Replace EXIT command placeholders for line numbers  
    - Replace function call placeholders for line   numbers  
- **Pass 5**  
  - `Classic module`
    - Convert ? to/from PRINT
    - Strip THEN
    - Strip GOTO
    - Replace unary and assignment operator
    - Replace TRUE and FALSE
    - Translate Unicode to ASCII 
  - Capitalize
- **Generate**  
  - Check translated characters
  - Process a line
    - `Classic module`
      - Separate X from OR
      - Separate hex numbers from A-F words
    - Add space before token
    - Add space after token
  - Add label report to the end of the line
  - Add a linefeed to the end of the line
  - Check line size

<!-- 
Note:
Standardize `em_run` and `tk_tokenize` arguments when available so the build systems are compatible. -->