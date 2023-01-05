# Installation  
  
### Requirements  
To run Basic Dignified you will need:  
- **Python 3.10+**  
  
You can use any **text editor** to write Dignified code and convert it with **Basic Dignified** on the **command line**, but to get the most of the **experience** with a **build system**, **syntax highlight** and **more**, you will need to have **installed**:  
- **Sublime Text 3 or 4**  
- **openMSX**  
  
### The basic setup  
  
**Download** this repository by clicking on the green `<> Code` button on the **main page** and selecting **Download ZIP** at the bottom. **Unzip** the downloaded file on the **appropriated** folder of your choice.  
If all you want is the **conversion** through the **command line**, you are set. See the Basic Dignified [manual](https://github.com/farique1/basic-dignified/blob/master/Documentation/BASIC_DIGNIFIED.md) on how to use it.  
  
### The main programs  
  
The main **converter** is in the root folder, it's called `badig.py`.  
The **tokenizer** and **DignifieR** are in `\BasicDignified\Modules\msx\`.  
To run the **tokenizer** from the **root** folder or to use it as an **standalone** program see it's [manual](https://github.com/farique1/basic-dignified/blob/master/Documentation/TOKENIZER.md).  
  
### The Sublime Tools (MSX)  
  
Preparing **Sublime Text**:  
Enter the path to the **current** location of `\BasicDignified\sublimebuild.py` on the files:  
`MSX Basic.sublime-build`  
`MSX Basic Dignified.sublime-build`  
On the path `\BasicDignified\Sublime Tools\MSX\`  
  
Change `PATH_TO/BasicDignified/sublimebuild.py` to your path on **every** line like:  
`"cmd": ["python", "-u", "PATH_TO/BasicDignified/sublimebuild.py", "$file", `...  
  
>Note that on your system, `python` **could** be `python3`.  
  
To **install** the files Sublime needs to **configure** the Dignified **environment**:  
Open **Sublime Text** and select the menu **Preferences > Browse Packages** to open the Sublime **Packages** folder.  
Move the **contents** of `\Sublime Tools\` to the Sublime **packages** folder  
  
>The Sublime Package folder usually is on:  
**Windows**: `C:\Users\<USER_NAME>\AppData\Roaming\Sublime Text\Packages\`.  
**macOS**: `~/Library/Application Support/Sublime Text 3/Packages/`  
**Linux**: `~/.config/sublime-text-3/Packages/`  
  
If using **openMSX** to run the build, enter its path on the file:  
`sublimebuild.ini`  
On the path `\BasicDignified\Modules\Settings\`
  
On one of the following lines **according** to your system:  
`emulator_filepath = [/PATH_TO/openmsx|openmsx.exe|openmsx.app]`  
**Windows**: `[WINDOWS]`  
**macOS**: `[DARWIN]`  
**Linux**: `[LINUX]`  
  
The **first time** you open a basic program, **classic** or **Dignified** in Sublime, you may need to **chose** the appropriated **highlight** on the bottom right of Sublime Text inside **User >**.  
  
Make sure **Package Control** is installed on Sublime Text.  
  
### Cleanup
  
You can safely delete the folders:  
`Sublime Tools` (after moving its contents to Sublime's packages folder)  
`Images` (Contains images for the GitHub page)  
`Examples` (Contains a Basic program in Dignified and classic formats)  
`Documentation` (Contains the instruction manuals)  
  