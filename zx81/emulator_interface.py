import argparse
import configparser
import os.path
import subprocess
from collections import namedtuple

from support.helper import Infolog


infolog = Infolog()


class Run:
    def __init__(self, e_stg):
        self.e_stg = e_stg

    def run(self):
        self.stg = Settings(self.e_stg)
        self.stg.init()

        if self.stg.run:
            if os.path.splitext(self.stg.file_save)[1].lower() != self.stg.binary_ext:
                infolog.log(1, 'EightyOne requires the tokenized .P output.')
            Emulator(self.stg).run()


class Expose:
    def __init__(self):
        remtag = namedtuple('remtag', 'name help metavar')
        self.remtags = {
            'EightyOne': [
                remtag('EM_RUN', 'Open EightyOne with the tokenized program.', 'True or false'),
            ]
        }

        self.parser = argparse.ArgumentParser(add_help=False)
        arg_group = self.parser.add_argument_group('EightyOne')
        arg_group.add_argument('--em_run', action='store_true', default=None,
                               help='Open EightyOne with the tokenized program.')


class Settings:
    def __init__(self, e_stg):
        self.e_stg = e_stg
        self.run = False
        self.emulator_path = r'C:\zeddy\EightyOne.exe'
        self.file_save = e_stg.file_save
        self.binary_ext = e_stg.binary_ext.lower()
        self.e_args = e_stg.args
        self.code_remtags = e_stg.code_remtags
        self.LOCAL_PATH = os.path.dirname(os.path.abspath(__file__))
        self.INI_FILE = 'emulator_interface.ini'

    def init(self):
        ini_path = os.path.join(self.LOCAL_PATH, self.INI_FILE)
        if os.path.isfile(ini_path):
            config = configparser.ConfigParser()
            config.read(ini_path)
            configs = config['CONFIGS']
            value = configs.get('run', '')
            if value:
                self.run = configs.getboolean('run')
            section = self.e_stg.CURRENT_SYSTEM
            if config.has_option(section, 'emulator_path'):
                self.emulator_path = config.get(section, 'emulator_path')

        if self.e_args.em_run:
            self.run = True
        if 'EM_RUN' in self.code_remtags:
            self.run = self.code_remtags['EM_RUN'].strip().upper() == 'TRUE'


class Emulator:
    def __init__(self, stg):
        self.stg = stg

    def run(self):
        if not os.path.isfile(self.stg.emulator_path):
            infolog.log(1, f'EightyOne not found: {self.stg.emulator_path}')

        infolog.log(3, 'EightyOne')
        infolog.log(4, f'Opening: {os.path.basename(self.stg.file_save)}')
        subprocess.Popen([self.stg.emulator_path, self.stg.file_save])