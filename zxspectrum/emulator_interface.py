"""Launch EightyOne with a private copy of a Spectrum 48K profile."""

import argparse
import configparser
import subprocess
import sys
import tempfile
from collections import namedtuple
from pathlib import Path

from support.helper import Infolog

from .badig_zxspectrum import fail


class Expose:
    def __init__(self):
        remtag = namedtuple('remtag', 'name help metavar')
        self.remtags = {'EightyOne': [
            remtag('EM_RUN', 'Open EightyOne and load the tape or snapshot.', 'True or false'),
            remtag('EM_PATH', 'Path to EightyOne.exe.', 'Executable'),
            remtag('EM_SETTING', 'Spectrum 48K INI to copy for this session.', 'INI file'),
        ]}
        self.parser = argparse.ArgumentParser(add_help=False)
        group = self.parser.add_argument_group('EightyOne (Windows)')
        group.add_argument('--em_run', action='store_true', default=None,
                           help='Generate Spectrum output and open EightyOne; wait until it closes.')
        group.add_argument('--em_path', help='Path to EightyOne.exe.')
        group.add_argument('--em_setting', help='48K profile to copy; original is not edited.')


class Settings:
    def __init__(self, stg):
        config = configparser.ConfigParser(interpolation=None)
        try:
            with Path(__file__).with_suffix('.ini').open(encoding='ascii') as stream:
                config.read_file(stream)
            self.run = config.getboolean('CONFIGS', 'run')
            path = config.get('CONFIGS', 'emulator_path')
            setting = config.get('CONFIGS', 'setting')
        except (OSError, ValueError, configparser.Error) as error:
            fail(f'EightyOne configuration: {error}')
        if stg.args.em_run is not None:
            self.run = stg.args.em_run
        if 'EM_RUN' in stg.code_remtags:
            value = stg.code_remtags['EM_RUN'].strip().upper()
            if value not in ('TRUE', 'FALSE'):
                fail('EM_RUN must be True or False')
            self.run = value == 'TRUE'
        path = stg.code_remtags.get('EM_PATH', stg.args.em_path if stg.args.em_path is not None else path)
        setting = stg.code_remtags.get(
            'EM_SETTING', stg.args.em_setting if stg.args.em_setting is not None else setting)
        self.path = Path(path).expanduser().resolve() if path else None
        self.setting = (Path(setting).expanduser().resolve() if setting else
                        Path(__file__).with_name('eightyone48.ini'))
        if self.run:
            if sys.platform != 'win32':
                fail('EightyOne integration currently requires Windows')
            if self.path is None or not self.path.is_file():
                fail('EightyOne executable not found; configure --em_path or EM_PATH')
            if not self.setting.is_file():
                fail(f'EightyOne profile not found: {self.setting}')


def run(stg, settings, tape):
    profile = configparser.ConfigParser(interpolation=None)
    try:
        with settings.setting.open(encoding='latin1') as stream:
            profile.read_file(stream)
        if profile.get('HARDWARE', 'MachineName') != '48K Spectrum':
            fail('EM_SETTING must select MachineName=48K Spectrum')
        if not profile.has_section('TZXMAN'):
            profile.add_section('TZXMAN')
        for key in ('FlashLoad', 'AutoStart', 'AutoLoad'):
            profile.set('TZXMAN', key, '1' if tape.suffix.lower() in ('.tap', '.tzx') else '0')
        logger = Infolog()
        logger.level = stg.verbose_level
        logger.log(3, f'EightyOne: {tape}; close the emulator to return to the converter')
        with tempfile.TemporaryDirectory(prefix='badig-spectrum-') as folder:
            temporary = Path(folder) / 'spectrum48.ini'
            with temporary.open('w', encoding='latin1') as stream:
                profile.write(stream)
            with subprocess.Popen([str(settings.path), str(temporary), str(tape.resolve())],
                                  cwd=settings.path.parent) as process:
                try:
                    result = process.wait()
                except KeyboardInterrupt:
                    process.terminate()
                    process.wait()
                    fail('EightyOne session interrupted')
                if result:
                    fail(f'EightyOne exited with status {result}')
    except (OSError, configparser.Error) as error:
        fail(f'EightyOne: {error}')
