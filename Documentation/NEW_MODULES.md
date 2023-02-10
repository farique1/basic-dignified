# New Modules  

> A complete guide on how to implement new systems is coming soon.  
> This is a small overview.  
  
Modules for **new systems** should be placed on **folders** named with their **system ID**.  
The **language** module for the **classic** system must be named `badig_SYSTEM-ID.py`.  
The **tools** module for the **classic** system must be named `tools_SYSTEM-ID.py`.  

The **language** module **describes** and adds **control** to the **conversion** fom the **Dignified** to the **classic** versions.  
The **tools** module **control** all **interfaces** associated with **programs** helping the **conversion** like **tokenizers** and **emulators**.  
The **interfaces** directly **control** the **external programs** like **tokenizers** and **emulators**, making a **bridge** between them and Basic Dignified and adding **configurations** and **features**.  

The **MSX folder** opened with its **files** as an example of a **typical** module.

```  
|- documentation  
|- examples  
|- images  
|- coco  
|- msx  
   |- msxbatoken
   |  badig_msx.ini
   |  badig_msx.py
   |  emulator_interface.ini
   |  emulator_interface.py
   |  msxbader.py
   |  openmsx_output.tcl
   |  tokenizer_interface.ini
   |  tokenizer_interface.py
   |  tools_msx.py
|- support  
|  badig.py  
```  
  
A **schematic** of the **relations** between the **files** of Basic Dignified ans the **MSX** module.  
<img src="https://github.com/farique1/basic-dignified/blob/main/images/filerelationsmsx.png" alt="File relations" width="480">  
  
The **description** for the system are on `\support\systems.json`:  
  
```json  
[  
 {  
   "msx": {  
      "name": "MSX",  
      "dig_ext": ".dmx",  
      "asc_ext": ".amx",  
      "bin_ext": ".bmx",  
      "lst_ext": ".lmx"  
   },  
   "coco": {  
      "name": "Color Computer",  
      "dig_ext": ".dcc",  
      "asc_ext": ".acc",  
      "bin_ext": ".bcc",  
      "lst_ext": ".lcc"  
    },  
   "spec": {  
      "name": "ZX Spectrum",  
      "dig_ext": ".dzs",  
      "asc_ext": ".azs",  
      "bin_ext": ".bzs",  
      "lst_ext": ".lzs"  
   },  
   "c64": {  
      "name": "Commodore 64",  
      "dig_ext": ".d64",  
      "asc_ext": ".a64",  
      "bin_ext": ".b64",  
      "lst_ext": ".l64"  
   }  
}  
]  
```  
  
Each system information is composed of:  
- *System ID*  
  - *System name*  
  - *Dignified extension*  
  - *ASCII extension*  
  - *Binary extension*  
  - *List extension*  
  
<!-- 
Note:
Standardize `em_run` and `tk_tokenize` arguments when available so the build systems are compatible. -->