import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from . import emulator_interface, tokenizer_interface
from .tape_zxspectrum import MAX_PROGRAM_BYTES, make_tap, make_tzx
from .tokenizer_zxspectrum import SpectrumTokenizeError, encode_number, tokenize


ROOT = Path(__file__).resolve().parents[1]


class TokenizerTests(unittest.TestCase):
    def test_known_rom_tokens_and_line_layout(self):
        self.assertEqual(
            tokenize('10 PRINT "HI"\n20 STOP'),
            bytes.fromhex('000a0700f520224849220d00140200e20d'))

    def test_numbers_use_integer_and_floating_point_formats(self):
        vectors = {
            '0': '0000000000',
            '1': '0000010000',
            '255': '0000ff0000',
            '256': '0000000100',
            '65535': '0000ffff00',
            '65536': '9100000000',
            '.5': '8000000000',
            '0.1': '7d4ccccccd',
            '1e2': '0000640000',
        }
        for text, expected in vectors.items():
            with self.subTest(text=text):
                self.assertEqual(encode_number(text).hex(), expected)
        body = tokenize('10 LET score2=-1')[4:]
        self.assertEqual(body, b'\xf1 score2=-1\x0e\x00\x00\x01\x00\x00\x0d')

    def test_strings_and_rem_are_not_tokenized_as_code(self):
        body = tokenize('10 PRINT "GO TO 20 ""HI"""\'"X": REM 30: PRINT')[4:]
        self.assertEqual(body, b'\xf5 "GO TO 20 ""HI"""\'"X": \xea 30: PRINT\x0d')

    def test_jump_alias_and_relational_tokens(self):
        self.assertEqual(
            tokenize('10 IF count<=3 THEN GOTO 10'),
            tokenize('10 IF count<=3 THEN GO TO 10'))
        self.assertIn(b'\xc7', tokenize('10 IF count<=3 THEN GO TO 10'))
        self.assertIn(b'\xec', tokenize('10 IF count<=3 THEN GO TO 10'))

    def test_native_function_and_string_array_bytes(self):
        self.assertEqual(tokenize('10 PRINT LEN a$'),
                         bytes.fromhex('000a0700f520b12061240d'))
        self.assertIn(b'\xe9 a$(2\x0e\x00\x00\x02\x00\x00,',
                      tokenize('10 DIM a$(2,5)'))
        self.assertIn(b'a$(1\x0e\x00\x00\x01\x00\x00 \xcc ',
                      tokenize('10 PRINT a$(1 TO 2)'))

    def test_rejects_unrepresentable_or_unsupported_source(self):
        sources = (
            '', 'PRINT "HI"', '0 STOP', '10 STOP\n10 STOP', '20 STOP\n10 STOP',
            '10000 STOP', '10 PRINT "oops', '10 PRINT 1e+', '10 LET n=1e1000',
            '10 PRINT 1e-1000', '10 PRINT "\u00e9"', '10 CAT',
            '10 LET name$="X"', '10 LET total_score=1', '10 LET array(1)=2',
            '10 a=1', '10 IF a=1 THEN 20', '10 PRINT 1:',
            '10 FOR counter=1 TO 2', '10 NEXT count', '10 DEF FN f(x)=x',
            '10 PRINT 1e999999999999999999999999',
        )
        for source in sources:
            with self.subTest(source=source):
                with self.assertRaises(SpectrumTokenizeError):
                    tokenize(source)


class TapeTests(unittest.TestCase):
    def test_autorun_header_and_validation(self):
        program = tokenize('10 STOP')
        for line in (0, 10, 9999):
            with self.subTest(line=line):
                tap = make_tap(program, 'RUN', line)
                self.assertEqual(struct.unpack_from('<H', tap, 16)[0], line)
                checksum = 0
                for byte in tap[2:21]:
                    checksum ^= byte
                self.assertEqual(checksum, 0)
                self.assertEqual(make_tzx(program, 'RUN', line)[13:34], tap[:21])
        for line in (-1, 10000, '10', True):
            with self.assertRaises(SpectrumTokenizeError):
                make_tap(program, 'RUN', line)

    def test_tzx_standard_blocks_match_tap(self):
        program = tokenize('10 STOP')
        tap = make_tap(program, 'HI')
        tzx = make_tzx(program, 'HI')
        self.assertEqual(tzx[:10], b'ZXTape!\x1a\x01\x14')
        self.assertEqual(tzx[10:13], b'\x10\xe8\x03')
        self.assertEqual(tzx[13:34], tap[:21])
        self.assertEqual(tzx[34:37], b'\x10\xe8\x03')
        self.assertEqual(tzx[37:], tap[21:])

    def test_known_tap_header_and_checksum(self):
        program = tokenize('10 STOP')
        tape = make_tap(program, 'HI')
        self.assertEqual(
            tape.hex(),
            '130000004849202020202020202006000080060081'
            '0800ff000a0200e20d18')
        offset = 0
        blocks = []
        while offset < len(tape):
            size = struct.unpack_from('<H', tape, offset)[0]
            block = tape[offset + 2:offset + 2 + size]
            checksum = 0
            for byte in block:
                checksum ^= byte
            self.assertEqual(checksum, 0)
            blocks.append(block)
            offset += size + 2
        header, data = blocks
        self.assertEqual(header[:2], b'\x00\x00')
        self.assertEqual(header[2:12], b'HI        ')
        self.assertEqual(struct.unpack_from('<HHH', header, 12), (len(program), 32768, len(program)))
        self.assertEqual(data[0], 255)
        self.assertEqual(data[1:-1], program)

    def test_rejects_invalid_name_and_oversized_program(self):
        for name in ('', 'ELEVENCHARS', '\u00e9', 'BAD\nNAME'):
            with self.subTest(name=name):
                with self.assertRaises(SpectrumTokenizeError):
                    make_tap(tokenize('10 STOP'), name)
        with self.assertRaises(SpectrumTokenizeError):
            make_tap(bytes(MAX_PROGRAM_BYTES + 1), 'BIG')


class ConversionTests(unittest.TestCase):
    def test_autorun_cli_and_remtag_precedence(self):
        result, _, tape = self.convert('##BB:tk_autorun=20\nSTOP\n', '--tk_autorun', '10')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(struct.unpack_from('<H', tape, 16)[0], 20)
        for value in ('-2', '10000', 'oops'):
            result, _, tape = self.convert(f'##BB:tk_autorun={value}\nSTOP\n')
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(tape)

    def test_emulator_remtag_can_disable_launch(self):
        result, _, tape = self.convert(
            '##BB:em_run=False\nSTOP\n', '--em_run', '--em_path', 'missing.exe')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(tape)
        result, _, tape = self.convert('##BB:em_run=maybe\nSTOP\n')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(tape)

    def test_implicit_let_compounds_and_dignified_function(self):
        source = (ROOT / 'examples' / 'zxspectrum' / 'functions.DSP').read_text(encoding='ascii')
        result, listing, tape = self.convert(source, '-rh')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('LET score=score*(1+2)', listing)
        self.assertIn('LET score=score+(1)', listing)
        self.assertIn('THEN LET score=score+(3)', listing)
        self.assertIn('PRINT AT 2,0;"SCORE ";score', listing)
        self.assertIn('LET value=score:GO SUB ', listing)
        self.assertIn('LET answer=result', listing)
        self.assertIn('RETURN', listing)
        self.assertTrue(tape)

    def test_compounds_reject_unsafe_targets_and_preserve_rhs(self):
        for source in ('a(1)++\n', 'score+=\n', 'score++2\n', 'a$++\n', 'a$*=2\n'):
            with self.subTest(source=source):
                result, _, tape = self.convert(source, '-rh')
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertFalse(tape)
        result, listing, tape = self.convert(
            'a$="A":a$+="B"\nvalue=0\nvalue+=TRUE+ABS (-1)\nvalue+=value\n'
            '? value\nSTOP\n', '-rh', '-ss', '-ca')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('LET A$=A$+("B")', listing)
        self.assertIn('LET VALUE=VALUE+(1+ABS(-1))', listing)
        self.assertIn('LET VALUE=VALUE+(VALUE)', listing)
        self.assertIn('PRINT VALUE', listing)
        self.assertTrue(tape)
    def test_colours_loops_and_subroutine_labels(self):
        source = (ROOT / 'examples' / 'zxspectrum' / 'colours.DSP').read_text(encoding='ascii')
        result, listing, tape = self.convert(source, '-rh', '--tk_format', 'both')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('GO SUB 80', listing)
        self.assertIn('FOR i=1 TO 3', listing)
        self.assertIn(b'\xeb', tape)
        self.assertIn(b'\xf3', tape)

    def test_tzx_remtag_overrides_cli_and_preserves_input(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'demo.DSP'
            path.write_text('##BB:tk_format=tzx\nSTOP\n', encoding='ascii')
            result = subprocess.run(
                [sys.executable, '-B', str(ROOT / 'badig.py'), str(path),
                 '-id', 'zxspectrum', '--tk_tokenize', '--tk_format', 'both', '-rh'],
                cwd=ROOT, capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertFalse(path.with_suffix('.tap').exists())
            self.assertEqual(path.with_suffix('.tzx').read_bytes(),
                             make_tzx(tokenize('10 STOP'), 'demo'))
            result, _, _ = self.convert('##BB:tk_format=wav\nSTOP\n')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('TK_FORMAT must be', result.stdout)

    def convert(self, source, *arguments, classic=False, includes=None, tokenized=True):
        with tempfile.TemporaryDirectory(prefix='Spectrum test ') as folder:
            path = Path(folder) / ('demo.ASP' if classic else 'demo.DSP')
            path.write_text(source, encoding='latin1')
            for name, content in (includes or {}).items():
                (Path(folder) / name).write_text(content, encoding='latin1')
            command = [sys.executable, '-B', str(ROOT / 'badig.py'), str(path),
                       '-id', 'zxspectrum']
            if tokenized:
                command.append('--tk_tokenize')
            if classic:
                command.append('-asc')
            result = subprocess.run(command + list(arguments), cwd=ROOT,
                                    capture_output=True, text=True, timeout=15)
            listing_path = path.with_suffix('.ASP')
            listing = listing_path.read_text(encoding='latin1') if listing_path.exists() else ''
            tape_path = path.with_suffix('.tap')
            tape = tape_path.read_bytes() if tape_path.exists() else b''
            return result, listing, tape

    def test_example_labels_and_native_long_names(self):
        source = (ROOT / 'examples' / 'zxspectrum' / 'hello.DSP').read_text(encoding='ascii')
        result, listing, tape = self.convert(source, '-rh', '-ca')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('40 PRINT "SPECTRUM ";COUNTER', listing)
        self.assertIn('60 IF COUNTER<=3 THEN GO TO 40', listing)
        self.assertTrue(tape, result.stdout + result.stderr)

    def test_quotes_macros_declare_and_label_report(self):
        source = ('define [limit] [2]\ndeclare total_score:t\n'
                  'LET total_score=1\n{again}\nPRINT "SAY ""HI"""\n'
                  'LET total_score=total_score+1\n'
                  'IF total_score<[limit] THEN GOTO {again}\nSTOP\n')
        result, listing, tape = self.convert(source, '-rh', '-ss', '-lbr')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('PRINT "SAY ""HI"""', listing)
        self.assertIn('THEN GO TO 20', listing)
        self.assertIn(': REM', listing)
        self.assertNotIn('total_score', listing)
        self.assertTrue(tape, result.stdout + result.stderr)

    def test_classic_input_and_tape_name_remtag(self):
        result, _, tape = self.convert('10 PRINT "HI"\n20 STOP\n', '--tk_name', 'CLASSIC',
                                      classic=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(tape[4:14], b'CLASSIC   ')
        result, _, tape = self.convert('##BB:tk_name=MY TAPE\nSTOP\n', '-rh')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(tape[4:14], b'MY TAPE   ')

    def test_header_booleans_and_report_sentinel(self):
        result, listing, tape = self.convert('LET value=TRUE\nPRINT value\nSTOP\n', '-var')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('REM Converted with Basic Dignified', listing)
        self.assertIn('LET value=1', listing)
        self.assertNotIn('PROGRAM', listing)
        self.assertTrue(tape, result.stdout + result.stderr)

    def test_include_is_numbered_with_the_main_program(self):
        source = 'LET counter=1\nINCLUDE "part.DSP"\nIF counter<2 THEN GOTO {again}\nSTOP\n'
        # Labels belong to their source file, so keep the main jump local.
        source = '{again}\n' + source
        result, listing, tape = self.convert(
            source, '-rh', includes={'part.DSP': 'PRINT counter\nLET counter=counter+1\n'})
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('20 PRINT counter', listing)
        self.assertIn('40 IF counter<2 THEN GO TO 10', listing)
        self.assertTrue(tape, result.stdout + result.stderr)

    def test_listing_only_still_rejects_unsupported_commands(self):
        result, listing, tape = self.convert('CAT\n', tokenized=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(listing)
        self.assertFalse(tape)

    def test_remtag_can_disable_tokenization_and_reject_invalid_boolean(self):
        result, listing, tape = self.convert('##BB:tk_tokenize=False\nSTOP\n', '-rh')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('10 STOP', listing)
        self.assertFalse(tape)
        result, _, tape = self.convert('##BB:tk_tokenize=maybe\nSTOP\n')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('TK_TOKENIZE must be True or False', result.stdout)
        self.assertFalse(tape)

    def test_failed_tokenization_preserves_an_existing_tape(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'bad.ASP'
            path.write_text('10 CAT\n', encoding='ascii')
            tape = path.with_suffix('.tap')
            tape.write_bytes(b'old tape')
            result = subprocess.run(
                [sys.executable, '-B', str(ROOT / 'badig.py'), str(path),
                 '-id', 'zxspectrum', '-asc', '--tk_tokenize'],
                cwd=ROOT, capture_output=True, text=True, timeout=15)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(tape.read_bytes(), b'old tape')

    def test_error_has_no_tape(self):
        for source, arguments in (
            ('CAT\n', ()),
            ('LET name$="X"\n', ()),
            ('PRINT "oops\n', ()),
            ('STOP\n', ('-lp', '0')),
            ('STOP\nSTOP\n', ('-ls', '9999')),
            ('PRINT 1e1000\n', ()),
            ('STOP\n', ('--tk_name', 'TOO LONG NAME')),
            ('STOP\n', ('--tk_name', '')),
        ):
            with self.subTest(source=source, arguments=arguments):
                result, _, tape = self.convert(source, *arguments)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertFalse(tape)

    def test_strings_arrays_data_and_native_functions(self):
        source = (ROOT / 'examples' / 'zxspectrum' / 'data.DSP').read_text(encoding='ascii')
        result, listing, tape = self.convert(source, '-rh', '-ss', '-ca')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('DIM A(3)', listing)
        self.assertIn('READ A(I)', listing)
        self.assertIn('LET N$="SPECTRUM"', listing)
        self.assertIn('LEN N$', listing)
        self.assertIn(b'\xe4', tape)
        self.assertIn(b'\xb1', tape)

    def test_sinclair_variable_categories(self):
        for source in ('FOR counter=1 TO 3\n', 'DIM numbers(3)\n',
                       'LET name$="X"\n', 'LET value%=1\n'):
            with self.subTest(source=source):
                result, _, tape = self.convert(source, '-rh')
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertFalse(tape)
        result, listing, tape = self.convert(
            'DECLARE loop_index:i, values:a, title:n\n'
            'DIM values(3)\nFOR loop_index=1 TO 3\n'
            'LET values(loop_index)=loop_index\nNEXT loop_index\n'
            'LET title$="OK"\nPRINT title$\nSTOP\n', '-rh')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('LET n$="OK"', listing)
        self.assertTrue(tape)


class EmulatorTests(unittest.TestCase):
    def test_launch_uses_private_profile_and_argv_with_spaces(self):
        with tempfile.TemporaryDirectory(prefix='Spectrum emulator ') as folder:
            root = Path(folder)
            original = root / 'original.ini'
            original.write_text('[HARDWARE]\nMachineName=48K Spectrum\n'
                                '[TZXMAN]\nAutoLoad=0\n', encoding='ascii')
            before = original.read_bytes()
            settings = SimpleNamespace(path=root / 'Eighty One.exe', setting=original)
            tape = root / 'my tape.tap'
            tape.write_bytes(make_tap(tokenize('10 STOP'), 'TEST', 0))
            copied = []

            def launch(arguments, **options):
                self.assertEqual(arguments[0], str(settings.path))
                self.assertEqual(arguments[2], str(tape.resolve()))
                self.assertEqual(options, {'cwd': root})
                private = Path(arguments[1])
                self.assertNotEqual(private, original)
                self.assertIn('autoload = 1', private.read_text(encoding='ascii'))
                copied.append(private)
                process = MagicMock()
                process.__enter__.return_value.wait.return_value = 0
                return process

            with patch.object(emulator_interface.subprocess, 'Popen', side_effect=launch):
                emulator_interface.run(SimpleNamespace(verbose_level=0), settings, tape)
            self.assertEqual(original.read_bytes(), before)
            self.assertFalse(copied[0].exists())

    def test_launch_errors_are_not_success(self):
        settings = SimpleNamespace(
            path=Path('missing.exe'),
            setting=ROOT / 'zxspectrum' / 'eightyone48.ini')
        with patch.object(emulator_interface.subprocess, 'Popen', side_effect=OSError('missing')):
            with self.assertRaises(SystemExit) as failure:
                emulator_interface.run(SimpleNamespace(verbose_level=0), settings, Path('demo.tap'))
            self.assertEqual(failure.exception.code, 1)
        with patch.object(emulator_interface.subprocess, 'Popen') as launch:
            process = launch.return_value.__enter__.return_value
            process.wait.return_value = 7
            with self.assertRaises(SystemExit) as failure:
                emulator_interface.run(SimpleNamespace(verbose_level=0), settings, Path('demo.tap'))
            self.assertEqual(failure.exception.code, 1)
        with patch.object(emulator_interface.subprocess, 'Popen') as launch:
            process = launch.return_value.__enter__.return_value
            process.wait.side_effect = [KeyboardInterrupt, 0]
            with self.assertRaises(SystemExit) as failure:
                emulator_interface.run(SimpleNamespace(verbose_level=0), settings, Path('demo.tap'))
            self.assertEqual(failure.exception.code, 1)
            process.terminate.assert_called_once_with()
        with tempfile.TemporaryDirectory() as folder:
            profile = Path(folder) / 'zx81.ini'
            profile.write_text('[HARDWARE]\nMachineName=ZX81\n', encoding='ascii')
            settings.setting = profile
            with patch.object(emulator_interface.subprocess, 'Popen') as launch:
                with self.assertRaises(SystemExit):
                    emulator_interface.run(SimpleNamespace(verbose_level=0), settings, Path('demo.tap'))
                launch.assert_not_called()

    def test_em_run_forces_tape_and_defaults_to_autorun(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'demo.ASP'
            source.write_text('10 STOP\n', encoding='ascii')
            stg = SimpleNamespace(
                file_save=str(source), verbose_level=0, code_remtags={},
                args=SimpleNamespace(tk_name=None, tk_tokenize=None,
                                     tk_format='both', tk_autorun=None))
            tapes = tokenizer_interface.Run(stg).run(force=True)
            self.assertEqual([path.suffix for path in tapes], ['.tap', '.tzx'])
            self.assertEqual(struct.unpack_from('<H', tapes[0].read_bytes(), 16)[0], 0)
            stg.code_remtags['TK_AUTORUN'] = '-1'
            tokenizer_interface.Run(stg).run(force=True)
            self.assertEqual(struct.unpack_from('<H', tapes[0].read_bytes(), 16)[0], 32768)
            stg.code_remtags['TK_TOKENIZE'] = 'False'
            with self.assertRaises(SystemExit):
                tokenizer_interface.Run(stg).run(force=True)


if __name__ == '__main__':
    unittest.main()
