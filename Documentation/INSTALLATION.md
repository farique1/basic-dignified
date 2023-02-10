# Installation  
  
### Requirements  
To run Basic Dignified you will need:  
- **Python 3.8+**  
  
To be able to **run** and **monitor** (monitoring is available on **MSX** and **Mac**/**Linux** only) the program **execution**, yo will need:
- **openMSX** with an emulated disk drive for the MSX (tested on **v.17.0**)
- **XRoar** for the CoCo. (tested on **v.1.3**)  

You can use any **text editor** to write **Dignified** code and convert it with `badig.py` on the **command line**, but to get the most of the **experience**, with the easy of a **build system**, **syntax highlight** and **more**, you will need to have **installed**:  
- **Sublime Text 3 or 4** with **Package Control** installed.  

### The basic setup  
  
**Download** this repository by clicking on the green `<> Code` button on the **main page** and selecting **Download ZIP** at the bottom. **Unzip** the downloaded file on the **folder** of your choice, it should be named `basic-dignified-main`, and **rename** it to whatever you want. For the purpose of this manual, lets **rename** it to `BasicDignified`.  

If all you want is the **conversion** through the **command line**, including **tokenization**, you are set. See the Basic Dignified [manual](https://github.com/farique1/basic-dignified/blob/main/documentation/BASIC_DIGNIFIED.md) on how to use it.  
  
### Setting up the emulators  
  
While the tokenizers are **provided** with the Suite, the **emulators** are not. The included **interfaces** work with **openMSX** for the **MSX** and **XRoar** for the **CoCo** and you have to install them **independently**.  

> Note that **openMSX** needs a machine with a **disk drive** or a disk drive **extension** to load the program.   

Once you have them **installed** you need to tell Basic Dignified **where** they are. Open the `emulator_interface.ini` file located on the **folder** of the **system** you want to use (`msx` or `coco`) and **add** the path to `emulator_path` in this section depending on your **operating system** (`[DARWIN]` is **MacOS**):

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

### The Sublime Tools  
  
To use Sublime Text to **edit** your code with syntax **highlight**, **snippets completion**, a **build system** and more you need to properly **set it up**.

**Download** and **install** Sublime Text (**not** the DEV build).  
Run it and **install** Package Control (https://packagecontrol.io/installation)

Now you need to **Tell** Sublime Text **where** Basic Dignified is.  

On the **folders** of the system modules (`msx` or `coco`) there is a folder called `Sublime Tools` and **inside** this folder there is another folder with the **system name** (`MSX` or `COCO`). Inside this folder there is a **bunch of files**.  

**Find** the files with the **extension** `.sublime-build`:  
`MSX Basic.sublime-build`  
`MSX Basic Dignified.sublime-build`  
or   
`CoCo Basic.sublime-build`  
`CoCo Basic Dignified.sublime-build`  

**Open** then on a text editor and **change all** the occurrences of `"PATH_TO/BasicDignified/badig.py"` to the path of **your installation** of Basic Dignified. There are **more than one** and they are also **separated** by operating system, change **all** that are **relevant** to the operating system you are using. They are on **blocks** like this:  

```json
},
"windows": {
    "cmd": ["python", "-u", "PATH_TO/BasicDignified/badig.py", 
                            "$file", "--tk_tokenize", "--em_run", "--em_monitor", "-id", "msx"]
},
```
> **Depending** on your installation `"python"` should be `"python3"`.  

> **ATTENTION** **Windows** users, use **forward** slashes (`/`) or **scaped** forward slashes (`//`) instead of the standard **backwards** one (`\`).  

**Now** lets actually **install** the **tools** into Sublime text.  

**Open** Sublime Text, open the `Preferences` **menu** and select `Browse Packages…`. This will **open** a **explorer** window on the `Packages` **folder** of Sublime Text.  

If there is a **folder** called `User`, **open** it, if not, **create** one and open it.  

**Go back** to the Basic Dignified **installation** and move the **contents** of the `Sublime Tools` folder of the **system** you want (you want **only** the contents, **not** the folder itself) inside the `Packages\User\` folder of Sublime Text and **restart** it.  

You can now safely **delete** the `Sublime Tools` folder (that should be **empty**).  

Sublime Text **should** correctly **interpret** the **Dignified** and **classic** Basic files based on their **extension** but you might have to **manually** chose them the first time you **create** or **open** one.  

With a **Dignified** or **classic** Basic file **opened**, click on the **bottom left** of Sublime Text (it should be reading `Plain Text`) and go to `Open all with the current extension as...` at the **top** of the **list**, then go to `User` and **select** the **appropriated** syntax description.  

See [the module tools manual](https://github.com/farique1/basic-dignified/blob/main/documentation/MODULE_TOOLS.md) on how to **use** the Sublime Tools.  
  