# This module is responsible for opening, sending information and controlling the Tokenizer

import os.path
import argparse
import configparser
from collections import namedtuple

from support.helper import Infolog

infolog = Infolog()

try:
    from .msxbatoken import msxbatoken as MSXBatoken
except ModuleNotFoundError as e:
    infolog.log(1, f'Tokenizer not found: {e}')


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
        self.remtags = {'MSX Batoken': [remtag('TK_TOKENIZE', 'Tokenize the ASCII code.', 'True or false'),
                                        remtag('TK_LIST', 'Export a list file.', 'Config_file'),
                                        remtag('TK_DEL_ASCII', 'Delete the ASCII file after tokenizing.', 'Machine_name'),
                                        remtag('TK_VERBOSE', 'Level of information given.', '0-5')]}

        # Command line arguments
        # Keep self.parser iven if none argument added
        self.parser = argparse.ArgumentParser(add_help=False)
        arg_group = self.parser.add_argument_group('MSX Batoken')
        arg_group.add_argument('--tk_tokenize', help='Tokenize the ASCII code.', action='store_true', default=None),
        arg_group.add_argument('--tk_list', help='Export a list file.', const=16, type=int, nargs='?', metavar='1-32'),
        arg_group.add_argument('--tk_del_ascii', help='Delete the ASCII file after tokenizing.', action='store_true', default=None),
        arg_group.add_argument('--tk_verbose', help='Level of information given.', type=int, metavar='0-5')


class Settings:
    def __init__(self, e_stg):
        super(Settings, self).__init__()
        self.e_stg = e_stg

        # Settings
        self.tokenize = False      # Tokenize
        self.list = 0              # Save a list file
        self.del_ascii = False     # Delete the original ASCII file
        self.verbose = 3           # Verbosity level: 0 silent, 1 errors, 2 +warnings, 3 +headers, 4 +conversion dump

        # Settings from Badig
        self.file_save = self.e_stg.file_save
        self.ascii_ext = self.e_stg.ascii_ext
        self.binary_ext = self.e_stg.binary_ext
        self.e_args = self.e_stg.args

        # Extra info
        self.list_ext = '.lmx'

        # Constants
        self.INI_FILE = 'tokenizer_interface.ini'
        self.LOCAL_PATH = os.path.split(os.path.abspath(__file__))[0]

    def str2bol(self, string, same, name):
        '''String to Bool
        string: string to convert to boolean
        same: fallback value if string is empty
        name: name of the object for error reporting'''

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
        self.list = self.list if self.e_args.tk_list is None else self.e_args.tk_list
        self.del_ascii = self.del_ascii if self.e_args.tk_del_ascii is None else self.e_args.tk_del_ascii
        self.verbose = self.verbose if self.e_args.tk_verbose is None else self.e_args.tk_verbose

        # Get passed remtags
        self.tokenize = self.str2bol(self.e_stg.code_remtags.get('TK_TOKENIZE', str(self.tokenize)), self.tokenize, 'tokenize')
        self.del_ascii = self.str2bol(self.e_stg.code_remtags.get('TK_DEL_ASCII', str(self.del_ascii)), self.del_ascii, 'del_ascii')
        try:
            err = 'tk_list'
            self.list = int(self.e_stg.code_remtags.get('TK_LIST', self.list) or self.list)
            err = 'tk_verbose'
            self.verbose = int(self.e_stg.code_remtags.get('TK_VERBOSE', self.verbose) or self.verbose)
        except ValueError as e:
            infolog.log(1, f'Remtag "{err}" must be a number: {e}')

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
                self.list = config_sec.get('list') or self.list
                self.del_ascii = config_sec.getboolean('del_ascii') if config_sec.get('del_ascii') != '' else self.del_ascii
                self.verbose = int(config_sec.get('verbose') or self.verbose)
            except (ValueError, configparser.NoOptionError) as e:
                infolog.log(1, f'Problem with: {self.INI_FILE}: {str(e)}')


class Tokenizer:
    def __init__(self, stg):
        self.stg = stg

    def run(self):

        tok = MSXBatoken

        tok_main = MSXBatoken.Main()

        tok_main.stg.init()

        tok_main.stg.file_load = self.stg.file_save
        tok_main.stg.file_save = os.path.splitext(self.stg.file_save)[0] + self.stg.binary_ext
        tok_main.stg.file_list = os.path.splitext(self.stg.file_save)[0] + self.stg.list_ext

        tok_main.stg.list = self.stg.list
        bytes_width = min(abs(self.stg.list), 32)
        tok_main.stg.width_byte = bytes_width * 2
        tok_main.stg.width_line = bytes_width * 3 + 7

        tok_main.stg.del_ascii = self.stg.del_ascii

        tok_main.stg.verbose = self.stg.verbose
        tok.info.level = self.stg.verbose

        tok_main.execute()

        self.stg.file_bin = tok_main.stg.file_save
