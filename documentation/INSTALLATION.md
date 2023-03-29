# Installation  
  
### Requirements  
To run Basic Dignified you will need:  
- **Python 3.8+**  
  
To be able to **run** and **monitor** (monitoring is available on **MSX** and **Mac**/**Linux** only) the program **execution**, you will need:
- **openMSX** with an emulated disk drive for the MSX (tested on **v.17.0**)
- **XRoar** for the CoCo. (tested on **v.1.3**)  

You can use any **text editor** to write **Dignified** code and convert it with `badig.py` on the **command line**, but to get the most of the **experience**, with the easy of a **build system**, **syntax highlight** and **more**, you will need to have **installed**:  
- **Sublime Text 3 or 4** with **Package Control**.  
and/or  
- **Visual Studio Code**. 

### Basic setup  
  
**Download** this repository by clicking on the green `<> Code` button on the **main page** and selecting **Download ZIP** at the bottom. **Unzip** the downloaded file on the **folder** of your choice, it should be named `basic-dignified-main`, and **rename** it to whatever you want. For the purpose of this manual, lets **rename** it to `BasicDignified`.  

If all you want is the **conversion** through the **command line**, including **tokenization**, you are set. See the Basic Dignified [manual](https://github.com/farique1/basic-dignified/blob/main/documentation/BASIC_DIGNIFIED.md) on how to use it.  
  
### Setting up the emulators  
  
While the tokenizers are **provided** with the Suite, the **emulators** are not. The included **interfaces** work with **openMSX** for the **MSX** and **XRoar** for the **CoCo** and you have to install them **independently**.  

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

Now Basic Dignified can **run** your program after the **conversion**.  
  
## Code Editors  

To write your program with the help of syntax **highlighting**, **snippets completion**, a **build system** and more you need to properly **set it up** on a code editor.  
There is currently support for **Visual Studio Code** and **Sublime Text**.  

> The instructons below mentions the `MSX`. Replace `MSX` with `CoCo` if you want to set up the **CoCo** module.  

### The VSCode Extension

If you don't have VS Code, **download** and **install** it.  

To **install** the extension, **run** VSCode, click on the **Extensions** icon (on the left side) and click on the `...` at the top right of the Extensions panel. Select `Install from VSIX...` and open the `basic-dignified-msx-2.0.0.vsix` file located inside `VSCode Extension` on the **folder** of the system module (`msx` or `coco`) of your Basic Dignified installation.  

**Restart** VSCode, find `Basic Dignified: MSX` on the **Extension** panel. Click on the **gear** icon and select `Extension Settings`. On the settings page, enter the **path** to the `badig.py` file on **your** installation (ie. `D:\BasicDignified\badig.py`) and change the name of your Python **executable** if needed (might be `python`, `python3` or other).  
  
VSCode **should** correctly **interpret** the **Dignified** and **classic** Basic files based on their **extension** but you might have to **manually** chose them the first time you **create** or **open** one. With a **Dignified** or **classic** Basic file **opened**, click on the **bottom left** of VSCode (it should be reading `Plain Text`), select `Configure File Assiciation for '.xxx'...` and **select** the **appropriated** syntax description (`MSX Basic classic` or `MSX Basic Dignified`).  
  
See [the code editor integration section](https://github.com/farique1/basic-dignified/blob/main/documentation/IDE_TOOLS.md) on how to **use** the VSCode extension.  
  
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

Sublime Text **should** correctly **interpret** the **Dignified** and **classic** Basic files based on their **extension** but you might have to **manually** chose them the first time you **create** or **open** one. With a **Dignified** or **classic** Basic file **opened**, click on the **bottom left** of Sublime Text (it should be reading `Plain Text`) and go to `Open all with the current extension as...` at the **top** of the **list**, then go to `User` and **select** the **appropriated** syntax description (`MSX Basic classic` or `MSX Basic Dignified`).  

See [the code editor integration section](https://github.com/farique1/basic-dignified/blob/main/documentation/IDE_TOOLS.md) on how to **use** the Sublime Package.  
  