# This module is responsible for opening, sending information and controlling the Emulator

import shutil
import os.path
import argparse
import subprocess
import configparser
from os import remove as osremove
from collections import namedtuple

from .cocotocas import Convert
from support.helper import Infolog

infolog = Infolog()


class Run:
    def __init__(self, e_stg):
        self.e_stg = e_stg

    def run(self):
        self.stg = Settings(self.e_stg)
        self.stg.init()

        file_ext = os.path.splitext(self.stg.file_save)[1]
        if file_ext == self.stg.e_stg.binary_ext:
            # XRoar bugs when reading tokenized files outside a tape or disk
            # So we put them into a .cas cassete file
            cas = Convert()
            cas.file_load = self.stg.file_save
            cas.file_format = 'bas'
            cas.execute()
            new_file = os.path.splitext(self.stg.file_save)[0] + self.stg.CAS_EXT
        else:
            # XRoar needs an .asc (or .bas) extension to open ascii files
            new_file = os.path.splitext(self.stg.file_save)[0] + self.stg.ASC_EXT
            shutil.copy(self.stg.file_save, new_file)

        self.stg.file_save = new_file

        if self.stg.run:
            emu = Emulator(self.stg)
            emu.run()

        # The .asc file is not needed anymore, remove after use
        if file_ext == self.stg.e_stg.ascii_ext:
            osremove(self.stg.file_save)


class Expose():
    '''Expose values up the dignified chain'''

    def __init__(self):

        # remTAGs
        # Keep self.remtags as an empty dictionary if no remtag to pass
        remtag = namedtuple('remtag', 'name help metavar')
        self.remtags = {'XRoar': [remtag('EM_RUN', 'Open XRoar and run the code', 'True or false'),
                                  remtag('EM_CONFIG', 'Load XRoar with a custom config', 'Config_file'),
                                  remtag('EM_MACHINE', 'Load XRoar with a custom machine', 'Machine_name'),
                                  remtag('EM_BAS', 'Load XRoar with a custom Color Basic', 'Color_basic_rom'),
                                  remtag('EM_EXTBAS', 'Load XRoar with a custom Extended Basic', 'Extended_basic_rom'),
                                  remtag('EM_CART', 'Load XRoar with a custom cartridge', 'Cartridge_rom'),
                                  remtag('EM_DOS', 'Load XRoar with a DOS interface', 'True or false'),
                                  remtag('EM_NORATELIMIT', 'Load XRoar with rate limit on or off', 'True or false'),
                                  remtag('EM_VERBOSE', 'Level of information given', '0-5')]}

        # Command line arguments
        # Keep self.parser even if none argument added
        self.parser = argparse.ArgumentParser(add_help=False)
        arg_group = self.parser.add_argument_group('XRoar')
        arg_group.add_argument('--em_run', help='Open XRoar and run the code.', action='store_true', default=None),
        arg_group.add_argument('--em_config', help='Load XRoar with a custom config.', metavar='Config_file'),
        arg_group.add_argument('--em_machine', help='Load XRoar with a custom machine.', metavar='Machine_name'),
        arg_group.add_argument('--em_bas', help='Load XRoar with a custom Color Basic.', metavar='Color_basic_rom'),
        arg_group.add_argument('--em_extbas', help='Load XRoar with a custom Extended Basic.', metavar='Extended_basic_rom'),
        arg_group.add_argument('--em_cart', help='Load XRoar with a custom cartridge.', metavar='Cartridge_rom'),
        arg_group.add_argument('--em_dos', help='Load XRoar with a DOS interface.', action='store_true', default=None),
        arg_group.add_argument('--em_noratelimit', help='Load XRoar without rate limit.', action='store_true', default=None),
        arg_group.add_argument('--em_verbose', help='Level of information given.', type=int, metavar='0-5')


class Settings:
    def __init__(self, e_stg):
        super(Settings, self).__init__()
        self.e_stg = e_stg

        # Settings
        self.run = False            # Open XRoar and run the code
        self.config = ''            # Load XRoar with a custom config
        self.machine = ''           # Load XRoar with a custom machine
        self.bas = ''               # Load XRoar with a custom Color Basic
        self.extbas = ''            # Load XRoar with a custom Extended Basic
        self.cart = ''              # Load XRoar with a custom cartridge
        self.dos = False            # Load XRoar with a custom cartridge
        self.noratelimit = False    # Load XRoar with rate limit on or off
        self.verbose = 3            # Level of information given
        self.emulator_path = ''     # Path to the emulator to run the program ('' = local path)

        # Settings from Badig
        self.CURRENT_SYSTEM = self.e_stg.CURRENT_SYSTEM    # Current OS
        self.line_list = self.e_stg.line_list
        self.file_save = self.e_stg.file_save
        self.file_path = self.e_stg.file_path
        self.e_args = e_stg.args

        # Constants
        self.INI_FILE = 'emulator_interface.ini'
        self.LOCAL_PATH = os.path.split(os.path.abspath(__file__))[0]
        self.INI_WIN = 'WINDOWS'
        self.INI_LNX = 'LINUX'
        self.INI_MAC = 'DARWIN'
        self.ASC_EXT = '.ASC'
        self.CAS_EXT = '.CAS'

    def str2bol(self, string, same, name):
        '''String to Bool
        string = string to convert to boolean
        same = fallback value if string is empty
        name = name of the object for error reporting'''

        if string.upper() == 'TRUE':
            boolean = True
        elif string.upper() == 'FALSE':
            boolean = False
        elif string == '':
            boolean = same
        else:
            infolog.log(1, f'Remtag must be true or false: {name} = {string}')

        return boolean

    def init(self):
        '''Initialize settings'''

        self.get_ini()

        # Add local path if none is given
        if not os.path.dirname(self.emulator_path):
            self.emulator_path = os.path.join(self.LOCAL_PATH, self.emulator_path)

        # Get passed command line arguments
        self.run = self.run if self.e_args.em_run is None else self.e_args.em_run
        self.config = self.config if self.e_args.em_config is None else self.e_args.em_config
        self.machine = self.machine if self.e_args.em_machine is None else self.e_args.em_machine
        self.bas = self.bas if self.e_args.em_bas is None else self.e_args.em_bas
        self.extbas = self.extbas if self.e_args.em_extbas is None else self.e_args.em_extbas
        self.cart = self.cart if self.e_args.em_cart is None else self.e_args.em_cart
        self.dos = self.dos if self.e_args.em_dos is None else self.e_args.em_dos
        self.noratelimit = self.noratelimit if self.e_args.em_noratelimit is None else self.e_args.em_noratelimit
        self.verbose = self.verbose if self.e_args.em_verbose is None else self.e_args.em_verbose

        # Get passed remtags
        self.run = self.str2bol(self.e_stg.code_remtags.get('EM_RUN', str(self.run)), self.run, 'em_run')
        self.config = self.e_stg.code_remtags.get('EM_CONFIG', self.config) or self.config
        self.machine = self.e_stg.code_remtags.get('EM_MACHINE', self.machine) or self.machine
        self.bas = self.e_stg.code_remtags.get('EM_BAS', self.bas) or self.bas
        self.extbas = self.e_stg.code_remtags.get('EM_EXTBAS', self.extbas) or self.extbas
        self.cart = self.e_stg.code_remtags.get('EM_CART', self.cart) or self.cart
        self.dos = self.str2bol(self.e_stg.code_remtags.get('EM_DOS', str(self.dos)), self.dos, 'em_dos')
        self.noratelimit = self.str2bol(self.e_stg.code_remtags.get('EM_NORATELIMIT', str(self.noratelimit)), self.noratelimit, 'em_noratelimit')
        try:
            self.verbose = int(self.e_stg.code_remtags.get('EM_VERBOSE', self.verbose) or self.verbose)
        except ValueError as e:
            infolog.log(1, f'Remtag "em_verbose" must be a number: {e}')

        infolog.level = self.verbose

    def get_ini(self):
        '''Read the .ini file if present using the defaults from the variables'''

        ini_path = os.path.join(self.LOCAL_PATH, self.INI_FILE)
        if os.path.isfile(ini_path):
            ini_section = self.CURRENT_SYSTEM
            config = configparser.ConfigParser()
            config.sections()
            try:
                config.read(ini_path)
                config_sec = config['CONFIGS']
                self.run = config_sec.get('run') or self.run
                self.config = config_sec.get('config') or self.config
                self.machine = config_sec.get('machine') or self.machine
                self.bas = config_sec.get('bas') or self.bas
                self.extbas = config_sec.get('extbas') or self.extbas
                self.cart = config_sec.get('cart') or self.cart
                self.dos = config_sec.getboolean('dos') if config_sec.get('dos') != '' else self.dos
                self.noratelimit = config_sec.getboolean('noratelimit') if config_sec.get('noratelimit') != '' else self.noratelimit
                self.verbose = int(config_sec.get('verbose') or self.verbose)
                paths_sec = config[ini_section]
                self.emulator_path = paths_sec.get('emulator_path') or self.emulator_path
            except (ValueError, configparser.NoOptionError) as e:
                infolog.log(1, f'Problem with: {self.INI_FILE}: ' + str(e))


class Emulator:
    def __init__(self, stg):
        self.stg = stg

    def output(self, output_text, proc):
        fail_words = ['cannot open', 'failed to open', 'Invalid CRC']
        if output_text.strip() != '':
            if any(word in output_text for word in fail_words):
                output_text = output_text.replace('WARNING: ', '')
                proc.kill()
                infolog.log(1, output_text.rstrip())
            elif 'WARNING:' in output_text:
                output_text = output_text.replace('WARNING: ', '')
                infolog.log(2, output_text.rstrip())
            elif output_text[:1] != '\t':
                infolog.log(5, output_text.rstrip())
            else:
                infolog.log(5, output_text.strip())

    def run(self):
        '''Run XRoar with the given arguments'''

        infolog.log(3, 'XRoar')

        # Check if the emulator exists on the given path
        if self.stg.CURRENT_SYSTEM == self.stg.INI_WIN or self.stg.CURRENT_SYSTEM == self.stg.INI_LNX:
            if not os.path.isfile(self.stg.emulator_path):
                infolog.log(1, f'Emulator not found: {self.stg.emulator_path}')
        elif self.stg.CURRENT_SYSTEM == self.stg.INI_MAC:
            if not os.path.isdir(self.stg.emulator_path):
                infolog.log(1, f'Emulator not found: {self.stg.emulator_path}')

        # Set the emulator execution command based on the machine
        self.stg.file_path = self.stg.file_path.replace(' ', r'\ ')  # Escaping spaces for cmd
        if self.stg.CURRENT_SYSTEM == self.stg.INI_WIN:
            self.stg.file_path = self.stg.file_path.replace('\\', '/')  # cmd apparently needs forward slashes even on Windows
            cmd = [self.stg.emulator_path]
        elif self.stg.CURRENT_SYSTEM == self.stg.INI_LNX:
            cmd = [self.stg.emulator_path]
        elif self.stg.CURRENT_SYSTEM == self.stg.INI_MAC:
            cmd = [os.path.join(self.stg.emulator_path, 'contents', 'macos', 'xroar')]

        infolog.log(3, f'Opening: {os.path.basename(self.stg.file_save)}')

        using_config = 'default config'
        emu_folder = os.path.dirname(self.stg.emulator_path)
        if self.stg.config != '':
            using_config = self.stg.config
            config_path = os.path.join(emu_folder, self.stg.config)
            cmd.extend(['-c', config_path])
        infolog.log(4, f'Using: {using_config}')

        # Windows needs -rompath
        if self.stg.CURRENT_SYSTEM == self.stg.INI_WIN:
            cmd.extend(['-rompath', emu_folder])

        if self.stg.machine != '':
            cmd.extend(['-machine', self.stg.machine])
            infolog.log(4, f'Machine profile: {self.stg.machine}')

        if self.stg.bas != '':
            cmd.extend(['-bas', self.stg.bas])
            infolog.log(4, f'Color Basic: {self.stg.bas}')

        if self.stg.extbas != '':
            cmd.extend(['-extbas', self.stg.extbas])
            infolog.log(4, f'Extended Basic: {self.stg.extbas}')

        if self.stg.cart != '':
            cmd.extend(['-machine-cart', self.stg.cart])
            infolog.log(4, f'Default cartridge: {self.stg.cart}')

        if self.stg.dos:
            cmd.extend(['-cart', 'rsdos'])
            infolog.log(4, f'RSDOS interface')

        if self.stg.noratelimit:
            cmd.append('-no-ratelimit')
            infolog.log(4, f'No rate limit applied')

        cmd.extend(['-run', self.stg.file_save])
        cmd.extend(['-v', '2', '-debug-file', '0x0004'])

        proc = subprocess.Popen(cmd, bufsize=1,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                encoding='utf-8',
                                cwd=emu_folder)
        for line in iter(proc.stdout.readline, b''):
            self.output(line, proc)
            poll = proc.poll()
            if poll is not None:
                print()
                break
