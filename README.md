<img src="https://github.com/farique1/basic-dignified/blob/main/images/BasicDignifiedSuite_Logo-160.png" alt="Basic Dignified" width="378" height="160">  
  
# Basic Dignified Suite  
**v2.2.1**  
    
> The **2.0+ versions** of the Basic Dignified Suite is slightly **incompatible** with the **previous versions** so old Dignified code must be **updated** accordingly. A list of incompatibilities is available [here](https://github.com/farique1/basic-dignified/blob/main/documentation/DIFFERENCES.md).  
    
**Basic Dignified** is a way for programming classic 8bit computer Basics on a modern, friendly paradigm. MSX and CoCo Basics are supported but more can be added through modules.

**ZX-81 addition:** this repository also includes a ZX-81 module. The original MSX and CoCo documentation is retained, with ZX-81-specific information added separately.
  
With **Basic Dignified** you can program for the included systems on a modern environment using Sublime Text or Visual Studio Code with syntax highlight, build systems, snippets and more.  
  
**Basic Dignified** improves and adds to the classic Basic, keeping the syntax as close as possible to the original, making the learning curve almost inexistent (the only requirement is the use of labels instead of line numbers), while adding a lot of quality of life improvements that can be used or not. The output is converted to the classic Basics and can run automatically on an emulator.  
  
Dignified Basic is written **without line numbers**, can be **indented**  and have **lines broken**, can use variables with **long names**, have macros **defined** and external files **included**, has a kind of **function** construct, can use **Unicode** special characters analogues to the original character set, as well as **rem toggles**, **true** and **false** statements, **compound arithmetic** operators and much more.  The conversion is customizable with controls for **line numbers**, **spaces**, **code cleanup** and more.

**ZX-81 note:** Unicode translation is not implemented for this module; its tokenizer supports ASCII spellings, graphics escapes and literal byte escapes instead.
  
The suite is designed to be very **modular**, implementing any **flavor** of Basic through modules that describe their **unique** characteristics. The **modules** are programmed **independently** and loaded as needed.  

**External** tools like **tokenizers** and **emulators** to run and debug the code can be **easily** added through **individual** modules inside each system ecosystem.  
  
The module and tools can add their own **commands** and **directives** to the overall control of Basic Dignified.

The suite can be used directly from the terminal, through command line arguments, but it is best experienced inside  **IDEs** and code editors like **Sublime Text**, **VSCode** and others.  

By default, the suite comes with two modules, one for **MSX Basic** and one for **Color Computer Basic** and **YOU** can make the next module. **ZX Spectrum** or **Commodore 64**, anyone?
  
The included modules contains the **Basic language description**, control for included **tokenizers**, the ability run the code on **emulators** and support for **Visual Studio Code** and **Sublime Text**  with **build system**, **syntax highlight** for the **Dignified** and **Classic** Basic versions as well as **themes**, **snippets**, **completions** and more.

The additional ZX-81 module has Visual Studio Code and Sublime Text integrations with syntax highlighting, builds and snippets. Its emulator interface launches EightyOne with tokenized `.p` files.

>**Beyond** the Dignified code, Basic Dignified can open **classic** ASCII code to **tokenize**, **execute**, **monitor** and more.  

>On **openMSX** on the **Mac** or **Linux**, the code can be **monitored** during execution and errors are **reported** back to the correct line in the Dignified code.  

> On **MSX**, to help **kickstart** you on the **Dignified** thing, try **MSX Basic DignifieR** to **convert** a **classic** Basic to the **Dignified** format.  

## ZX-81 Quick Start

From the repository root, convert a Dignified source to numbered `.AZX` and tokenized `.p`:

```console
python badig.py examples/zx81/zx81-intro.DZX -id zx81
```

For an existing numbered listing, use `python badig.py program.AZX -id zx81 -asc`. Add `--tk_ascii_only` to a Dignified conversion for ASCII output only, or `--em_run` to tokenize and launch EightyOne.

The ZX-81 module supports native `PRINT AT`, the `[?](row,column)` shorthand, long-variable allocation from `Z` down to `A`, renumbering of numbered listings, `remx` machine code `REM` lines, and literal byte escapes `\{XX}` compatible with Go81 `p2txt` listings, including inside strings and `REM`.

See the [ZX-81 module guide](documentation/MODULE_TOOLS.md#zx-81-usage-and-byte-escapes) for conversion helpers, byte escapes, explicit hidden numeric values, and current limitations.

The [drawn character reference](documentation/BASIC_DIGNIFIED.md#zx-81-graphics-escape-and-drawing) shows graphic glyphs beside their source spellings. See the [ZX-81 audit and remaining fixes](documentation/IMPLEMENTATIONS.md#zx-81-audit-2026-11-03) before treating the module as complete.
  
---  
### [Installation](https://github.com/farique1/basic-dignified/blob/main/documentation/INSTALLATION.md)  
  
### [Using Basic Dignified and the Included Modules (MSX and CoCo)](https://github.com/farique1/basic-dignified/blob/main/documentation/BASIC_DIGNIFIED.md)

The guide also includes additional ZX-81 sections.
  
### [Additional Features of the Included Modules (Language, Tokenizers and Emulators)](https://github.com/farique1/basic-dignified/blob/main/documentation/MODULE_TOOLS.md)  

### [Visual Studio Code and Sublime Text Integration (Syntax Highlight, Snippets, Build System, etc)](https://github.com/farique1/basic-dignified/blob/main/documentation/IDE_TOOLS.md)

### [Creating Modules for Other Systems (SOON)](https://github.com/farique1/basic-dignified/blob/main/documentation/NEW_MODULES.md)
  
### [Differences and Incompatibilities with v1.6](https://github.com/farique1/basic-dignified/blob/main/documentation/DIFFERENCES.md)  
  
### [Implementation Ideas, changes and Known Bugs](https://github.com/farique1/basic-dignified/blob/main/documentation/IMPLEMENTATIONS.md)  

#### Support Tools: [MSX Basic Tokenizer](https://github.com/farique1/basic-dignified/blob/main/documentation/BATOKEN.md), [MSX DignifieR](https://github.com/farique1/basic-dignified/blob/main/documentation/DIGNIFIER.md) and [CoCo to CAS](https://github.com/farique1/basic-dignified/blob/main/documentation/COCOTOCAS.md)  

ZX-81 support tool: [ZX81 Basic DignifieR](documentation/DIGNIFIER.md#zx81-basic-dignifier), to convert numbered ZX-81 programs to the Dignified format.


---  
  
> **Basic Dignified** runs on **Python 3.8+**.  
> No external dependencies are needed.  
  
>**Basic Dignified** is constantly evolving so please report any misbehavior.  
  
> As always, **Basic Dignified** is offered as is, with no guaranties whatsoever. Use at your own discretion.  


Having said that, enjoy and send feedback.  
  
Thanks.  
  
---  
  
 ![#CGKcomparison.png](https://github.com/farique1/basic-dignified/blob/main/images/CGKcomparison.png)  
  