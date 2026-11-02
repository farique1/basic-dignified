# Additional Features of the included modules  

Basic Dignified includes modules for **MSX**, **Tandy Color Computer** and **ZX-81**. All three modules have editor integrations, tokenizers and emulator launch support.

Beyond their Basic **dialect** description, the modules can provide **tokenizers** and automatic **emulator** execution.

Below is an explanation of these modules and their uses.  

> MSX and CoCo options are described together where their interfaces match; ZX-81-specific behavior is called out separately.

> This sections deals only with the features of the modules. For an in depth exploration, see the section about [creating modules for other systems](https://github.com/farique1/basic-dignified/blob/main/documentation/NEW_MODULES.md).  

**[Language Modules](#Language-Module)**  
**[Tokenizer Interfaces](#Tokenizer-Interfaces)**  
**[Emulator Interfaces](#Emulator-Interfaces)**  
**[Helper Tools](#Helper-Tools)**  

## Language Module

MSX and CoCo share language options with some system-specific differences such as `[?](x,y)`. The ZX-81 also supports `[?](row,column)`, expanding it to native `PRINT AT row,column;`. **Convert Print** `-cp p|?` and **Strip THEN/GOTO** `-tg t|g` are MSX/CoCo-only options. Their language `.ini` files are `msx/badig_msx.ini` and `coco/badig_coco.ini`; ZX-81 currently has no language-specific `.ini` options.

## Tokenizer Interfaces

All three included systems have tokenizer modules **available**.
They **control** the actual tokenizers, **bridging** them with Basic Dignified and expose **command line arguments** and **remtags**.  
Their **default** behavior can be **set** on `tokenizer_interface.ini` on their respective **modules** folder.  
The **MSX** tokenizer is the custom **MSX Batoken**. The **CoCo** tokenizer uses Toolshed's **decb**. The **ZX-81** tokenizer is implemented in Python and generates a `.p` program file.

**ZX-81 pipeline**
Use `-id zx81` to select this module. A Dignified `.DZX` source is converted to numbered BASIC in `.AZX`, then tokenized to `.p`. Tokenization is enabled by default for this module; pass `--tk_ascii_only` to keep only the `.AZX` file. `--em_run` launches `C:\zeddy\EightyOne.exe` with the `.p` file. The emulator path can be changed in `zx81/emulator_interface.ini`.

`.ini:` `.ini` file.  
`cmdl:` Command line arguments.  
`rmtg:` Remtags.  

  - *Tokenize*  
Creates a tokenized version of the converted ASCII classic code. MSX/CoCo default to `False`; ZX-81 defaults to `True`.
  `Default:` `False` (MSX/CoCo); `True` (ZX-81)
    `.ini:` `tokenize = [True|False]`.  
	`cmdl:` `--tk_tokenize`  
    `rmtg:` `##BB:tk_tokenize=[True|False]`  

  - *Delete ASCII file*  
Delete the converted ASCII code if only the tokenized version is required.  
	`Default:` `False`  
    `.ini:` `del_ascii = [True|False]`  
	`cmdl:` `--tk_del_ascii`  
    `rmtg:` `##BB:tk_del_ascii=[True|False]`  

  - *ASCII-only conversion* **(ZX-81 only)**
  Skip `.p` generation and keep only the numbered `.AZX` file.
    `Default:` `False`
    `cmdl:` `--tk_ascii_only`
    `rmtg:` `##BB:arguments=--tk_ascii_only`

  - *Verbose level* **(MSX/CoCo only)**
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

All three modules can automatically **run** converted code on an emulator. The emulators are **openMSX** for MSX, **XRoar** for CoCo, and **EightyOne** for ZX-81. Each interface bridges its emulator with Basic Dignified and can expose settings, command-line arguments and remtags.

MSX and CoCo emulator settings are configurable in their module `.ini` files. The ZX-81 interface currently launches EightyOne with the tokenized `.p` file; it does not yet monitor execution or expose machine/profile options.

**ZX-81** uses `--em_run` or `##BB:em_run=True`; its default is `False`. The executable path is read from the `[WINDOWS] emulator_path` setting in `zx81/emulator_interface.ini`. No `--em_verbose` option is exposed by this interface.

```ini
[CONFIGS]
run = false

[WINDOWS]
emulator_path = C:\zeddy\EightyOne.exe
```

**MSX particularities**  
To **run** the code on **openMSX**, a machine with a **disk drive** is needed. It will load the **folder** where the converted code is **as a disk** before loading the program. Be aware that all **limitations** of the **MSX disk system** will apply to that folder. File names must have **8 characters** with a **3 characters** extension, cannot have **spaces** and the total file size of the folder should not **exceed** ~700kb. The interface will try to **mitigate** some of these but **caution** is the better approach.    

**CoCo Particularities**  
The converted code will be loaded on **XRoar** as a **tape** file. Since XRoar cannot **directly** load a **binary** file and does not **speed** load **ASCII** files, the converted code will be **wrapped** in a `.CAS` cassette file **before** being loaded. The cassette file is **deleted** after its use.

> On **MacOS**, **XRoar** `.config` files must be **inside** the emulator `.app` folder, **except** for the **default** one. **ROMS** must be on the `.xroar` folder as **usual**.


`.ini:` `.ini` file.  
`cmdl:` Command line arguments.  
`rmtg:` Remtags.  

  - *Emulator executable location*   
The location of the emulator executable. This is the full path and file name of the `.exe` for Windows, `.app` for MacOS and the Linux executable.
Add them under your system description in the `.ini` file: `[WINDOWS]`, `[LINUX]` or `[DARWIN]` for MacOS  
  `Default:` EightyOne uses `C:\zeddy\EightyOne.exe`; MSX/CoCo paths are installation-specific.
    `.ini:` `emulator_path = [PATH_TO_THE_EXECUTABLE]`.  

  - *Run code*  
Run the converted code on the emulator. MSX/CoCo can use tokenized output or their ASCII fallback; ZX-81 requires the tokenized `.p` output.
	`Default:` `False`  
    `.ini:` `run = [True|False]`.  
	`cmdl:` `--em_run`  
    `rmtg:` `##BB:em_run=[True|False]`

  - *Verbose level* **(MSX/CoCo only)**
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
  
## Helper Tools  

Bundled with the system modules are some helper tools that can be used independently.  

### MSX
**[MSX Basic Tokenizer](https://github.com/farique1/basic-dignified/blob/main/documentation/BATOKEN.md)**  
A tokenizer made **for** Basic Dignified that **can** be used **independently** of it.  

**[MSX Basic DignifieR](https://github.com/farique1/basic-dignified/blob/main/documentation/DIGNIFIER.md)**  
A tool to convert **classic** Basic **to** the **Dignified** format.  
Helps **automate** the conversion of large **programs** or **libraries**.  

### CoCo  

**[CoCo to CAS](https://github.com/farique1/basic-dignified/blob/main/documentation/COCOTOCAS.md)**  
Another tool made **for** Basic Dignified that **can** be used **independently**.  
Converts **ASCII** Basic, **tokenized** Basic or **binary** files to the **cassette** (`.cas`) format.  
  