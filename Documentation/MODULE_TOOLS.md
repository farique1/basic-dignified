# Additional Features of the included modules  

There are two fairly complete included modules with Basic Dignified: **MSX** and **Tandy Color Computer**.  

Beyond their Basic **dialect** description, they both have **extensive** support for the **Sublime Text** code editor, have **tokenizers** available and can automatically execute their code on emulators.

The module files are kept on **sub folders** named for each system **ID**. `msx` and `coco` for the included module.
They only need to be **accessed** during the **installation** phase and for **configuration** purposes.

Below is an explanation of these modules and their uses.  

> Due to the similarities between both systems, they will be described in parallel, with the differences pointed as needed.

> This sections deals only with the features of the modules. For an in depth exploration, see the section about [creating modules for other systems](https://github.com/farique1/basic-dignified/blob/main/documentation/NEW_MODULES.md).

**[Language Modules](#Language-Module)**  
**[Tokenizer Interfaces](#Tokenizer-Interfaces)**  
**[Emulator Interfaces](#Emulator-Interfaces)**  
**[Sublime Text Integration](#Sublime-Text-Integration)**  
**[Helper Tools](#Helper-Tools)**  

## Language Module

The language modules are very **similar** for both systems with some notable **exceptions** like the `[?](x,y)` handling for instance.  
This is the module that exposed the **Convert Print** `-cp p|?` and **Strip THEN/GOTO** `-tg t|g` features explained on the [main Basic Dignified section](https://github.com/farique1/basic-dignified/blob/main/documentation/BASIC_DIGNIFIED.md) section. Their `.ini` files are `\msx\badig_msx.ini` and `\coco\badig_coco.ini`.  

## Tokenizer Interfaces

**Both** included systems have tokenizer modules **available**.  
They **control** the actual tokenizers, **bridging** them with Basic Dignified and expose **command line arguments** and **remtags**.  
Their **default** behavior can be **set** on `tokenizer_interface.ini` on their respective **modules** folder.  
The tokenized used for the **MSX** is the **custom** made **MSX Batoken**.  
The tokenized used for the **CoCo** is Toolshed's **decb**. There are executables for **Windows** and **MacOS** on the folder.

`.ini:` `.ini` file.  
`cmdl:` Command line arguments.  
`rmtg:` Remtags.  

  - *Tokenize*  
Creates a tokenized version of the converted ASCII classic code.  
	`Default:` `False`  
    `.ini:` `tokenize = [True|False]`.  
	`cmdl:` `--tk_tokenize`  
    `rmtg:` `##BB:tk_tokenize=[True|False]`  

  - *Delete ASCII file*  
Delete the converted ASCII code if only the tokenized version is required.  
	`Default:` `False`  
    `.ini:` `del_ascii = [True|False]`  
	`cmdl:` `--tk_del_ascii`  
    `rmtg:` `##BB:tk_del_ascii=[True|False]`  

  - *Verbose level*  
Set the level of feedback given by the tokenizer module.  
**MSX**: Level 5 will show a byte by byte representation of the tokenization process.  
**CoCo**: Level 5 is not used.  
	`Default:` `3`  
    `.ini:` `verbose = [0-5]`  
	`cmdl:` `--tk_verbose <0-5>`  
    `rmtg:` `##BB:tk_verbose=[0-5]`  

  - *Export list* **(MSX only)**  
Exports a list file similar to the ones exported by assemblers with the tokens alongside the ASCII code and some statistics. The number argument refers to the amount of bytes shown per line. The default is `16` if no number is given. The maximum is `32`. `0` will disable the export.  
	`Default:` `16`  
    `.ini:` `list = [0-32]`  
	`cmdl:` `--tk_list <0-32>`  
    `rmtg:` `##BB:tk_list=[0-32]`  

 
## Emulator Interfaces

**Both** included systems have modules that can automatically **run** the converted code on **emulators**.  
The emulators are **openMSX** for the **MSX** and **XRoar** for the **CoCo**.  
The modules **control** the actual emulators, **bridging** them with Basic Dignified and expose **command line arguments** and **remtags**.  
Their **default** behavior can be **set** on `emulator_interface.ini` on their respective **modules** folder.  
Both emulators will be **opened** with their **default** settings but this can be **changed** if a specif configuration is **needed** for the code execution, for instance, a disk drive for the **MSX** or if a **different** machine is needed for **testing** proposes.  

**MSX particularities**  
To **run** the code on **openMSX**, a machine with a **disk drive** is needed. It will load the **folder** where the converted code is **as a disk** before loading the program. Be aware that all **limitations** of the **MSX disk system** will apply to that folder. File names must have **8 characters** with a **3 characters** extension, cannot have **spaces** and the total file size of the folder should not **exceed** ~700kb. The interface will try to **mitigate** some of these but **caution** is the better approach.    

**CoCo Particularities**  
The converted code will be loaded on **XRoar** as a **tape** file. Since XRoar cannot **directly** load a **binary** file and does not **speed** load **ASCII** files, the converted code will be **wrapped** in a `.CAS` cassette file **before** being loaded. The cassette file is **deleted** after its use.

> On **MacOS**, **XRoar** `.config` files must be **inside** the emulator `.app` folder, **except** for the **default** one. **ROMS** must be on the `.xroar` folder as **usual**.


`.ini:` `.ini` file.  
`cmdl:` Command line arguments.  
`rmtg:` Remtags.  

  - *Emulator executable location*   
The location of openMSX or XRoar executable. This is the full path and file name of the `.exe` for Windows, `.app` for MacOS and the Linux executable.  
Add them under your system description in the `.ini` file: `[WINDOWS]`, `[LINUX]` or `[DARWIN]` for MacOS  
	`Default:` `None`  
    `.ini:` `emulator_path = [PATH_TO_THE_EXECUTABLE]`.  

  - *Run code*  
Run the converted code on the emulator. Both systems will try to load a binary tokenized code, if none is found they will load the ASCII file.  
	`Default:` `False`  
    `.ini:` `run = [True|False]`.  
	`cmdl:` `--em_run`  
    `rmtg:` `##BB:em_run==[True|False]`  

  - *Verbose level*  
Set the level of feedback given by the tokenizer module.  
	`Default:` `3`  
    `.ini:` `verbose = [0-5]`  
	`cmdl:` `--em_verbose <0-5>`  
    `rmtg:` `##BB:em_verbose=[0-5]`  

**MSX Specific Settings**  

  - *Setting*  
Run openMSX with a custom `.xml` setting file.  
	`Default:` `None`  
    `.ini:` `setting = [SETTING.XML]`  
	`cmdl:` `--em_setting SETTING.XML`  
    `rmtg:` `##BB:em_setting=[SETTING.XML]`  

  - *Machine*  
Run openMSX with a custom machine.  
	`Default:` `None`  
    `.ini:` `machine = [MACHINE_NAME]`  
	`cmdl:` `--em_machine MACHINE_NAME`  
    `rmtg:` `##BB:em_machine=[MACHINE_NAME]`  

  - *Extension*  
Run openMSX with a custom extension.  
The extension will be loaded on the first available slot (`ext`).  
A slot can be forced by adding `:exta`, `:extb`, etc after the extension name.  
	`Default:` `None`  
    `.ini:` `extension = [EXTENSION_NAME[:SLOT]]`  
	`cmdl:` `--em_extension EXTENSION_NAME[:SLOT]`  
    `rmtg:` `##BB:em_extension=[EXTENSION_NAME[:SLOT]]`  

  - *No throttle*  
Run openMSX at full speed.  
	`Default:` `False`  
    `.ini:` `nothrottle = [True|False]`  
	`cmdl:` `--em_nothrottle`  
    `rmtg:` `##BB:em_nothrottle=[True|False]`  

  - *Monitor the code execution*  
On Mac or Linux, openMSX can monitor the execution of the code and errors will be pointed back to the correct editor line in the Dignified listing. The same thing is possible when running classic code.  
    `Default:` `False`  
    `.ini:` `monitor = [True|False]`  
	`cmdl:` `--em_monitor`  
    `rmtg:` `##BB:em_monitor=[True|False]`  

> When programming on **MSX Basic Dignified** and using `on error` to **catch** and/or **customize** errors, always use a `CHR$(7)` (***BEEP***) character and pass the **line number** at the **end** of the string on the **error message** to make sure the **monitoring algorithm** will **catch** and **parse** the error and its location correctly.  

**CoCo Specific Settings**  

  - *Configuration*  
Run XRoar with a custom `.conf` config file.  
	`Default:` `None`  
    `.ini:` `config = [CONFIG.CONF]`  
	`cmdl:` `--em_config CONFIG.CONF`  
    `rmtg:` `##BB:em_config=[CONFIG.CONF]`  

  - *Machine*  
Run XRoar with a default machine profile.  
	`Default:` `None`  
    `.ini:` `machine = [MACHINE_PROFILE]`  
	`cmdl:` `--em_machine MACHINE_PROFILE`  
    `rmtg:` `##BB:em_machine=[MACHINE_PROFILE]`  

  - *Basic ROM*  
Run XRoar with a Basic ROM image.  
	`Default:` `None`  
    `.ini:` `bas = [BASIC_ROM]`  
	`cmdl:` `--em_bas BASIC_ROM`  
    `rmtg:` `##BB:em_bas=[BASIC_ROM]`  

  - *Extended Basic rom*  
Run XRoar with an Extended Basic ROM image.  
	`Default:` `None`  
    `.ini:` `extbas = [EXTENDED_BASIC_ROM]`  
	`cmdl:` `--em_extbas EXTENDED_BASIC_ROM`  
    `rmtg:` `##BB:em_extbas=[EXTENDED_BASIC_ROM]`  

  - *Default cartridge*  
Run XRoar with a default cartridge attached.  
	`Default:` `None`  
    `.ini:` `cart = [CARTRIDGE]`  
	`cmdl:` `--em_cart CARTRIDGE`  
    `rmtg:` `##BB:em_cart=[CARTRIDGE]`  

  - *RSDOS Interface*  
Run XRoar with a RSDOS interface.  
	`Default:` `False`  
    `.ini:` `dos = [True|False]`  
	`cmdl:` `--em_dos`  
    `rmtg:` `##BB:em_dos=[True|False]`  

  - *No rate limit*  
Run XRoar at full speed.  
	`Default:` `False`  
    `.ini:` `noratelimit = [True|False]`  
	`cmdl:` `--em_noratelimit`  
    `rmtg:` `##BB:em_noratelimit=[True|False]`  
 
# Sublime Text Integration  
  
Although Basic Dignified can be **comfortably** used on a **notepad** and **command line** environment its full **potential** is revealed when **integrated** with an **IDE** or **code editor** like **Sublime Text** or **VS Code**.  

**Included** on this version is a **full set** of tools for **integration** with the **Sublime Text** editor, including **support** for the **Dignified** and **classic** Basic versions.
    
There are tools for the **MSX** and the **CoCo**.

The tools are:  
- A **Build System** for the **Dignified** and **classic** versions of Basic.  
- **Syntax Highlight** for the Dignified and classic versions of Basic.  
- **Themes** based on Boxy Ocean and Monokai with special scopes for **both** Basic versions.  
- A **Theme** simulating the blue **MSX 1 screen** and accompanying **MSX Screen 0 font**.  
- **Snippets** for the Dignified version of Basic.  
- A **Comment Preference** for the Dignified version.  

> See the [installation](https://github.com/farique1/basic-dignified/blob/main/documentation/INSTALLATION.md) page on how to **install** the Sublime Text Tools.

### Build System  

**All** functions of Basic Dignified can be **achieved** and most can be **automated** from **within** Sublime Text with a few **remtags** and **shortcuts**.

Once everything is **installed** and a program is being coded, the **builds** will be **available** from the `Tools > Build System` menu and are called:  
  
`MSX Basic`  
`MSX Basic Dignified`  
`CoCo Basic`  
`CoCo Basic Dignified`  

The best approach is to leave the **build type** on `automatic`. It will use the **syntax scopes** and the extensions to figure out the **correct** build.    

To **run** the build just press **CONTROL-B**/**COMMAND-B**.  
 
Each of the **builds** have some **variants** that can be chosen by pressing **CONTROL-SHIFT-B**/**COMMAND-SHIFT-B**.  
Once they are **chosen** they will be used as the **default** build until Sublime is **closed** or another variant is **chosen**. They are:  
  
- *MSX/CoCo Basic Dignified:*  
`Default`: **convert**, **tokenize**, **run** and **monitor** the Dignified code. **(No monitoring on CoCo or Windows)**  
`Don't monitor`: **convert**, **tokenize** and **run** the Dignified code. **(MSX only)**  
`Don't Tokenize`: **convert** and **run** the Dignified code. **(CoCo only)**  
`Tokenize only`: **convert** and **tokenize** the Dignified code.  
`Convert only`: only **convert** the Dignified code.  
  
- *MSX/CoCo Basic:*  
`Default`: **tokenize**, **run** and **monitor** the classic Basic code. **(No monitoring on CoCo or Windows)**  
`Don't monitor`: **tokenize** and **run** the classic Basic code. **(MSX only)**  
`Don't Tokenize`: **run** and **monitor** the classic Basic code  
`Tokenize only`: only **tokenize** the classic Basic code.  
`Tokenize and save list`: **tokenize** the classic Basic code and **save** a list file. **(MSX only)**  
  
You can further **refine** the build **behavior** by passing **arguments** with **remtags**, they will **override** the **default** behavior of the **chosen** build variant.  
  
### Syntax Highlight  
  
**Two** pretty decent **syntax highlights**, one for the **Dignified** and one for the **classic** version are available on **both** systems.   
  
The **classic** version is the one **used** by the **list** format exported by the **tokenizer**.  
  
There is also a **syntax highlight** for the **console** output of the **build** system.  
  
### Themes and color schemes  
  
Several **themes** and **color schemes** are included with some based on **Monokai**, **Boxy Ocean** and **Mariana**. There are also a **light** and **dark** color scheme using the **MSX** colors. They **improve** the syntax highlight (classic and Dignified) with **scopes** specific for the Dignified code: `define`, `declare`, labels, errors and warnings.  

For the truly **adventurous**, there is a theme **mimicking** the blue **MSX 1 screen** and a MSX **Screen 0** **font**.  
  
### Auto Completion And Snippets  
  
Snippets for auto completion for:  
 `FOR-NEXT-STEP`  
 `IF-THEN-ELSE`  
 `FUNC-RET`  
 `PMODE-SCREEN-PCLS` **(CoCo only)**  
 `SCREEN-WIDTH-KEY OFF-COLOR` **(MSX only)**  
 `LOCATE-PRINT` **(MSX only)**  
  
A snippet for the creation of the standard **remtags**.  
  
### Comment Preference  
  
Set `##` as the **default comment** of the Dignified Basic.  
`##` is a Dignified **comment** that is **deleted** when the code is **converted** to the classic version.  
There is **no block comment** but **all lines** selected will be **commented**.  
  
There is **no classic comment** preference as I couldn't find a way to **insert** the `REM` or `'` **AFTER** the line number.  
  
## Helper Tools  

Bundled with the system modules are some helper tools that can be used independently.  

### MSX
**[MSX Basic Tokenizer](https://github.com/farique1/basic-dignified/blob/main/documentation/BATOKEN.md)**  
A tokenizer made **for** Basic Dignified that **can** and **should** be used **independently** of it.  

**[MSX Basic DignifieR](https://github.com/farique1/basic-dignified/blob/main/documentation/DIGNIFIER.md)**  
A tool to convert **classic** Basic **to** the **Dignified** format.  
Helps **automate** the conversion of large **programs** or **libraries**.  

### CoCo  

**[CoCo to CAS](https://github.com/farique1/basic-dignified/blob/main/documentation/COCOTOCAS.md)**  
Another tool made **for** Basic Dignified that **can** and **should** be used **independently**.  
Converts **ASCII** Basic, **tokenized** Basic or **binary** files to the **cassette** (`.cas`) format.  
  