# Additional Features of the included modules  

There are two fairly complete included modules with Basic Dignified: **MSX** and **Tandy Color Computer**.  
**ZX Spectrum** is also included, with a documented **48K Sinclair**
subset, its own tokenizer and optional snapshot engine.

Beyond their Basic **dialect** description, they have **tokenizers** available and can automatically **execute** their code on emulators.  

Below is an explanation of these modules and their uses.  

> Due to their similarities, **MSX and CoCo** are described in parallel, with the differences pointed as needed. Spectrum-specific features are described separately.

> This sections deals only with the features of the modules. For an in depth exploration, see the section about [creating modules for other systems](NEW_MODULES.md).  

**[Language Modules](#Language-Module)**  
**[Tokenizer Interfaces](#Tokenizer-Interfaces)**  
**[Emulator Interfaces](#Emulator-Interfaces)**  
**[Helper Tools](#Helper-Tools)**  

## Language Module

The language modules are very **similar** for MSX/CoCo with some notable **exceptions** like the `[?](x,y)` handling for instance.
This is the module that exposed the **Convert Print** `-cp p|?` and **Strip THEN/GOTO** `-tg t|g` features explained on the [main Basic Dignified section](BASIC_DIGNIFIED.md) section. Their `.ini` files are `\msx\badig_msx.ini` and `\coco\badig_coco.ini`.  

### ZX Spectrum

Select **-id zxspectrum**. The module supplies Sinclair commands and numbers,
long numeric scalars, explicit aliases for restricted variable categories,
implicit LET, scalar compounds and **PRINT AT**.
**-cp/-tg** are MSX/CoCo options, not Spectrum shortcuts.
**REMX** reserves an absolute numbered REM, and **\80..\A4 / %A..%U**
encode graphic/UDG bytes. See the
[language and character reference](BASIC_DIGNIFIED.md#zx-spectrum-characters).
Unsupported Sinclair words fail explicitly; the ROM still checks runtime
expression types/ranges.

## Tokenizer Interfaces

**All three** included systems have tokenizer modules **available**.
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

 
### ZX Spectrum

The **Spectrum tokenizer** reads the generated AZS or an existing numbered
listing with **-asc**. It uses the Sinclair token table, numeric records and
checksums; it does **not** use MSX Batoken or CoCo DECB.
Defaults are in `zxspectrum\tokenizer_interface.ini`.
INI < command line < **remtags** determines the final settings.

- *Tokenize*  
  Generate the selected binary formats after validating the listing.  
  `Default:` `False`  
  `.ini:` `tokenize = [True|False]`  
  `cmdl:` `--tk_tokenize`  
  `rmtg:` `##BB:tk_tokenize=[True|False]`

- *Output format*  
  TAP/TZX are **tapes**; Z80/SNA are real **48K snapshots**.  
  `Default:` `tap`  
  `.ini:` `format = tap|tzx|both|z80|sna|all`  
  `cmdl:` `--tk_format <format>`  
  `rmtg:` `##BB:tk_format=<format>`  
  **both** means TAP+TZX; **all** adds Z80+SNA. Snapshots require
  [optional SkoolKit](INSTALLATION.md#zx-spectrum-snapshots); tapes do not.

- *Tape name*  
  Name stored in the intermediate tape header, also used when building snapshots.  
  `Default:` first 10 characters of the output stem  
  `.ini:` `name =`  
  `cmdl:` `--tk_name <1..10 printable ASCII characters>`  
  `rmtg:` `##BB:tk_name=<name>`

- *BASIC autorun*  
  **-1** disables it, **0** starts at the first line, **1..9999** selects a line.  
  `Default:` `-1` (`0` with --em_run unless overridden)  
  `.ini:` `autorun = -1`  
  `cmdl:` `--tk_autorun <line>`  
  `rmtg:` `##BB:tk_autorun=<line>`

The Spectrum adapter does not expose MSX/CoCo-only tokenizer arguments,
including list export and ASCII deletion. Use the common **-vb** for feedback.
Each output is replaced atomically after successful generation; the whole
set is not a multi-file transaction. Snapshot failure preserves all existing
binary outputs. An AZS listing may already exist when binary generation fails.

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
  
### ZX Spectrum

**EightyOne** integration is available on **Windows**. The profile must select
**MachineName=48K Spectrum** and have an installed English ROM.
The adapter copies the profile into a temporary directory, waits for the
emulator to close and checks its exit status. It does not monitor BASIC errors.

- *Run emulator*  
  `Default:` `False`  
  `.ini:` `[CONFIGS] run = False`  
  `cmdl:` `--em_run`  
  `rmtg:` `##BB:em_run=True|False`
- *Executable path*  
  `.ini:` `[CONFIGS] emulator_path =`  
  `cmdl:` `--em_path PATH`  
  `rmtg:` `##BB:em_path=PATH`
- *48K profile to copy*  
  `Default:` bundled 48K template  
  `.ini:` `[CONFIGS] setting =`  
  `cmdl:` `--em_setting PATH`  
  `rmtg:` `##BB:em_setting=PATH`

**EM_RUN** enables generation; **TK_TOKENIZE=False** conflicts with it.
TAP/TZX use private autoload/flash-load settings; Z80/SNA disable tape
autoload. With **both/all**, the first output, TAP, is opened. Select
**z80** or **sna** to launch that snapshot directly. Manual loading is
described in the [Spectrum reference](ZX_SPECTRUM.md).

## Helper Tools

Bundled with the system modules are some helper tools that can be used independently.  

### MSX
**[MSX Basic Tokenizer](BATOKEN.md)**  
A tokenizer made **for** Basic Dignified that **can** be used **independently** of it.  

**[MSX Basic DignifieR](DIGNIFIER.md)**  
A tool to convert **classic** Basic **to** the **Dignified** format.  
Helps **automate** the conversion of large **programs** or **libraries**.  

### CoCo  

**[CoCo to CAS](COCOTOCAS.md)**  
Another tool made **for** Basic Dignified that **can** be used **independently**.  
Converts **ASCII** Basic, **tokenized** Basic or **binary** files to the **cassette** (`.cas`) format.

### ZX Spectrum

The [Spectrum reference](ZX_SPECTRUM.md) describes numbered input, TAP/TZX,
optional Z80/SNA and **REMX**. The tokenizer is part of the language module;
MSX DignifieR and CoCo to CAS do not convert Spectrum programs.
The [Spectrum DignifieR](DIGNIFIER.md#zx-spectrum-dignifier) converts
numbered AZS to DZS through `python -m zxspectrum.dignifier`; **-asc**
instead preserves the numbered listing. Both use Suite graphic/raw escapes.
