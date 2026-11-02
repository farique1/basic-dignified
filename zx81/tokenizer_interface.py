import argparse
import configparser
import os.path
from collections import namedtuple

from support.helper import Infolog
from .tokenizer_zx81 import tokenize_file
from .tokenizer_zx81 import ZX81TokenizeError


infolog = Infolog()


class Run:
    def __init__(self, e_stg):
        self.e_stg = e_stg

    def run(self):
        self.stg = Settings(self.e_stg)
        self.stg.init()

        if self.stg.tokenize:
            infolog.log(3, 'ZX-81 tokenizer')
            infolog.log(4, f'Tokenizing: {os.path.basename(self.stg.file_save)}')
            try:
                tokenize_file(self.stg.file_save, self.stg.file_bin)
            except (OSError, ZX81TokenizeError) as error:
                infolog.log(1, f'Tokenizer failed: {error}')

            if self.stg.del_ascii:
                os.remove(self.stg.file_save)


class Expose:
    def __init__(self):
        remtag = namedtuple('remtag', 'name help metavar')
        self.remtags = {
            'ZX-81 tokenizer': [
                remtag('TK_TOKENIZE', 'Generate a tokenized .P file.', 'True or false'),
                remtag('TK_DEL_ASCII', 'Delete the .AZX file after tokenizing.', 'True or false'),
            ]
        }

        self.parser = argparse.ArgumentParser(add_help=False)
        arg_group = self.parser.add_argument_group('ZX-81 tokenizer')
        arg_group.add_argument('--tk_tokenize', action='store_true', default=None,
                               help='Generate the ZX-81 .P file.')
        arg_group.add_argument('--tk_ascii_only', action='store_true',
                               help='Generate only the numbered .AZX file.')
        arg_group.add_argument('--tk_del_ascii', action='store_true', default=None,
                       help='Delete the .AZX file after tokenizing.')


class Settings:
    def __init__(self, e_stg):
        self.e_stg = e_stg
        self.tokenize = True
        self.del_ascii = False
        self.file_save = e_stg.file_save
        self.ascii_ext = e_stg.ascii_ext
        self.binary_ext = e_stg.binary_ext
        self.file_bin = os.path.splitext(self.file_save)[0] + self.binary_ext
        self.e_args = e_stg.args
        self.INI_FILE = 'tokenizer_interface.ini'
        self.LOCAL_PATH = os.path.dirname(os.path.abspath(__file__))

    def init(self):
        ini_path = os.path.join(self.LOCAL_PATH, self.INI_FILE)
        if os.path.isfile(ini_path):
            config = configparser.ConfigParser()
            config.read(ini_path)
            configs = config['CONFIGS']
            value = configs.get('tokenize', '')
            if value:
                self.tokenize = configs.getboolean('tokenize')
            value = configs.get('del_ascii', '')
            if value:
                self.del_ascii = configs.getboolean('del_ascii')

        if self.e_args.tk_tokenize:
            self.tokenize = True
        if self.e_args.tk_ascii_only:
            self.tokenize = False
        if self.e_args.tk_del_ascii is not None:
            self.del_ascii = self.e_args.tk_del_ascii

        remtags = self.e_stg.code_remtags
        if 'TK_TOKENIZE' in remtags:
            self.tokenize = remtags['TK_TOKENIZE'].strip().upper() == 'TRUE'
        if 'TK_DEL_ASCII' in remtags:
            self.del_ascii = remtags['TK_DEL_ASCII'].strip().upper() == 'TRUE'