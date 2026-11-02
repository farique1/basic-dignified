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
  
The tokenizers are **provided** with the Suite, while emulators must be installed **independently**. The included interfaces support **openMSX** for MSX, **XRoar** for CoCo, and **EightyOne** for ZX-81.

> Note that **openMSX** needs a machine with a **disk drive** or a disk drive **extension** to load the program.   

Once you have them **installed** you need to tell Basic Dignified **where** they are. Open `emulator_interface.ini` in the system folder you want to use (`msx`, `coco`, or `zx81`) and set `emulator_path` for your operating system (`[DARWIN]` is **MacOS**):

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
.\zx81\convert-zx81.ps1 zx81\samples\zx81-intro
```

```bash
bash zx81/convert-zx81.sh zx81/samples/zx81-intro
```

Both helpers write the numbered `.AZX` and tokenized `.p` beside the source file.

Now Basic Dignified can **run** your program after the **conversion**.
  
## Code Editors  

To write your program with the help of syntax **highlighting**, **snippets completion**, a **build system** and more you need to properly **set it up** on a code editor.  
There is currently support for **Visual Studio Code** and **Sublime Text**.  

Choose the editor package for the system you want to use: **MSX**, **CoCo**, or **ZX-81**.

### The VSCode Extension

If you don't have VS Code, **download** and **install** it.  

To install a VS Code extension, open **Extensions > ... > Install from VSIX...** and choose the matching file from your Basic Dignified installation:

- MSX: `msx/VSCode Extension/basic-dignified-msx-2.0.0.vsix`
- CoCo: `coco/VSCode Extension/basic-dignified-coco-2.0.0.vsix`
- ZX-81: `zx81/VSCode Extension/basic-dignified-zx81-2.0.0.vsix`

Restart VS Code and open **Extension Settings** for the installed system extension. Set its `badigPath` property to your `badig.py` path (for example, `D:\BasicDignified\badig.py`) and set the Python executable if it is not `python`.
  
VS Code associates the system-specific source extensions with their language grammars. If needed, use **Configure File Association** to select the matching classic or Dignified language. For ZX-81, `.DZX` uses `ZX-81 Basic Dignified` and `.AZX` uses `ZX-81 BASIC`; copy its provided `.vscode/tasks.json` into your workspace to enable the builds.
  
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

Each system's Sublime package is under its module's `Sublime Package` folder. The detailed walkthrough below uses MSX; for ZX-81, use `zx81/Sublime Package/BasicDignifiedZX81` and follow the ZX-81-specific setup above.

For MSX, open the files inside its `build` folder:
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

Copy the package folder for the system you want into Sublime Text's `Packages\User\` folder and restart Sublime Text. For ZX-81, copy the complete `BasicDignifiedZX81` folder and update the `badig.py` path in both build files as described above.

Sublime Text **should** correctly **interpret** the **Dignified** and **classic** Basic files based on their **extension** but you might have to **manually** chose them the first time you **create** or **open** one. With a **Dignified** or **classic** Basic file **opened**, click on the **bottom left** of Sublime Text (it should be reading `Plain Text`) and go to `Open all with the current extension as...` at the **top** of the **list**, then go to `User` and **select** the **appropriated** syntax description (`MSX Basic classic` or `MSX Basic Dignified`).  

See [the code editor integration section](https://github.com/farique1/basic-dignified/blob/main/documentation/IDE_TOOLS.md) on how to **use** the Sublime Package.  
  