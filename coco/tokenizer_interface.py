# This module is responsible for opening, sending information and controlling the Tokenizer

import os.path
import argparse
import subprocess
import configparser
from os import remove as osremove
from collections import namedtuple

from support.helper import Infolog

infolog = Infolog()


class Run:
    def __init__(self, e_stg):
        self.e_stg = e_stg

    def run(self):
        self.stg = Settings(self.e_stg)
        self.stg.init()

        if self.stg.tokenize:
            tok = Tokenizer(self.stg)
            tok.run()


class Expose():
    '''Expose values up the dignified chain'''

    def __init__(self):
        # remTAGs
        remtag = namedtuple('remtag', 'name help metavar')
        self.remtags = {'Toolshed decb (tokenizer)': [remtag('TK_TOKENIZE', 'Tokenize the ASCII code', 'True or false'),
                                                      remtag('TK_DEL_ASCII', 'Delete the ASCII file after tokenizing', 'Machine_name'),
                                                      remtag('TK_VERBOSE', 'Level of information given', '0-4')]}

        # Command line arguments
        # Keep self.parser iven if none argument added
        self.parser = argparse.ArgumentParser(add_help=False)
        arg_group = self.parser.add_argument_group('Toolshed decb (tokenizer)')
        arg_group.add_argument('--tk_tokenize', help='Tokenize the ASCII code.', action='store_true', default=None),
        arg_group.add_argument('--tk_del_ascii', help='Delete the ASCII file after tokenizing.', action='store_true', default=None),
        arg_group.add_argument('--tk_verbose', help='Level of information given.', type=int, metavar='0-4')


class Settings:
    def __init__(self, e_stg):
        super(Settings, self).__init__()
        self.e_stg = e_stg

        # Settings
        self.tokenize = False      # Tokenize
        self.del_ascii = False     # Delete the original ASCII file
        self.verbose = 3           # Verbosity level: 0 silent, 1 errors, 2 +warnings, 3 +headers, 4 +conversion dump

        # Settings from Badig
        self.file_save = self.e_stg.file_save
        self.ascii_ext = self.e_stg.ascii_ext
        self.binary_ext = self.e_stg.binary_ext
        self.e_args = self.e_stg.args

        # Constants
        self.INI_FILE = 'tokenizer_interface.ini'
        self.INI_WIN = 'WINDOWS'
        self.LOCAL_PATH = os.path.split(os.path.abspath(__file__))[0]

        self.DECB_FILE = 'decb'
        if self.e_stg.CURRENT_SYSTEM == self.INI_WIN:
            self.DECB_FILE += '.exe'
        self.DECB_FILE = os.path.join(self.LOCAL_PATH, self.DECB_FILE)

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

        # Get passed command line arguments
        self.tokenize = self.tokenize if self.e_args.tk_tokenize is None else self.e_args.tk_tokenize
        self.del_ascii = self.del_ascii if self.e_args.tk_del_ascii is None else self.e_args.tk_del_ascii
        self.verbose = self.verbose if self.e_args.tk_verbose is None else self.e_args.tk_verbose

        # Get passed remtags
        self.tokenize = self.str2bol(self.e_stg.code_remtags.get('TK_TOKENIZE', str(self.tokenize)), self.tokenize, 'tokenize')
        self.del_ascii = self.str2bol(self.e_stg.code_remtags.get('TK_DEL_ASCII', str(self.del_ascii)), self.del_ascii, 'del_ascii')
        try:
            self.verbose = int(self.e_stg.code_remtags.get('TK_VERBOSE', self.verbose) or self.verbose)
        except ValueError as e:
            infolog.log(1, f'Remtag "tk_verbose" must be a number: {e}')

        infolog.level = self.verbose

    def get_ini(self):
        '''Read the .ini file if present using the defaults from the variables'''

        ini_path = os.path.join(self.LOCAL_PATH, self.INI_FILE)
        if os.path.isfile(ini_path):
            config = configparser.ConfigParser()
            config.sections()
            try:
                config.read(ini_path)
                config_sec = config['CONFIGS']
                self.tokenize = config_sec.getboolean('tokenize') if config_sec.get('tokenize') != '' else self.tokenize
                self.del_ascii = config_sec.getboolean('del_ascii') if config_sec.get('del_ascii') != '' else self.del_ascii
                self.verbose = int(config_sec.get('verbose') or self.verbose)
            except (ValueError, configparser.NoOptionError) as e:
                infolog.log(1, f'Problem with: {self.INI_FILE}: ' + str(e))


class Tokenizer:
    def __init__(self, stg):
        self.stg = stg

    def run(self):

        infolog.log(3, f'Toolshed Decb')
        infolog.log(3, f'Tokenizing: {os.path.basename(self.stg.file_save)}')

        if os.path.isfile(self.stg.DECB_FILE):
            file_load = self.stg.file_save
            file_save = os.path.splitext(self.stg.file_save)[0] + self.stg.binary_ext

            infolog.log(4, f'Converting file: {file_load}')
            infolog.log(4, f'to file: {file_save}')
            decb_cmd = [self.stg.DECB_FILE, 'copy', file_load, file_save, '-t']
            decb_output = subprocess.check_output(decb_cmd, encoding='utf-8')

            out_line = ''
            for line in decb_output:
                out_line += line
                if line == '\n':
                    infolog.log(4, out_line.rstrip())
                    out_line = ''
        else:
            infolog.log(1, f'Decb not found: {self.stg.DECB_FILE}')

        if self.stg.del_ascii:
            if os.path.isfile(file_save):
                infolog.log(4, f'Deleting file: {file_load}')
                osremove(file_load)
            else:
                infolog.log(2, f'Converted file not found: {file_save}')
                infolog.log(2, f'Source not deleted: {file_load}')

        self.stg.file_bin = file_save
