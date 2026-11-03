# Installation  
  
### Requirements  
To run Basic Dignified you will need:  
- **Python 3.8+**  
  
To be able to **run** and **monitor** (monitoring is available on **MSX** and **Mac**/**Linux** only) the program **execution**, you will need:
- **openMSX** with an emulated disk drive for the MSX (tested on **v.17.0**)
- **XRoar** for the CoCo. (tested on **v.1.3**)  
- **EightyOne** for the ZX-81. The ZX-81 module defaults to `C:\zeddy\EightyOne.exe` on Windows.

You can use any **text editor** to write **Dignified** code and convert it with `badig.py` on the **command line**, but to get the most of the **experience**, with the easy of a **build system**, **syntax highlight** and **more**, you will need to have **installed**:  
- **Sublime Text 3 or 4** with **Package Control**.  
and/or  
- **Visual Studio Code**. 

### Basic setup  
  
**Download** this repository by clicking on the green `<> Code` button on the **main page** and selecting **Download ZIP** at the bottom. **Unzip** the downloaded file on the **folder** of your choice, it should be named `basic-dignified-main`, and **rename** it to whatever you want. For the purpose of this manual, lets **rename** it to `BasicDignified`.  

If all you want is the **conversion** through the **command line**, including **tokenization**, you are set. See the Basic Dignified [manual](https://github.com/farique1/basic-dignified/blob/main/documentation/BASIC_DIGNIFIED.md) on how to use it.  
  
### Setting up the emulators  
  
While the tokenizers are **provided** with the Suite, the **emulators** are not. The included **interfaces** work with **openMSX** for the **MSX** and **XRoar** for the **CoCo** and you have to install them **independently**.

**ZX-81 addition:** install EightyOne independently to use this module's emulator launcher.

> Note that **openMSX** needs a machine with a **disk drive** or a disk drive **extension** to load the program.   

Once you have them **installed** you need to tell Basic Dignified **where** they are. Open the `emulator_interface.ini` file from the **folder** of the **system** you want to use (`msx` or `coco`) and **add** the path to `emulator_path` depending on your **operating system** (`[DARWIN]` is **MacOS**):

```INI
[WINDOWS]
emulator_path = 

[DARWIN]
emulator_path = 

[LINUX]
emulator_path = 
```
The path must be an **absolute** path with the **executable** included (`.exe` for **Windows** and `.app` for **MacOS**).  
ie: `emulator_path = D:\Emulators\openMSX\openmsx.exe`  

For ZX-81 on Windows, `zx81/emulator_interface.ini` already points to `C:\zeddy\EightyOne.exe`. If EightyOne is installed elsewhere, change the path in its `[WINDOWS]` section. The ZX-81 run task tokenizes to `.p` and passes that file to EightyOne.

To convert a ZX-81 program from the repository root without launching EightyOne, pass its base name (without `.DZX`) to the helper for your shell:

```powershell
.\zx81\convert-zx81.ps1 examples\zx81\zx81-intro
```

```bash
bash zx81/convert-zx81.sh examples/zx81/zx81-intro
```

Both helpers write the numbered `.AZX` and tokenized `.p` beside the source file.

A numbered classic listing saved as `.DZX` is renumbered into a new `.AZX` and tokenized, without changing the source; for example, `.\zx81\convert-zx81.ps1 game` for `game.dzx`. On case-sensitive filesystems the Bash helper requires the `.DZX` suffix in uppercase.

PowerShell also accepts explicit source extensions, for example `.\zx81\convert-zx81.ps1 game.AZX`. It appends `.DZX` only when no extension is present. **Before conversion it deletes the destination `.p`, if one exists**; a failed conversion therefore does not preserve the previous binary. Text sources are retained.

To tokenize a Go81 `p2txt` or other numbered listing directly, keep it as `.AZX` and run from the repository root:

```console
python badig.py game.AZX -id zx81 -asc --tk_tokenize
```

No additional Python packages are needed for the ZX-81 tokenizer. Literal `\{XX}` bytes are supported in code, strings, and `REM`; see [the ZX-81 module guide](MODULE_TOOLS.md#zx-81-usage-and-byte-escapes) for the syntax and hidden numeric values. Generating `.AZX` and `.p` does not require an emulator.

Now Basic Dignified can **run** your program after the **conversion**.
  
## Code Editors  

To write your program with the help of syntax **highlighting**, **snippets completion**, a **build system** and more you need to properly **set it up** on a code editor.  
There is currently support for **Visual Studio Code** and **Sublime Text**.  

> The instructons below mentions the `MSX`. Replace `MSX` with `CoCo` if you want to set up the **CoCo** module.

**ZX-81 addition:** use the dedicated ZX-81 setup sections below rather than substituting ZX-81 into the original MSX/CoCo walkthrough.

### The VSCode Extension

If you don't have VS Code, **download** and **install** it.  

To **install** the extension, **run** VSCode, click on the **Extensions** icon (on the left side) and click on the `...` at the top right of the Extensions panel. Select `Install from VSIX...` and open the `basic-dignified-msx-2.0.0.vsix` file located inside `VSCode Extension` on the **folder** of the system module (`msx` or `coco`) of your Basic Dignified installation.

The system-specific VSIX paths are:

- MSX: `msx/VSCode Extension/basic-dignified-msx-2.0.0.vsix`
- CoCo: `coco/VSCode Extension/basic-dignified-coco-2.0.0.vsix`
- ZX-81: `zx81/VSCode Extension/basic-dignified-zx81-2.0.0.vsix`

**Restart** VSCode, find `Basic Dignified: MSX` on the **Extension** panel. Click on the **gear** icon and select `Extension Settings`. On the settings page, enter the **path** to the `badig.py` file on **your** installation (ie. `D:\BasicDignified\badig.py`) and change the name of your Python **executable** if needed (might be `python`, `python3` or other).
  
VSCode **should** correctly **interpret** the **Dignified** and **classic** Basic files based on their **extension** but you might have to **manually** chose them the first time you **create** or **open** one. With a **Dignified** or **classic** Basic file **opened**, click on the **bottom left** of VSCode (it should be reading `Plain Text`), select `Configure File Assiciation for '.xxx'...` and **select** the **appropriated** syntax description (`MSX Basic classic` or `MSX Basic Dignified`).

For ZX-81, `.DZX` uses `ZX-81 Basic Dignified` and `.AZX` uses `ZX-81 BASIC`; copy its provided `.vscode/tasks.json` into your workspace to enable the builds.
  
See [the code editor integration section](https://github.com/farique1/basic-dignified/blob/main/documentation/IDE_TOOLS.md) on how to **use** the VSCode extension.  
  
#### ZX-81 VS Code extension

Install `zx81/VSCode Extension/basic-dignified-zx81-2.0.0.vsix` using **Extensions > ... > Install from VSIX...**, then restart VS Code. In the extension settings, set `zx81-basic-dignified.badigPath` to this installation's `badig.py` and set `zx81-basic-dignified.pythonInterpreter` if your Python command is not `python`.

Copy `zx81/VSCode Extension/.vscode/tasks.json` into the `.vscode` folder of your program workspace. This exposes tasks to convert a `.DZX` file to ASCII only, tokenize it to `.p`, or run it in EightyOne. The extension associates `.DZX` with ZX-81 Basic Dignified and `.AZX` with numbered classic BASIC; `.p` is a binary file, not a text grammar.

#### ZX-81 Sublime package

Copy `zx81/Sublime Package/BasicDignifiedZX81` into Sublime Text's `Packages/User/` folder. In both files in `BasicDignifiedZX81/build`, replace every `PATH_TO/BasicDignified/badig.py` with the full path to your `badig.py`. On Windows, use forward slashes or escaped backslashes. Set the EightyOne path in `zx81/emulator_interface.ini` if it is not `C:\zeddy\EightyOne.exe`.

The package provides `ZX81 Basic Dignified` and `ZX81 Basic classic` builds, syntax highlighting for `.DZX` and `.AZX`, and Dignified snippets. If Sublime does not select a syntax automatically, choose `ZX-81 Basic Dignified` for `.DZX` or `ZX-81 BASIC` for `.AZX` from the syntax selector.

### The Sublime Package

If you don't have Sublime Text, **download** and **install** it (**not** the DEV build).  
Run it and **install** Package Control (https://packagecontrol.io/installation)

Now you need to **tell** Sublime Text **where** Basic Dignified is.  

Inside the **folder** of the system module (`msx` or `coco`), there is a folder called `Sublime Package`. **Inside** `Sublime Package` go to `BasicDignifiedMSX` > `Build`.

**Open** the files inside the `build` folder on a text editor:
`MSX Basic.sublime-build`  
and  
`MSX Basic Dignified.sublime-build`  

And **change all** the occurrences of `"PATH_TO/BasicDignified/badig.py"` with the path of **your installation** of Basic Dignified (ie. `D:\BasicDignified\badig.py`). There are **more than one** and they are also **categorized** by operating system, change **all** that are **relevant** to the operating system you are using. They are on **blocks** similar to:  

```json
},
"windows": {
    "cmd": ["python", "-u", "PATH_TO/BasicDignified/badig.py", 
                            "$file", "--tk_tokenize", "--em_run", "--em_monitor", "-id", "msx"]
},
```
> **Depending** on your installation `"python"` may be `"python3"`.  

> **ATTENTION** **Windows** users, use **forward** slashes (`/`) or **scaped** backward slashes (`\\`) instead of the standard single **backwards** one (`\`).  

**Now** lets actually **install** the **package** into Sublime text.  

**Open** Sublime Text, then open the `Preferences` **menu** and select `Browse Packages…`. This will **open** a **explorer** window on the `Packages` **folder** of Sublime Text.  

If there is a **folder** called `User`, **open** it, if not, **create** one and open it.  

**Go back** to the Basic Dignified **installation** and move the **contents** of the `Sublime Tools` folder of the **system** you want (you want only the **contents**, **not** the folder itself) inside the `Packages\User\` folder of Sublime Text and **restart** it.

**Path clarification:** the original instructions call this folder `Sublime Tools`; in the current repository the editor packages are under `Sublime Package`. For ZX-81, copy the complete `BasicDignifiedZX81` folder and update the `badig.py` path in both build files as described in the dedicated ZX-81 section above.

Sublime Text **should** correctly **interpret** the **Dignified** and **classic** Basic files based on their **extension** but you might have to **manually** chose them the first time you **create** or **open** one. With a **Dignified** or **classic** Basic file **opened**, click on the **bottom left** of Sublime Text (it should be reading `Plain Text`) and go to `Open all with the current extension as...` at the **top** of the **list**, then go to `User` and **select** the **appropriated** syntax description (`MSX Basic classic` or `MSX Basic Dignified`).  

See [the code editor integration section](https://github.com/farique1/basic-dignified/blob/main/documentation/IDE_TOOLS.md) on how to **use** the Sublime Package.  
  