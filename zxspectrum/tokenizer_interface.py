"""Expose Spectrum TAP generation to Basic Dignified."""

import argparse
import configparser
import tempfile
from collections import namedtuple
from pathlib import Path

from support.helper import Infolog

from .badig_zxspectrum import fail
from .tape_zxspectrum import make_tap
from .tokenizer_zxspectrum import SpectrumTokenizeError, tokenize


class Expose:
    def __init__(self):
        remtag = namedtuple('remtag', 'name help metavar')
        self.remtags = {'Spectrum TAP': [
            remtag('TK_TOKENIZE', 'Generate a tokenized Spectrum TAP.', 'True or false'),
            remtag('TK_NAME', 'Name stored in the tape header.', '1-10 ASCII characters'),
        ]}
        self.parser = argparse.ArgumentParser(add_help=False)
        group = self.parser.add_argument_group('Spectrum TAP')
        group.add_argument('--tk_tokenize', action='store_true', default=None,
                           help='Generate a tokenized Spectrum TAP.')
        group.add_argument('--tk_name', help='Tape header name (1-10 ASCII characters).')


class Run:
    def __init__(self, stg):
        self.stg = stg

    def run(self):
        config = configparser.ConfigParser()
        path = Path(__file__).with_name('tokenizer_interface.ini')
        try:
            with path.open(encoding='ascii') as stream:
                config.read_file(stream)
            enabled = config.getboolean('CONFIGS', 'tokenize')
            name = config.get('CONFIGS', 'name')
        except (OSError, ValueError, configparser.Error) as error:
            fail(f'Spectrum tokenizer configuration: {error}')
        if self.stg.args.tk_tokenize is not None:
            enabled = self.stg.args.tk_tokenize
        if self.stg.args.tk_name is not None:
            name = self.stg.args.tk_name
        remtags = self.stg.code_remtags
        if 'TK_TOKENIZE' in remtags:
            value = remtags['TK_TOKENIZE'].strip().upper()
            if value not in ('TRUE', 'FALSE'):
                fail('TK_TOKENIZE must be True or False')
            enabled = value == 'TRUE'
        name = remtags.get('TK_NAME', name)
        if not enabled:
            return
        if not name and (self.stg.args.tk_name is not None or 'TK_NAME' in remtags):
            fail('Tape name must contain 1..10 printable ASCII characters')
        source = Path(self.stg.file_save)
        destination = source.with_suffix('.tap')
        if source.resolve() == destination.resolve():
            fail('ASCII source and TAP destination must be different files')
        name = name or source.stem[:10]
        temporary = None
        try:
            program = tokenize(source.read_text(encoding='latin1'))
            tape = make_tap(program, name)
            with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(tape)
            temporary.replace(destination)
        except (OSError, SpectrumTokenizeError) as error:
            fail(f'Spectrum TAP: {error}')
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()
        logger = Infolog()
        logger.level = self.stg.verbose_level
        logger.log(3, f'Spectrum TAP: {destination}')
