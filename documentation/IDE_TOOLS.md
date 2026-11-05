# Code Editor Integration  
 
Although Basic Dignified can be **comfortably** used on a **notepad** and **command line** environment its full **potential** is revealed when **integrated** with an **IDE** or **code editor** like **Sublime Text** or **VSCode**.   

**All** functions of Basic Dignified can be **achieved** and most can be **automated** from **within** them with a few **remtags** and **shortcuts**.  

**Included** on this version is a **full set** of tools for **integration** with **both** editors, including **support** for the **Dignified** and **classic** Basic versions of both included **systems**.  
The **Spectrum** companion adds DZS/AZS syntax, snippets and build
templates, retaining DSP/ASP associations. Its external converter/Python
setup is described in [installation](INSTALLATION.md).

The tools are:  
- A **[Build System](#Build-System)** for the **Dignified** and **classic** versions of Basic.  
- **[Syntax Highlight](#Syntax-Highlight)** for the Dignified and classic versions of Basic.  
- **[Themes](#Themes-and-color-schemes)** based on Boxy Ocean and Monokai with special scopes for **both** Basic versions.  
- A **Theme** simulating the blue **MSX 1 screen** and accompanying **MSX Screen 0 font**.  
- **[Snippets](#Auto-Completion-And-Snippets)** for the Dignified version of Basic.  
- A **[Comment Preference](#Comment-Preference)** for the Dignified version. 
  
> See the [installation](INSTALLATION.md) page on how to **install** these tools.  
  
## Build System  

### VSCode  
  
> Due to the **nature** of the VSCode **build** system, you will need to have the `.vscode` **folder** containing the `tasks.json` of your system **opened** on the editor. For **convenience**, this folder is **provided** on the `VSCode Extension` folder of the Basic Dignified **installation**. If you open your Basic programs as a **folder** in VSCode, you can have `.vscode` as a **subfolder** there. If you want to have build access using single files, you can just `add a folder` containing the **provided** `.vscode` folder ***AS A SUBFOLDER***.

Once everything is **installed** and a program is being coded, the **builds** will be **available** from the `>` icon at the top left of the code window.  
  
There are a number of different build options depending on the kind of Basic you are working on. You can select them from the Command Palette list appearing on the center of the screen.   
  
You can further **refine** the build **behavior** by passing **arguments** with **remtags**, they will **override** the **default** behavior of the **chosen** build variant.  
  
> See the end of the [Basic Dignified usage secton](BASIC_DIGNIFIED.md) for an explanation of the **remtags**.  

For **Spectrum**, merge the supplied `zxspectrum\VSCode Extension\.vscode\tasks.json` into `.vscode/tasks.json`
and set **spectrum-basic.python**, **spectrum-basic.badigPath** and
**spectrum-basic.emulatorPath**. Choose a **Dignified** task for DZS/DSP
and a **Classic** task (`-asc`) for numbered AZS/ASP.
The normal build creates **TAP/TZX**. The **all formats** tasks add Z80/SNA
after installing optional SkoolKit through the explicit installation task,
which uses that **same configured Python**.
The launcher waits for EightyOne; it does not monitor ROM runtime errors.
The VSIX does not bundle Python/converter/engine. A fully integrated
installer remains a separate packaging step.
  
### Sublime Text  
  
Once everything is **installed** and a program is being coded, the **builds** will be **available** from the `Tools > Build System` menu and are called:  
  
`MSX Basic`  
`MSX Basic Dignified`  
or  
`CoCo Basic`  
`CoCo Basic Dignified`  

**Spectrum** supplies `Spectrum.sublime-build`. Open the converter root
as the project folder and use Python 3.8+ on PATH. The default build is for
DZS/DSP and produces TAP/TZX; use the classic variant for AZS/ASP.

The best approach is to leave the **build type** on `automatic`, this will use the **syntax scopes** and the extensions to figure out the **correct** build.    
  
To **run** the build just press **CONTROL-B**/**COMMAND-B**.  
  
Each of the **builds** have some **variants** that can be chosen by pressing **CONTROL-SHIFT-B**/**COMMAND-SHIFT-B**. They depend on the kind of Basic you are working on. Once they are **chosen** they will be used as the **default** build until Sublime is **closed** or another variant is **chosen**.  
  
You can further **refine** the build **behavior** by passing **arguments** with **remtags**, they will **override** the **default** behavior of the **chosen** build variant.  

> See the end of the [Basic Dignified usage secton](BASIC_DIGNIFIED.md) for an explanation of the **remtags**.  
  
## Syntax Highlight  
  
**Two** pretty decent **syntax highlights**, one for the **Dignified** and one for the **classic** version are available on **both** systems.   
Spectrum syntax also highlights **REMX** and the **graphic/UDG escapes**
inside strings and REM text. The [character table](BASIC_DIGNIFIED.md#zx-spectrum-characters)
shows the actual byte values; fonts do not redefine Spectrum UDG bitmaps.
  
> The **list** exported by the MSX **tokenizer** uses the **classic** version.  

## Themes and color schemes  
  
Several **themes** and **color schemes** are included with some based on **Monokai**, **Boxy Ocean** and **Mariana**. They **improve** the syntax highlight (classic and Dignified) with **scopes** specific for the Dignified code: `define`, `declare`, labels, errors and warnings.  

There are also a **light** and a **dark** color scheme using the **MSX** colors and
for the truly **adventurous** there are themes **mimicking** the blue **MSX 1 screen** and the **green**/**orange** CoCo screen. Also there are accompanying **fonts** representing the ones found on the **original** systems.  
These themes/fonts remain system-specific; the Spectrum companion does not
claim a bundled Spectrum font or additional screen theme.
  
## Auto Completion And Snippets  
  
Snippets for auto completion for:  
 `FOR-NEXT-STEP`  
 `IF-THEN-ELSE`  
 `FUNC-RET`  
 `PMODE-SCREEN-PCLS` **(CoCo only)**  
 `SCREEN-WIDTH-KEY OFF-COLOR` **(MSX only)**  
 `LOCATE-PRINT` **(MSX only)**  
  
A snippet for the creation of the standard **remtags**.  
Spectrum snippets include single-letter **FOR**, **PRINT AT**, string
**DECLARE** aliases, **UDG bitmap definition** and **REMX**.
Native **DEF FN** and literal-byte snippets are also included.
The **Dignify numbered AZS** task writes `${file}.dignified.DZS`, not the
original source. This module task needs the suite folder as the workspace
root (or an adjusted task cwd). Existing output is refused unless the CLI
is explicitly invoked with **--force**.
  
## Comment Preference  
  
Set `##` as the **default comment** of the Dignified Basic.  
`##` is a Dignified **comment** that is **deleted** when the code is **converted** to the classic version.  
There is **no block comment** but **all lines** selected will be **commented**.  
  
There is no **classic Basic** comment preference as I couldn't find a way to **insert** the `REM` or `'` **AFTER** the line number.
