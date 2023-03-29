# Code Editor Integration  
 
Although Basic Dignified can be **comfortably** used on a **notepad** and **command line** environment its full **potential** is revealed when **integrated** with an **IDE** or **code editor** like **Sublime Text** or **VSCode**.   

**All** functions of Basic Dignified can be **achieved** and most can be **automated** from **within** them with a few **remtags** and **shortcuts**.  

**Included** on this version is a **full set** of tools for **integration** with **both** editors, including **support** for the **Dignified** and **classic** Basic versions of both included **systems**.  

The tools are:  
- A **[Build System](#Build-System)** for the **Dignified** and **classic** versions of Basic.  
- **[Syntax Highlight](#Syntax-Highlight)** for the Dignified and classic versions of Basic.  
- **[Themes](#Themes-and-color-schemes)** based on Boxy Ocean and Monokai with special scopes for **both** Basic versions.  
- A **Theme** simulating the blue **MSX 1 screen** and accompanying **MSX Screen 0 font**.  
- **[Snippets](#Auto-Completion-And-Snippets)** for the Dignified version of Basic.  
- A **[Comment Preference](#Comment-Preference)** for the Dignified version. 
  
> See the [installation](https://github.com/farique1/basic-dignified/blob/main/documentation/INSTALLATION.md) page on how to **install** these tools.  
  
## Build System  

### VSCode  
  
> Due to the **nature** of the VSCode **build** system, you will need to have the `.vscode` **folder** containing the `tasks.json` of your system **opened** on the editor. For **convenience**, this folder is **provided** on the `VSCode Extension` folder of the Basic Dignified **installation**. If you open your Basic programs as a **folder** in VSCode, you can have `.vscode` as a **subfolder** there. If you want to have build access using single files, you can just `add a folder` containing the **provided** `.vscode` folder ***AS A SUBFOLDER***.

Once everything is **installed** and a program is being coded, the **builds** will be **available** from the `>` icon at the top left of the code window.  
  
There are a number of different build options depending on the kind of Basic you are working on. You can select them from the Command Palette list appearing on the center of the screen.   
  
You can further **refine** the build **behavior** by passing **arguments** with **remtags**, they will **override** the **default** behavior of the **chosen** build variant.  
  
> See the end of the [Basic Dignified usage secton](https://github.com/farique1/basic-dignified/blob/main/documentation/BASIC_DIGNIFIED.md) for an explanation of the **remtags**.  
  
### Sublime Text  
  
Once everything is **installed** and a program is being coded, the **builds** will be **available** from the `Tools > Build System` menu and are called:  
  
`MSX Basic`  
`MSX Basic Dignified`  
or  
`CoCo Basic`  
`CoCo Basic Dignified`  

The best approach is to leave the **build type** on `automatic`, this will use the **syntax scopes** and the extensions to figure out the **correct** build.    
  
To **run** the build just press **CONTROL-B**/**COMMAND-B**.  
  
Each of the **builds** have some **variants** that can be chosen by pressing **CONTROL-SHIFT-B**/**COMMAND-SHIFT-B**. They depend on the kind of Basic you are working on. Once they are **chosen** they will be used as the **default** build until Sublime is **closed** or another variant is **chosen**.  
  
You can further **refine** the build **behavior** by passing **arguments** with **remtags**, they will **override** the **default** behavior of the **chosen** build variant.  

> See the end of the [Basic Dignified usage secton](https://github.com/farique1/basic-dignified/blob/main/documentation/BASIC_DIGNIFIED.md) for an explanation of the **remtags**.  
  
## Syntax Highlight  
  
**Two** pretty decent **syntax highlights**, one for the **Dignified** and one for the **classic** version are available on **both** systems.   
  
> The **list** exported by the MSX **tokenizer** uses the **classic** version.  

## Themes and color schemes  
  
Several **themes** and **color schemes** are included with some based on **Monokai**, **Boxy Ocean** and **Mariana**. They **improve** the syntax highlight (classic and Dignified) with **scopes** specific for the Dignified code: `define`, `declare`, labels, errors and warnings.  

There are also a **light** and a **dark** color scheme using the **MSX** colors and
for the truly **adventurous** there are themes **mimicking** the blue **MSX 1 screen** and the **green**/**orange** CoCo screen. Also there are accompanying **fonts** representing the ones found on the **original** systems.  
  
## Auto Completion And Snippets  
  
Snippets for auto completion for:  
 `FOR-NEXT-STEP`  
 `IF-THEN-ELSE`  
 `FUNC-RET`  
 `PMODE-SCREEN-PCLS` **(CoCo only)**  
 `SCREEN-WIDTH-KEY OFF-COLOR` **(MSX only)**  
 `LOCATE-PRINT` **(MSX only)**  
  
A snippet for the creation of the standard **remtags**.  
  
## Comment Preference  
  
Set `##` as the **default comment** of the Dignified Basic.  
`##` is a Dignified **comment** that is **deleted** when the code is **converted** to the classic version.  
There is **no block comment** but **all lines** selected will be **commented**.  
  
There is no **classic Basic** comment preference as I couldn't find a way to **insert** the `REM` or `'` **AFTER** the line number.  
  