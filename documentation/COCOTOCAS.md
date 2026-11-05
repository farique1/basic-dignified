# CoCo to CAS  
  
Convert CoCo binary `.bin`, tokenized Basic `.bas` or ASCII Basic `.asc` programs to the `.cas` cassette format.  

**CAS** here is the **CoCo cassette format**, not Spectrum TAP/TZX.
For **ZX Spectrum**, use the module's tape/snapshot output described in
[module tools](MODULE_TOOLS.md#tokenizer-interfaces). This helper's existing
CoCo formats and arguments are unchanged.
  
**CoCo to CAS** try to guess the file format based on the extension but it can be forced with the `-ff` argument.  
  
Run with:  
`python cocotocas.py <input file> [output file] [-ff <bas|bin|asc>]`  
  
If no `output file` is given, the `input file` name will be used.  

----

> **CoCo to CAS** is part of the **Basic Dignified Suite**: https://github.com/farique1/basic-dignified  
