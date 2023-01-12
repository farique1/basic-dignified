<img src="https://github.com/farique1/basic-dignified/blob/main/Images/BasicDignifiedSuite_Logo-160.png" alt="Basic Dignified" width="378" height="160">  
  
# Basic Dignified Suite  
**v2.0 Beta**  
  
> This version is in beta, there are some (a lot of?) changes and improvements still being made.   
  
> The **2.0 version** of the Basic Dignified Suite is slightly **incompatible** with the **previous versions** so old Dignified code must be **updated** accordingly. A list of incompatibilities is available on a link below.  
  
**Basic Dignified** is a suite of programs aimed to facilitate the creation, writing and maintaining of classical Basic programs, especially the ones from the **8-bit** era computers.  
  
In its heart, **Basic Dignified** is a 'dialect' of the classical Basics, adding modern coding style and standards that can be composed on any text editor and converted to traditional Basic to be executed.  
  
**Basic Dignified** code strives to be as similar as the original Basic as possible, keeping the language essentially the same. The only necessary feature are the labels that replace number lines, all other components can be added gradually making for a very gentle learning curve.  
  
Dignified Basic is written **without line numbers**, can be **indented**  and have **lines broken**, can use variables with **long names**, have macros **defined** and external files **included**, has a kind of **function** construct, can use **Unicode** special characters analogues to the original character set, as well as **rem toggles**, **true** and **false** statements, **compound arithmetic** operators and much more.  The conversion is highly customizable with controls for **line numbers**, **spaces**, **code cleanup** and more.  
  
The suite is designed to be **modular**, taking any flavor of Basic through external modules that describe each one unique characteristics. The modules are programmed independently and loaded as needed.  
  
 Also included on the suite is a **build system** for the **Sublime Text** editor to automatically convert the **Dignified** code to the **Classic** one.  
  
By default, the suite comes with support for the **MSX Basic** but a module for the **TRS Color Computer** is coming soon and **YOU** can make the next module. **ZX Spectrum**, anyone?  
  
The included **MSX** package contains the **Basic language description** along with support for **Sublime Text** with a module for the **build system**. It also has **syntax highlight** for the **Dignified** and **Classic** Basic versions as well as **themes**, **snippets**, **completions** and more. The build system can automatically run the code on the **openMSX** emulator and on **macOS** and **Linux** can even monitor the execution of the program, reporting any errors back to the offending line on the **Dignified** code (monitoring on Windows is coming).  
Also included on the **MSX** package is a **Tokenizer** and a tool to convert **Classic** Basic to the **Dignified** format to help migrating libraries and big programs.  
  
Throughout the suite, the **extensions** are derived from general names and depend on the current **system module** and the **file type**.  
The included **MSX** module uses:  
(The general names are in parenthesis for context)  
`.dmx` (`.bad`) for the **Dignified** code.  
`.amx` (`.asc`) for the **classic** Basic in **ASCII**.  
`.bmx` (`.bas`) for the **classic** Basic in **binary**.  
`.lmx` (`.lst`) for the **list** format exported by the **tokenizer**.  
  
> The  system specific extensions will **avoid conflict** when more modules are available.  
> General and system specific extensions will be mentioned **interchangeably** across the documentation. i.e.: `.dmx` is the same as `.bad`.  
  
---  
### [Installation](https://github.com/farique1/basic-dignified/blob/main/Documentation/INSTALLATION.md)  
  
### [Basic Dignified Converter](https://github.com/farique1/basic-dignified/blob/main/Documentation/BASIC_DIGNIFIED.md)  
  
### [Sublime Text Build And Tools](https://github.com/farique1/basic-dignified/blob/main/Documentation/SUBLIME_TOOLS.md)  
  
#### [Tokenizer](https://github.com/farique1/basic-dignified/blob/main/Documentation/TOKENIZER.md)  
  
#### [DignifieR](https://github.com/farique1/basic-dignified/blob/main/Documentation/DIGNIFIER.md)  
  
### [Creating Modules For Other Systems (SOON)](https://github.com/farique1/basic-dignified/blob/main/Documentation/NEW_MODULES.md)  
  
### [Differences and Incompatibilities with v1.6](https://github.com/farique1/basic-dignified/blob/main/Documentation/DIFFERENCES.md)  
  
### [Implementation Ideas and Known Bugs](https://github.com/farique1/basic-dignified/blob/main/Documentation/IMPLEMENTATIONS.md)  
---  
  
> **Basic Dignified** runs on **Python 3.10**.  
> No external dependencies are needed.  
  
>**Basic Dignified** is constantly evolving so please report any misbehavior.  
  
> As always, **Basic Dignified** is offered as is, with no guaranties whatsoever. Use at your own discretion.  
Having said that, enjoy and send feedback.  
  
Thanks.  
  
---  
  
 ![# CGKcomparison.png](https://github.com/farique1/basic-dignified/blob/main/Images/CGKcomparison.png)  
  
