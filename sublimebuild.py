#!/usr/bin/env python3
"""
MSX Badig Build
v2.0
Copyright (C) 2018 - Fred Rique (farique)
https://github.com/farique1/basic-dignified

A Sublime Text 3-4 build system to convert Basic Dignified to traditional Basic,
    tokenize and run on an emulator
or just tokenize tokenize and run on an emulator.

The complete suite includes:
Basic Dignified
    A modern take on 8 bit classic Basics
    Support for any classic Basic though description modules
Basic DignifieR
    Convert classic Basic to Dignified format
Syntax Highlight, Theme, Build System, Comment Preference and Auto Completion
    for Sublime Text 3 and 4

Installation notes on the README.md

New: 2.0 11/04/2022
    Modular design for compatibility with Basic Dignfied v2.0
"""

import os.path
import importlib

# Custom modules
from Modules.Support import infolog
from Modules.Settings.sublimebuild_settings import SettingsBuild

# Get the Settings class from the settings module
stg = SettingsBuild()

# Initialize the settings
stg.init()

# Prepare the classical system information for the module name
system_id = stg.system_id
system_module = f'..{system_id}.sublimebuild_{system_id}'
system_package = f'Modules.{system_id}'

# Classic system module
try:
    System = importlib.import_module(system_module, system_package)
except ModuleNotFoundError as e:
    infolog.log(1, f'Classic system not found: {e}')

# Badig as a module
BADIG_EXISTS = True
try:
    import badig
except (ImportError, ModuleNotFoundError):
    BADIG_EXISTS = False

infolog.level = stg.verbose_level


class Build:
    def __init__(self, stg):
        self.stg = stg

    def build(self):
        tokenized = None
        remtags = None
        line_list = None
        if not self.stg.classic_basic:
            if BADIG_EXISTS:
                dig = badig.Main()

                verbose = self.stg.verbose_level
                remtags = dig.stg.remtags
                if remtags.get('ARGUMENTS', None):
                    args = remtags['ARGUMENTS']
                    if '-vb' in remtags['ARGUMENTS']:
                        vb_idx = args.index('-vb') + 1
                        verbose = args[vb_idx]
                infolog.level = int(verbose)

                self.stg.source_file = dig.stg.file_save
                self.stg.binary_ext = dig.stg.binary_ext
                self.stg.ascii_ext = dig.stg.ascii_ext

                dig.execute()

                line_list = dig.line_list

                if 'T' in dig.stg.output_format:
                    tokenized = True
            else:
                infolog.log(1, 'Basic Dignified not found.')

        elif self.stg.tokenize:
            sys = System.Build(self.stg)
            sys.build()
            tokenized = True

        return tokenized, remtags, line_list


# Main class ------------------------------------------------------------------
class Main:
    def __init__(self):
        self.stg = stg

    def str_to_bool(self, string, same):
        if string.upper() == 'TRUE':
            boolean = True
        elif string.upper() == 'FALSE':
            boolean = False
        elif string == '':
            boolean = same
        else:
            infolog.log(1, f'Remtag argument must be True or False.')

        return boolean

    def execute(self):

        infolog.log(3, 'Basic Dignified Build System', bullet='')
        infolog.log(3, f'Building: {os.path.join(self.stg.file_name)}', bullet='')

        if self.stg.classic_basic:
            type_log = 'Classic Basic'
            option_log = 'Tokenize only' if self.stg.tokenize and self.stg.convert_only and not self.stg.save_list \
                else 'Tokenize and save list' if self.stg.tokenize and self.stg.convert_only and self.stg.save_list \
                else 'Tokenize and run' if self.stg.tokenize and not self.stg.convert_only and not self.stg.save_list \
                else 'Run'
        else:
            type_log = 'Basic Dignified'
            option_log = 'Convert and run' if self.stg.monitor_exec and not self.stg.convert_only \
                else 'Convert only' if not self.stg.monitor_exec and self.stg.convert_only \
                else "Don't monitor"
        infolog.log(3, f'{type_log}: {option_log}')

        bui = Build(self.stg)
        tokenized, remtags, line_list = bui.build()

        if remtags:
            self.stg.machine_name = remtags.get('OVERRIDE_MACHINE', self.stg.machine_name) or self.stg.machine_name
            self.stg.disk_ext_name = remtags.get('OVERRIDE_EXTENSION', self.stg.disk_ext_name) or self.stg.disk_ext_name
            self.stg.monitor_exec = self.str_to_bool(remtags.get('MONITOR_EXEC', str(self.stg.monitor_exec)), self.stg.monitor_exec)
            self.stg.throttle = self.str_to_bool(remtags.get('THROTTLE', str(self.stg.throttle)), self.stg.throttle)
            self.stg.convert_only = self.str_to_bool(remtags.get('CONVERT_ONLY', str(self.stg.convert_only)), self.stg.convert_only)

        if self.stg.convert_only:
            raise SystemExit(0)

        base_file = os.path.splitext(self.stg.source_file)[0]
        ascii_file = os.path.join(self.stg.file_path, self.stg.source_file)
        binary_file = os.path.join(self.stg.file_path, base_file + self.stg.binary_ext)

        if os.path.isfile(binary_file) and tokenized:
            file_run = binary_file
        elif os.path.isfile(ascii_file):
            file_run = ascii_file
        else:
            infolog.log(1, f'No file found to run:\n*** {binary_file}\n*** {ascii_file}')

        self.stg.file_name = os.path.basename(file_run)
        run = System.Run(self.stg)
        run.run(line_list)


# Main function ---------------------------------------------------------------
def main():
    '''Do the thing'''

    build_main = Main()
    build_main.execute()


if __name__ == '__main__':
    main()
