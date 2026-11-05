"""Expose Spectrum tape and optional snapshot generation to Basic Dignified."""

import argparse
import configparser
import subprocess
import sys
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
        self.remtags = {'Spectrum output': [
            remtag('TK_TOKENIZE', 'Generate Spectrum tapes or snapshots.', 'True or false'),
            remtag('TK_NAME', 'Name stored in the tape header.', '1-10 ASCII characters'),
            remtag('TK_FORMAT', 'Tape/snapshot format to generate.', 'tap, tzx, both, z80, sna, all'),
            remtag('TK_AUTORUN', 'BASIC autorun line (-1 disables).', '-1 or 0-9999'),
        ]}
        self.parser = argparse.ArgumentParser(add_help=False)
        group = self.parser.add_argument_group('Spectrum output')
        group.add_argument('--tk_tokenize', action='store_true', default=None,
                           help='Generate Spectrum tapes or optional snapshots.')
        group.add_argument('--tk_name', help='Tape header name (1-10 ASCII characters).')
        group.add_argument('--tk_format', choices=('tap', 'tzx', 'both', 'z80', 'sna', 'all'),
                           help='Output format; both=tapes, all=tapes+snapshots (default: tap).')
        group.add_argument('--tk_autorun', type=int,
                           help='BASIC autorun line: 0-9999, or -1 to disable.')


def write_output(destination, content):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
        temporary.replace(destination)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


class Run:
    def __init__(self, stg):
        self.stg = stg

    def run(self, force=False):
        config = configparser.ConfigParser()
        path = Path(__file__).with_name('tokenizer_interface.ini')
        try:
            with path.open(encoding='ascii') as stream:
                config.read_file(stream)
            enabled = config.getboolean('CONFIGS', 'tokenize')
            name = config.get('CONFIGS', 'name')
            tape_format = config.get('CONFIGS', 'format')
            autorun = config.getint('CONFIGS', 'autorun')
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
            if force and not enabled:
                fail('EM_RUN requires tokenization; TK_TOKENIZE=False conflicts with it')
        enabled = enabled or force
        name = remtags.get('TK_NAME', name)
        tape_format = remtags.get('TK_FORMAT', self.stg.args.tk_format or tape_format).strip().lower()
        if tape_format not in ('tap', 'tzx', 'both', 'z80', 'sna', 'all'):
            fail('TK_FORMAT must be tap, tzx, both, z80, sna or all')
        if self.stg.args.tk_autorun is not None:
            autorun = self.stg.args.tk_autorun
        elif force and autorun == -1 and 'TK_AUTORUN' not in remtags:
            autorun = 0
        try:
            autorun = int(remtags.get('TK_AUTORUN', autorun))
        except ValueError:
            fail('TK_AUTORUN must be -1 or a line within 0..9999')
        if not -1 <= autorun <= 9999:
            fail('TK_AUTORUN must be -1 or a line within 0..9999')
        if not enabled:
            return ()
        if not name and (self.stg.args.tk_name is not None or 'TK_NAME' in remtags):
            fail('Tape name must contain 1..10 printable ASCII characters')
        source = Path(self.stg.file_save)
        formats = (('tap', 'tzx', 'z80', 'sna') if tape_format == 'all' else
                   ('tap', 'tzx') if tape_format == 'both' else (tape_format,))
        destinations = [source.with_suffix('.' + extension) for extension in formats]
        if any(source.resolve() == destination.resolve() for destination in destinations):
            fail('ASCII source and Spectrum destination must be different files')
        model = self.stg.c_stg.sp_model
        if model != '48' and any(extension in formats for extension in ('z80', 'sna')):
            fail('Z80/SNA snapshots are only supported for --sp_model 48')
        name = name or source.stem[:10]
        try:
            program = tokenize(source.read_text(encoding='latin1'), model=model)
            tape = make_tap(program, name, None if autorun == -1 else autorun)
            outputs = {'tap': tape}
            if 'tzx' in formats:
                outputs['tzx'] = make_tzx(program, name, None if autorun == -1 else autorun)
            if any(extension in formats for extension in ('z80', 'sna')):
                with tempfile.TemporaryDirectory(prefix='badig-snapshot-') as folder:
                    workspace = Path(folder)
                    (workspace / 'input.tap').write_bytes(tape)
                    result = subprocess.run(
                        [sys.executable, '-B', str(Path(__file__).with_name('snapshot_zxspectrum.py'))],
                        cwd=workspace, capture_output=True, text=True, timeout=120)
                    if result.returncode:
                        raise SpectrumTokenizeError(
                            result.stderr.strip() or result.stdout.strip()
                            or f'Snapshot engine exited with status {result.returncode}')
                    for extension in ('z80', 'sna'):
                        outputs[extension] = (workspace / ('state.' + extension)).read_bytes()
            for destination, extension in zip(destinations, formats):
                write_output(destination, outputs[extension])
        except (OSError, subprocess.TimeoutExpired, SpectrumTokenizeError) as error:
            fail(f'Spectrum output: {error}')
        logger = Infolog()
        logger.level = self.stg.verbose_level
        for destination in destinations:
            logger.log(3, f'Spectrum output: {destination}')
        return tuple(destinations)
