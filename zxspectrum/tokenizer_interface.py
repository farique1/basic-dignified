"""Expose Spectrum TAP generation to Basic Dignified."""

import argparse
import configparser
import tempfile
from collections import namedtuple
from pathlib import Path

from support.helper import Infolog

from .badig_zxspectrum import fail
from .tape_zxspectrum import make_tap, make_tzx
from .tokenizer_zxspectrum import SpectrumTokenizeError, tokenize


class Expose:
    def __init__(self):
        remtag = namedtuple('remtag', 'name help metavar')
        self.remtags = {'Spectrum TAP': [
            remtag('TK_TOKENIZE', 'Generate a tokenized Spectrum TAP.', 'True or false'),
            remtag('TK_NAME', 'Name stored in the tape header.', '1-10 ASCII characters'),
            remtag('TK_FORMAT', 'Tape container to generate.', 'tap, tzx or both'),
        ]}
        self.parser = argparse.ArgumentParser(add_help=False)
        group = self.parser.add_argument_group('Spectrum TAP')
        group.add_argument('--tk_tokenize', action='store_true', default=None,
                           help='Generate a tokenized Spectrum TAP.')
        group.add_argument('--tk_name', help='Tape header name (1-10 ASCII characters).')
        group.add_argument('--tk_format', choices=('tap', 'tzx', 'both'),
                           help='Tape container (default: tap).')


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
            tape_format = config.get('CONFIGS', 'format')
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
        tape_format = remtags.get('TK_FORMAT', self.stg.args.tk_format or tape_format).strip().lower()
        if tape_format not in ('tap', 'tzx', 'both'):
            fail('TK_FORMAT must be tap, tzx or both')
        if not enabled:
            return
        if not name and (self.stg.args.tk_name is not None or 'TK_NAME' in remtags):
            fail('Tape name must contain 1..10 printable ASCII characters')
        source = Path(self.stg.file_save)
        formats = ('tap', 'tzx') if tape_format == 'both' else (tape_format,)
        destinations = [source.with_suffix('.' + extension) for extension in formats]
        if any(source.resolve() == destination.resolve() for destination in destinations):
            fail('ASCII source and tape destination must be different files')
        name = name or source.stem[:10]
        try:
            program = tokenize(source.read_text(encoding='latin1'))
            tapes = [(make_tap if extension == 'tap' else make_tzx)(program, name)
                     for extension in formats]
            for destination, tape in zip(destinations, tapes):
                temporary = None
                try:
                    with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as stream:
                        temporary = Path(stream.name)
                        stream.write(tape)
                    temporary.replace(destination)
                finally:
                    if temporary is not None and temporary.exists():
                        temporary.unlink()
        except (OSError, SpectrumTokenizeError) as error:
            fail(f'Spectrum tape: {error}')
        logger = Infolog()
        logger.level = self.stg.verbose_level
        for destination in destinations:
            logger.log(3, f'Spectrum tape: {destination}')
