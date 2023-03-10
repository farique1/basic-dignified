# MSX Basic DignifieR  
  
MSX Basic DignifieR **converts** **classic** MSX Basic **to** the **Dignified** format.  

It **eases** the heavily **repetitive** and **error** prone task of **removing** line numbers, **creating** branching labels, **adding** spaces between keywords, etc. Helps if you want to **convert** a **lot** of files or a **long** one for **editing** or just for **better visualization** / **reading**. There are a series of **options** to configure the **appearance** of the final Dignified code according to your **preferences**.  
  
> The interplay between all the configurable options and the variety of the Basic itself is somewhat complex and was not nearly as tested as it should so please keep an eye and report any bugs.  
  
## Usage  
  
  
Run with:  
`python msxbader.py <CLASSIC_CODE> [DIGNIFIED_CODE] [arguments]`  
  
### Arguments  
  
You can control the behavior of **MSX Basic DignifieR** through:  
  
`code:` The **code itself**.  
`cmdl:` Arguments on the **command line**.  
  
Command line arguments have **priority** over the code.  
  
- *Source file*  
The **classic** code file to be read.  
`Default:` `""`  
`code:` `self.file_load = <CLASSIC_CODE>`  
`cmdl:` `<CLASSIC_CODE>`  
  
- *Destination file*  
The **Dignified**  file to be saved.  
`Default:` **None**  
`code:` `self.file_load = <DIGNIFIED_CODE>`  
`cmdl:` `<DIGNIFIED_CODE>`  
If no name is given, the destination file will have the source name with the proper extension.  
  
- *Convert to lower case*  
**Convert** all text (**excluding** literals: **quotations**, **DATAs** and **REMs**) to **lowercase**.  
`Default:` `True`  
`code:` `self.conv_lower = [True|False]`  
`cmdl:` `-tl`  
  
- *Keep original spaces*  
All **spaces** are normalized to **1** by default. This will **keep** any **original** spaces beyond that.  
`Default:` `False`  
`code:` `self.keep_spcs = [True|False]`  
`cmdl:` `-ks`  
  
- *Convert `LOCATE:PRINT`*  
Convert `locate x,y:print` to `[?](x,y) `.  
`Default:` `True`  
`code:` `self.conv_locprt = [True|False]`  
`cmdl:` `-cp`  
  
- *Format labels*  
Define how **labels** are **converted**.  
(Add multiple letters to add functions)  
`i` **Indent** non label lines after the first label.  
`s` **Add** a blank line before each label.  
`Default:` `is`  
`code:` `self.format_label = ['i,s']`  
`cmdl:` `-fl <i,s>`  
  
- *Format REMs*  
Define how **REMs** are converted.  
(Add multiple letters to add functions)  
`l` Remove REMs **alone** on a line.  
`i` Remove REMs at the **end** of a line.  
`b` **Keep** blank REM lines as blank lines.  
`m` **Move** inline REMs above its original line.  
`k` **Add** a label if a REM directed by a **branching** instruction was **removed**.  
`Default:` `m`  
`code:` `self.format_rems = <l,i,b,m,k>`  
`cmdl:` `-fr <l,i,b,m,k>`  
  
- *Unravel `THEN/ELSE`*  
**Break** the line on `THEN` and/or `ELSE` with a `_` line break.  
(Add multiple letters to add functions)  
`t` Break the line **after** `THEN`.  
`n` Break the line **before** `THEN`.  
`e` Break the line **after** `ELSE`.  
`b` Break the line **before** `ELSE`.  
`Default:` `te`  
`code:` `self.unravel_if = <t,n,e,b>`  
`cmdl:` `-ut <t,n,e,b>`  
  
- *Unravel colons*  
**Break** the line on `:`.  
(Add multiple letters to add functions)  
`w` Break the line and **do not** indent.  
`i` Break the line **indenting** after the first `:`.  
`c` Put the `:` on the line **below**.  
`Default:` `ic`  
`code:` `self.unravel_colons = <i,w,c>`  
`cmdl:` `-uc <i,w,c>`  
  
- *Repel before keyword*  
A case insensitive **regex** string with **elements** which should **generate** a space **before** a keyword and them.  
`Default:` `[a-z0-9{}")$]`  
`code:` `self.repelcbef = [REGEX]`  
`cmdl:` `-rb <REGEX>`  
  
- *Repel after keyword*  
A case insensitive **regex** string with **elements** which should **generate** a space **after** a keyword and them.  
`Default:` `[a-z0-9{}"(]`  
`code:` `self.repelcaft = [REGEX]`  
`cmdl:` `-ra <REGEX>`  
  
- *Join before*  
A case insensitive **regex** string with **elements** forcing the **removal** of spaces **before** them.  
`Default:` `^(,|:)$`  
`code:` `self.stripsbef = [REGEX]`  
`cmdl:` `-jb <REGEX>`  
  
- *Join after*  
A case insensitive **regex** string with **elements** forcing the **removal** of spaces **after** them.  
`Default:` `^(,|:)$`  
`code:` `self.stripsaft = [REGEX]`  
`cmdl:` `-ja <REGEX>`  
  
- *Force spaces before*  
A case insensitive **regex** string with **elements** that must have a space **before** them.  
`Default:` `^(:|\+|-|\*|/|\^|\\)$`  
`code:` `self.spacesbef = [REGEX]`  
`cmdl:` `-sb <REGEX>`  
  
- *Force spaces after*  
A case insensitive **regex** string with **elements** that must have a space **after** them.  
`Default:` `^(#|\+|-|\*|/|\^|\\)$`  
`code:` `self.spacesaft = [REGEX]`  
`cmdl:` `-sa <REGEX>`  
  
- *Force together*  
A case insensitive **regex** string with **elements** that will be forced **together**.  
`Default:` `(<=|>=|=<|=>|\)-\()`  
`code:` `self.forcetogt = [REGEX]`  
`cmdl:` `-ft <REGEX>`  
  
- *Verbose*  
Set the level of feedback given by the program.  
 `0` = silent, `1` = +errors, `2` = +warnings, `3` = +steps, `4` = +details.  
`Default:` `3`  
`code:` `self.verbose_level = [#]`  
`.ini:` `verbose_level = [#]`  
`cmdl:` `-vb <#>`  
  
----
> **MSX Basic DignifieR** is part of the **Basic Dignified Suite**: https://github.com/farique1/basic-dignified  
