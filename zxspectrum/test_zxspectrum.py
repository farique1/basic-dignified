import configparser
import importlib.util
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from . import emulator_interface, snapshot_zxspectrum, tokenizer_interface
from .tape_zxspectrum import MAX_PROGRAM_BYTES, make_tap, make_tzx
from .tokenizer_zxspectrum import (
    SpectrumTokenizeError, encode_number, encode_text, parse_remx, tokenize,
)
from .dignifier import dignify


ROOT = Path(__file__).resolve().parents[1]


class TokenizerTests(unittest.TestCase):
    def test_raw_bytes_are_literal_in_code_strings_and_rem(self):
        literal = ''.join(f'\\{{{code:02X}}}' for code in range(256))
        expected = bytes(range(256))
        self.assertEqual(tokenize(f'10 {literal}')[4:], expected + b'\r')
        self.assertEqual(tokenize(f'10 PRINT "{literal}"')[4:],
                         b'\xf5 "' + expected + b'"\r')
        self.assertEqual(tokenize(r'10 \{EA} 123:FN "%%A"')[4:],
                         b'\xea 123:FN "%A"\r')
        self.assertEqual(
            tokenize(r'10 DEF FN f(x\{0E}\{00}\{00}\{00}\{00}\{00})=x'),
            tokenize('10 DEF FN f(x)=x'))
        self.assertEqual(tokenize(r'10 \{F5}#2;"OK"')[4:],
                         tokenize('10 PRINT#2;"OK"')[4:])
        self.assertEqual(tokenize(r'10 PRINT FN f\{28}3\{29}'),
                         tokenize('10 PRINT FN f(3)'))
        for text in (r'\{0}', r'\{000}', r'\{GG}', r'\{FF', r'\FF'):
            with self.assertRaises(SpectrumTokenizeError):
                tokenize('10 ' + text)

    def test_native_fn_parameter_slots_and_tape_stream_commands(self):
        self.assertEqual(tokenize('10 DEF FN f(x,a$)=x+LEN a$')[4:],
                         b'\xce f(x\x0e' + bytes(5) + b',a$\x0e' + bytes(5)
                         + b')=x+\xb1 a$\r')
        for statement in (
                'DEF FN z()=42', 'PRINT FN z()', 'PRINT LEN (FN s$("A"))',
                'LOAD ""', 'SAVE "P" LINE 10', 'VERIFY "P" CODE 30000,16',
                'MERGE "P"', 'LOAD "P" CODE', 'LOAD "P" SCREEN$',
                'SAVE "P" DATA a()', 'LOAD "P" DATA a$()',
                'OPEN#4,"S":PRINT #4;"OK":CLOSE#4',
                'INPUT #0;LINE a$', 'LIST #2;10', 'LIST #2,10',
                'LIST #FN s(1,2),10', 'LPRINT "P"', 'LLIST', 'COPY'):
            with self.subTest(statement=statement):
                self.assertTrue(tokenize('10 ' + statement))
        for statement in (
                'DEF FN long(x)=x', 'DEF FN f(long)=long', 'DEF FN f(x)',
                'DEF FN f(x)=', 'PRINT FN f 1', 'PRINT FN f(1',
                'OPEN#4', 'CLOSE#', 'CLOSE#1,2', 'LIST #2,10,20',
                'COPY 1', 'SAVE', 'LOAD',
                'LET x#=1'):
            with self.subTest(statement=statement):
                with self.assertRaises(SpectrumTokenizeError):
                    tokenize('10 ' + statement)

    def test_graphic_and_udg_escapes_emit_real_character_bytes(self):
        graphics = ''.join(f'\\{code:02X}' for code in range(128, 144))
        udgs = ''.join('%' + chr(letter) for letter in range(ord('A'), ord('U') + 1))
        expected = bytes(range(128, 165))
        for literal in (graphics + udgs, ''.join(f'\\{code:02x}' for code in range(128, 165))):
            self.assertEqual(tokenize(f'10 PRINT "{literal}"')[4:],
                             b'\xf5 "' + expected + b'"\r')
            self.assertEqual(tokenize(f'10 REM {literal}')[4:],
                             b'\xea ' + expected + b'\r')
        self.assertEqual(tokenize(r'10 PRINT "%%ABC\\80""%a"')[4:],
                         b'\xf5 "%ABC\\80""\x90"\r')
        self.assertEqual(tokenize(r'10 REM \{00}\{A5}\{FF}')[4:],
                         b'\xea \x00\xa5\xff\r')
        for literal in (r'\7F', r'\A5', r'\8', r'\GG', '%V', '%Z'):
            with self.assertRaises(SpectrumTokenizeError):
                tokenize(f'10 PRINT "{literal}"')
        self.assertEqual(tokenize(r'10 REM \{0D}')[4:], b'\xea \r\r')
        for literal in (r'\{0}', r'\{GG}'):
            with self.assertRaises(SpectrumTokenizeError):
                tokenize(f'10 REM {literal}')

    def test_remx_fill_counts_decoded_bytes_and_rejects_invalid_arguments(self):
        for arguments, payload in (('100,4', '0000'), ('100,3,65', 'AAA'),
                                   (r'100,2,"%A"', r'\90\90'),
                                   (r'100,2,"\8F"', r'\8F\8F'),
                                   ('100,2,0', r'\{00}\{00}'),
                                   ('100,2,13', r'\{0D}\{0D}'),
                                   ('100,2,255', r'\{FF}\{FF}'),
                                   ('100,2,37', '%%%%'),
                                   ('100,2,92', '\\\\' * 2)):
            self.assertEqual(parse_remx(arguments), (100, payload))
        for arguments in ('0,1', '10000,1', '10,0', '10,65533', '10,2,256',
                          '10,1,"AB"', '10,1,""', '10,-1',
                          '10,1,1,2', '10,1:PRINT 1', '9' * 5000 + ',1'):
            with self.assertRaises(SpectrumTokenizeError):
                parse_remx(arguments)
        number, payload = parse_remx('9999,65532,0')
        record = tokenize(f'{number} REM {payload}')
        self.assertEqual(struct.unpack_from('<H', record, 2)[0], 65535)
        number, payload = parse_remx('10,41605')
        make_tap(tokenize(f'{number} REM {payload}'), 'LIMIT')
        number, payload = parse_remx('10,41606')
        with self.assertRaises(SpectrumTokenizeError):
            make_tap(tokenize(f'{number} REM {payload}'), 'LIMIT')

    def test_binary_literals_use_binary_values_in_rom_number_records(self):
        self.assertEqual(
            tokenize('10 PRINT BIN 1010'),
            bytes.fromhex('000a0f00f520c420313031300e00000a00000d'))
        for digits, number in (
                ('0', '0000000000'), ('1', '0000010000'),
                ('1111111111111111', '0000ffff00'),
                ('00000000000000001', '0000010000'),
                ('0' * 64, '0000000000'), ('1 0\t1 0', '00000a0000')):
            with self.subTest(digits=digits):
                expected = b'\xf5 \xc4 ' + digits.replace('\t', ' ').encode('ascii') + b'\x0e'
                self.assertEqual(tokenize('10 PRINT BIN ' + digits)[4:],
                                 expected + bytes.fromhex(number) + b'\x0d')
        self.assertEqual(
            tokenize('10 PRINT "BIN 102:":REM BIN 2')[4:],
            b'\xf5 "BIN 102:":\xea BIN 2\x0d')

    def test_binary_literals_reject_missing_invalid_and_overflowing_digits(self):
        for expression in ('BIN', 'BIN 2', 'BIN 102', 'BIN 1 2', 'BIN 10.1',
                           'BIN 10E2', 'BIN 10x', 'BIN -1', 'BIN "10"',
                           'BIN (10)', 'BIN 10000000000000000'):
            with self.subTest(expression=expression):
                with self.assertRaises(SpectrumTokenizeError):
                    tokenize('10 PRINT ' + expression)

    def test_native_control_and_port_commands(self):
        for command, expected in (
                ('RUN', b'\xf7'), ('LIST', b'\xf0'), ('NEW', b'\xe6'),
                ('CONTINUE', b'\xe8')):
            with self.subTest(command=command):
                self.assertEqual(tokenize('10 ' + command)[4:], expected + b'\x0d')
        self.assertEqual(
            tokenize('10 OUT 254,1')[4:],
            b'\xdf 254\x0e\x00\x00\xfe\x00\x00,1\x0e\x00\x00\x01\x00\x00\x0d')
        for statement in ('RUN start+10', 'LIST ABS (-10)', 'OUT ATTR (0,0),BIN 1',
                          'LIST VAL "10"', 'OUT CODE ",",1'):
            with self.subTest(statement=statement):
                self.assertTrue(tokenize('10 ' + statement))

    def test_native_commands_check_argument_structure_and_statement_context(self):
        for statement in ('NEW 1', 'CONTINUE 1', 'RUN 1,2', 'LIST 1,2',
                          'OUT', 'OUT 254', 'OUT ,1', 'OUT 254,', 'OUT 1,2,3',
                          'OUT (1,2', 'OUT 1),2', 'PRINT RUN', 'LET x=LIST'):
            with self.subTest(statement=statement):
                with self.assertRaises(SpectrumTokenizeError):
                    tokenize('10 ' + statement)

    def test_model_128_enables_spectrum_and_play_tokens(self):
        for statement in ('SPECTRUM', 'PLAY "a"'):
            with self.subTest(statement=statement, model='48'):
                with self.assertRaises(SpectrumTokenizeError) as error:
                    tokenize('10 ' + statement)
                self.assertIn('--sp_model 128', str(error.exception))
        self.assertEqual(tokenize('10 SPECTRUM', model='128')[4:], b'\xa3\x0d')
        self.assertEqual(tokenize('10 PLAY "a","b","c"', model='128')[4:],
                         b'\xa4 "a","b","c"\x0d')
        for statement in ('SPECTRUM 1', 'PLAY', 'PLAY "a","b","c","d"', 'PLAY "a",'):
            with self.subTest(statement=statement):
                with self.assertRaises(SpectrumTokenizeError):
                    tokenize('10 ' + statement, model='128')
        with self.assertRaises(SpectrumTokenizeError):
            tokenize('10 STOP', model='256')

    def test_model_128_udg_t_and_u_become_reserved_tokens(self):
        self.assertEqual(encode_text('%T%U', model='48'), b'\xa3\xa4')
        for literal in ('%T', '%U', r'\A3', r'\a4'):
            with self.assertRaises(SpectrumTokenizeError):
                encode_text(literal, model='128')
        for code in (0xA3, 0xA4):
            raw = f'\\{{{code:02X}}}'
            self.assertEqual(encode_text(raw, model='48'), bytes((code,)))
            self.assertEqual(encode_text(raw, model='128'), bytes((code,)))

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
            '10 FOR counter=1 TO 2', '10 NEXT count', '10 DEF FN long(x)=x',
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
    def test_dignifier_round_trip_preserves_literals_fn_and_rem_data(self):
        classic = (
            '10 DEF FN f(x,a$)=x+LEN a$\n'
            '20 IF FN f(1,"A")=2 THEN GO TO 50:PRINT "NOT UNCONDITIONAL"\n'
            '30 REM  123:\\{00} %%A\n'
            '40 RESTORE 60:SAVE "P" LINE 50\n'
            '50 PRINT "\\{00}%A":GO TO 20\n'
            '60 DATA 1,"GO TO 20":STOP\n')
        converted = dignify(classic, lowercase=False)
        self.assertIn('{line_50}', converted)
        self.assertIn('THEN GO TO {line_50}:PRINT "NOT UNCONDITIONAL"', converted)
        self.assertIn(r'\{EA}  123:\{00} %%A', converted)
        result, listing, tape = self.convert(converted)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(tape[24:-1], tokenize(classic))
        self.assertIn('SAVE "P" LINE 50', listing)
        near_limit = '10 PRINT "' + 'X' * 230 + '":GO TO 20\n20 STOP\n'
        result, _, tape = self.convert(dignify(near_limit, lowercase=False))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(tape[24:-1], tokenize(near_limit))
        for name in ('hello', 'colours', 'data', 'functions', 'native'):
            original = (ROOT / 'examples' / 'zxspectrum' / (name + '.AZS')).read_text()
            result, _, tape = self.convert(dignify(original, lowercase=False))
            self.assertEqual(result.returncode, 0, name + result.stdout + result.stderr)
            self.assertEqual(tape[24:-1], tokenize(original), name)

    def test_dignifier_irregular_numbering_and_unsafe_destinations(self):
        original = '5 PRINT "GO TO 900"\n90 GO TO 6\n900 STOP\n'
        converted = dignify(original)
        self.assertIn('arguments=-rh -ls 1 -lp 1', converted)
        self.assertIn('go to {line_90}', converted)
        result, listing, _ = self.convert(converted)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('2 GO TO 2', listing)
        converted = dignify('5 LIST #FN s(1,2),90\n90 STOP\n900 STOP\n')
        self.assertIn('list #fn s(1,2),{line_90}', converted)
        result, listing, _ = self.convert(converted)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('1 LIST#FN s(1,2),2', listing)
        for source in ('5 GO TO destination\n90 STOP\n900 STOP\n',
                       '10 GO TO 999\n20 STOP\n', '10 STOP\n10 PRINT 1\n'):
            with self.assertRaises(SpectrumTokenizeError):
                dignify(source)
        converted = dignify('10 LET destination=30\n20 GO TO destination\n30 STOP\n')
        self.assertIn('go to destination', converted)
        self.assertIn('arguments=-rh -ls 10 -lp 10', converted)

    def test_dignifier_cli_preserves_destination_on_failure(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'classic.AZS'
            destination = source.with_suffix('.DZS')
            source.write_text('10 GO TO 999\n20 STOP\n')
            destination.write_text('previous source')
            result = subprocess.run(
                [sys.executable, '-B', '-m', 'zxspectrum.dignifier',
                 str(source), str(destination), '-vb', '0'],
                cwd=ROOT, capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 1)
            self.assertIn('destination 999', result.stderr)
            self.assertEqual(destination.read_text(), 'previous source')
            source.write_text('10 PRINT "\u00a3"\n20 STOP\n', encoding='utf-8')
            result = subprocess.run(
                [sys.executable, '-B', '-m', 'zxspectrum.dignifier',
                 str(source), str(destination), '-tr'],
                cwd=ROOT, capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 1)
            self.assertIn('use --force', result.stderr)
            self.assertEqual(destination.read_text(), 'previous source')
            result = subprocess.run(
                [sys.executable, '-B', '-m', 'zxspectrum.dignifier',
                 str(source), str(destination), '-tr', '--force'],
                cwd=ROOT, capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('"\u00a3"', destination.read_text(encoding='utf-8'))
            source.write_text(r'10 PRINT "\{FF}%A"' + '\n20 STOP\n')
            result = subprocess.run(
                [sys.executable, '-B', '-m', 'zxspectrum.dignifier', str(source), '--force'],
                cwd=ROOT, capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('print "\\{FF}%A"', destination.read_text())

    def test_dignifier_sp_model_128_accepts_spectrum_and_play(self):
        source = '10 PLAY "a"\n20 SPECTRUM\n'
        with self.assertRaises(SpectrumTokenizeError):
            dignify(source)
        converted = dignify(source, model='128')
        self.assertIn('play "a"', converted)
        self.assertIn('spectrum', converted)
        with tempfile.TemporaryDirectory() as folder:
            classic = Path(folder) / 'classic.AZS'
            classic.write_text(source, encoding='ascii')
            result = subprocess.run(
                [sys.executable, '-B', '-m', 'zxspectrum.dignifier', str(classic), '-vb', '0'],
                cwd=ROOT, capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 1)
            result = subprocess.run(
                [sys.executable, '-B', '-m', 'zxspectrum.dignifier', str(classic),
                 '--sp_model', '128'],
                cwd=ROOT, capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('play "a"', classic.with_suffix('.DZS').read_text())

    def test_raw_native_fn_and_streams_use_the_dignified_pipeline(self):
        result, listing, tape = self.convert(
            'DEF FN f(x,a$)=x+LEN a$\n'
            'PRINT FN f(3,"AB"):OPEN#4,"S":PRINT#4;"OK":CLOSE#4\n'
            '\\{F5}"RAW"\n\\{EA} 123:FN "%%A"\n'
            'SAVE "P" LINE {start}\n{start}\nSTOP\n', '-rh')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('DEF FN f(x,a$)', listing)
        self.assertIn('SAVE "P" LINE 60', listing)
        self.assertIn(r'\{EA} 123:FN "%%A"', listing)
        self.assertEqual(tape[24:-1], tokenize(listing))

    def test_remx_absolute_lines_preserve_labels_includes_and_reports(self):
        result, listing, tape = self.convert(
            'remx 15,3,"%A"\n{start}\nPRINT "\\80%U"\n'
            'INCLUDE "part.DZS"\nGO TO {start}\nSTOP\n',
            '-rh', '-lnr', '-prr', includes={'part.DZS': 'remx 100,300\n'})
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('10 PRINT "\\80%U"\n15 REM \\90\\90\\90\n20 GO TO 10', listing)
        self.assertIn('100 REM ' + '0' * 300, listing)
        self.assertIn('15 - 1', result.stdout)
        self.assertIn('100 - 1', result.stdout)
        self.assertEqual(tape[24:-1], tokenize(listing))
        result, listing, tape = self.convert('remx 100,4\n', '-rh', '-lnr', '-prr')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(listing, '100 REM 0000\n')
        self.assertIn('100 - 1', result.stdout)
        self.assertTrue(tape)

    def test_remx_collisions_and_removed_directives(self):
        for source, options in (
                ('STOP\nremx 10,2\n', ('-rh',)),
                ('remx 100,2\nremx 100,3\n', ('-rh',)),
                ('remx 10,2\nSTOP\n', ()),
                ('PRINT 1:REMX 100,2\n', ('-rh',)),
                ('remx 100,2:PRINT 1\n', ('-rh',))):
            result, listing, tape = self.convert(source, *options)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertFalse(listing)
            self.assertFalse(tape)
        result, listing, tape = self.convert(
            '###\nremx 100,2\n###\n#off\nremx 200,2\n#off\nSTOP\n', '-rh')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(listing, '10 STOP\n')
        self.assertTrue(tape)

    def test_chained_statements_preserve_if_strings_rem_and_normalization(self):
        for source, expected in (
                ('counter=1:counter+=2:PRINT counter:STOP\n',
                 '10 LET counter=1:LET counter=counter+(2):PRINT counter:STOP'),
                ('IF 1 THEN PRINT "YES":counter=2:PRINT counter\n',
                 '10 IF 1 THEN PRINT "YES":LET counter=2:PRINT counter'),
                ('PRINT "A:B":REM BIN 2:CAT\n',
                 '10 PRINT "A:B":REM  BIN 2:CAT'),
                ('PRINT 1::PRINT 2\n', '10 PRINT 1:PRINT 2')):
            with self.subTest(source=source):
                result, listing, tape = self.convert(source, '-rh')
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(listing.strip(), expected)
                self.assertEqual(tape[24:-1], tokenize(expected))
        for source in ('PRINT 1:CAT\n', 'PRINT 1:counter+=\n', 'PRINT 1:\n'):
            with self.subTest(source=source):
                result, _, tape = self.convert(source, '-rh')
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertFalse(tape)
        for source in ('10 PRINT 1::PRINT 2\n', '10 PRINT 1:\n'):
            result, _, tape = self.convert(source, classic=True)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertFalse(tape)

    def test_native_commands_binary_macros_labels_and_compound_rhs(self):
        result, listing, tape = self.convert(
            'DEFINE [mask] [BIN 1010]\n'
            'value=[mask]:value+=BIN 10:PRINT value\n'
            'LIST {done}:RUN {done}\n'
            '{done}\nOUT 254,BIN 001\nNEW:CONTINUE\n', '-rh')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('LET value=BIN 1010:LET value=value+(BIN 10)', listing)
        self.assertIn('20 LIST 30:RUN 30', listing)
        self.assertIn('30 OUT 254,BIN 001', listing)
        self.assertIn('40 NEW:CONTINUE', listing)
        self.assertEqual(tape[24:-1], tokenize(listing))
        for source in ('OUT 254\n', 'NEW 1\n', 'PRINT BIN 102\n', 'PRINT 1:BIN 1\n'):
            for tokenized in (True, False):
                with self.subTest(source=source, tokenized=tokenized):
                    result, listing, tape = self.convert(source, '-rh', tokenized=tokenized)
                    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                    self.assertFalse(listing)
                    self.assertFalse(tape)
        source = '10 PRINT BIN 1010:OUT 254,1\n20 LIST:RUN 10\n30 NEW:CONTINUE\n'
        result, _, tape = self.convert(source, classic=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(tape[24:-1], tokenize(source))

    def test_shared_errors_exit_nonzero(self):
        cases = (
            ('GO TO {missing}\n', 'Label does not exist'),
            ('PRINT [missing]\n', 'define not defined'),
            ('PRINT `\n', 'Character not recognized'),
            ('INCLUDE "absent.DZS"\n', 'File not found'),
            ('##BB:help=maybe\nSTOP\n', 'Remtag must be true or false'),
        )
        for source, diagnostic in cases:
            for verbosity in ('3', '0'):
                with self.subTest(source=source, verbosity=verbosity):
                    result, listing, tape = self.convert(
                        source, '-rh', '--tk_format', 'both', '-vb', verbosity)
                    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                    self.assertFalse(listing)
                    self.assertFalse(tape)
                    if verbosity == '3':
                        self.assertIn(diagnostic, result.stdout)
                    elif diagnostic == 'Label does not exist':
                        self.assertEqual(result.stdout, '')

    def test_shared_io_errors_exit_nonzero(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'demo.DZS'
            command = [sys.executable, '-B', str(ROOT / 'badig.py'), str(path),
                       '-id', 'zxspectrum', '--tk_tokenize']
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn('File not found', result.stdout)
            path.write_text('STOP\n', encoding='ascii')
            output = Path(folder) / 'absent' / 'demo.AZS'
            result = subprocess.run(
                command + [str(output)], cwd=ROOT, capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn('Save folder not found', result.stdout)
            self.assertFalse(output.exists())
            self.assertFalse(output.with_suffix('.tap').exists())

    def test_shared_ini_errors_use_the_selected_dialect_status(self):
        with tempfile.TemporaryDirectory() as folder:
            config = configparser.ConfigParser()
            config.read(ROOT / 'support' / 'badig.ini')
            config['CONFIGS'].update(use_ini_file='True', system_id='zxspectrum',
                                     line_start='invalid')
            script = (
                'import sys\n'
                'from support.badig_settings import Settings\n'
                'folder=sys.argv[1]\n'
                'arguments=sys.argv[2:]\n'
                'sys.argv=["badig.py", "-id", "zxspectrum"]\n'
                'settings=Settings()\n'
                'settings.LOCAL_PATH=folder\n'
                'try:\n'
                '    settings.init()\n'
                'except SystemExit as error:\n'
                '    assert error.code == 1\n'
                'sys.argv=["badig.py"]+arguments\n'
                'settings=Settings()\n'
                'settings.LOCAL_PATH=folder\n'
                'settings.init()\n')
            for system, arguments, expected in (
                    ('zxspectrum', [], 1), ('msx', ['-id', 'zxspectrum'], 1),
                    ('zxspectrum', ['-id', 'msx'], 0), ('zxspectrum', ['-id', 'coco'], 0)):
                with self.subTest(system=system, arguments=arguments):
                    config['CONFIGS']['system_id'] = system
                    with (Path(folder) / 'badig.ini').open('w', encoding='ascii') as stream:
                        config.write(stream)
                    result = subprocess.run(
                        [sys.executable, '-B', '-c', script, folder] + arguments,
                        cwd=ROOT, capture_output=True, text=True, timeout=15)
                    self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
                    self.assertIn('Problem with: badig.ini', result.stdout)

    def test_help_version_and_remtag_help_still_exit_zero(self):
        for arguments in (['-h'], ['--spectrum-version'], ['-rtg']):
            with self.subTest(arguments=arguments):
                result = subprocess.run(
                    [sys.executable, '-B', str(ROOT / 'badig.py'), '-id', 'zxspectrum'] + arguments,
                    cwd=ROOT, capture_output=True, text=True, timeout=15)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertTrue(result.stdout)
        result, _, tape = self.convert('##BB:help=True\nSTOP\n')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Available remtags', result.stdout)
        self.assertFalse(tape)
        with tempfile.TemporaryDirectory() as folder:
            config = configparser.ConfigParser()
            config.read(ROOT / 'support' / 'badig.ini')
            with (Path(folder) / 'badig.ini').open('w', encoding='ascii') as stream:
                config.write(stream)
            script = (
                'import sys; from support.badig_settings import Settings; '
                'folder=sys.argv[1]; sys.argv=["badig.py", "-id", "zxspectrum", "-ini"]; '
                'settings=Settings(); settings.LOCAL_PATH=folder; settings.init()')
            result = subprocess.run(
                [sys.executable, '-B', '-c', script, folder],
                cwd=ROOT, capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('.ini file written', result.stdout)

    def test_legacy_parser_errors_keep_their_exit_status(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'demo.bad'
            path.write_text('GOTO {missing}\n', encoding='ascii')
            for system in ('msx', 'coco'):
                with self.subTest(system=system):
                    result = subprocess.run(
                        [sys.executable, '-B', str(ROOT / 'badig.py'), str(path),
                         '-id', system, '-rh'],
                        cwd=ROOT, capture_output=True, text=True, timeout=15)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertIn('Label does not exist', result.stdout)

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
        source = (ROOT / 'examples' / 'zxspectrum' / 'functions.DZS').read_text(encoding='ascii')
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
        source = (ROOT / 'examples' / 'zxspectrum' / 'colours.DZS').read_text(encoding='ascii')
        result, listing, tape = self.convert(source, '-rh', '--tk_format', 'both')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('GO SUB 80', listing)
        self.assertIn('FOR i=1 TO 3', listing)
        self.assertIn(b'\xeb', tape)
        self.assertIn(b'\xf3', tape)

    def test_tzx_remtag_overrides_cli_and_preserves_input(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'demo.DZS'
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

    def test_new_defaults_and_legacy_source_listing_compatibility(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'legacy.DSP'
            source.write_text('PRINT "HI"\nSTOP\n', encoding='ascii')
            command = [sys.executable, '-B', str(ROOT / 'badig.py'), str(source)]
            options = ['-id', 'zxspectrum', '-rh', '--tk_tokenize']
            result = subprocess.run(command + options, cwd=ROOT, capture_output=True,
                                    text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual((root / 'legacy.AZS').read_text(encoding='ascii'),
                             '10 PRINT "HI"\n20 STOP\n')
            legacy = root / 'old.ASP'
            result = subprocess.run(command + [str(legacy)] + options, cwd=ROOT,
                                    capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(legacy.read_bytes(), (root / 'legacy.AZS').read_bytes())
            result = subprocess.run(
                [sys.executable, '-B', str(ROOT / 'badig.py'), str(legacy),
                 '-id', 'zxspectrum', '-asc', '--tk_tokenize'],
                cwd=ROOT, capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual((root / 'old.tap').read_bytes(),
                             make_tap(tokenize(legacy.read_text(encoding='ascii')), 'old'))

    def convert(self, source, *arguments, classic=False, includes=None, tokenized=True):
        with tempfile.TemporaryDirectory(prefix='Spectrum test ') as folder:
            path = Path(folder) / ('demo.AZS' if classic else 'demo.DZS')
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
            listing_path = path.with_suffix('.AZS')
            listing = listing_path.read_text(encoding='latin1') if listing_path.exists() else ''
            tape_path = path.with_suffix('.tap')
            tape = tape_path.read_bytes() if tape_path.exists() else b''
            return result, listing, tape

    def test_example_labels_and_native_long_names(self):
        source = (ROOT / 'examples' / 'zxspectrum' / 'hello.DZS').read_text(encoding='ascii')
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

    def test_sp_model_cli_and_remtag_enable_128k_tokens(self):
        source = 'SPECTRUM\nPLAY "a"\nSTOP\n'
        result, _, tape = self.convert(source, '-rh')
        self.assertEqual(result.returncode, 1)
        self.assertIn('--sp_model 128', result.stdout)
        result, listing, tape = self.convert(source, '-rh', '--sp_model', '128')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('SPECTRUM', listing)
        self.assertIn('PLAY "a"', listing)
        self.assertTrue(tape, result.stdout + result.stderr)
        result, _, tape = self.convert('##BB:sp_model=128\n' + source, '-rh')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(tape, result.stdout + result.stderr)
        result, _, _ = self.convert(source, '-rh', '--sp_model', '256')
        self.assertNotEqual(result.returncode, 0)

    def test_sp_model_128_rejects_z80_sna_output(self):
        result, _, _ = self.convert('STOP\n', '-rh', '--sp_model', '128',
                                    '--tk_format', 'z80')
        self.assertEqual(result.returncode, 1)
        self.assertIn('only supported for --sp_model 48', result.stdout)

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
        source = 'LET counter=1\nINCLUDE "part.DZS"\nIF counter<2 THEN GOTO {again}\nSTOP\n'
        # Labels belong to their source file, so keep the main jump local.
        source = '{again}\n' + source
        result, listing, tape = self.convert(
            source, '-rh', includes={'part.DZS': 'PRINT counter\nLET counter=counter+1\n'})
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
            path = Path(folder) / 'bad.AZS'
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
        source = (ROOT / 'examples' / 'zxspectrum' / 'data.DZS').read_text(encoding='ascii')
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


class SnapshotTests(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec('skoolkit'), 'optional SkoolKit not installed')
    def test_native_fn_raw_strings_and_streams_execute_in_the_rom(self):
        import skoolkit.snapshot as snapshots

        if not hasattr(snapshots, 'Snapshot'):
            self.skipTest('ROM execution probe requires the newer SkoolKit snapshot API')
        from skoolkit.simulator import Simulator
        from skoolkit.simutils import from_snapshot

        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'fn.DZS'
            source.write_text(
                'CLS\nDEF FN f(x,a$)=x+LEN a$\nDEF FN s$(a$)=a$+"!"\n'
                'DEF FN z()=42\nDEF FN g(x)=FN f(x,"AB")*2\n'
                'x=99\nOPEN #4,"S":PRINT #4;"OK"\n'
                'LIST #4,9999:LIST #4;9999:CLOSE #4\n'
                'POKE 30000,FN f(3,"AB"):POKE 30001,x\n'
                'POKE 30002,LEN (FN s$("Z")):POKE 30003,FN z()\n'
                'POKE 30004,FN g(3)\na$="\\{00}\\{FF}"\n'
                'POKE 30005,CODE a$(1):POKE 30006,CODE a$(2)\n'
                '\\{F5}"RAW"\nPOKE 30007,123\nSTOP\n', encoding='ascii')
            result = subprocess.run(
                [sys.executable, '-B', str(ROOT / 'badig.py'), str(source),
                 '-id', 'zxspectrum', '-rh', '--tk_tokenize', '--tk_format', 'all',
                 '--tk_autorun', '0'],
                cwd=ROOT, capture_output=True, text=True, timeout=150)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for extension in ('.z80', '.sna'):
                snapshot = snapshots.Snapshot.get(str(source.with_suffix(extension)))
                registers = {'SP': snapshot.sp + 2} if extension == '.sna' else None
                simulator = from_snapshot(Simulator, snapshot, registers=registers)
                for _ in range(200000):
                    simulator.run()
                    if simulator.memory[30007] == 123:
                        break
                self.assertEqual(simulator.memory[30000:30008],
                                 [5, 99, 2, 42, 10, 0, 255, 123], extension)

    @unittest.skipUnless(importlib.util.find_spec('skoolkit'), 'optional SkoolKit not installed')
    def test_graphics_udg_bitmap_and_raw_remx_execute_in_the_rom(self):
        import skoolkit.snapshot as snapshots

        if not hasattr(snapshots, 'Snapshot'):
            self.skipTest('ROM graphics probe requires the newer SkoolKit snapshot API')
        from skoolkit.simulator import Simulator
        from skoolkit.simutils import from_snapshot

        rows = [60, 66, 165, 129, 165, 153, 66, 60]
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'graphics.DZS'
            source.write_text(
                'remx 5,4,13\nCLS\nFOR i=0 TO 7\nREAD pixel\n'
                'POKE USR "A"+i,pixel\nNEXT i\n'
                'DATA 60,66,165,129,165,153,66,60\n'
                'PRINT "\\8F%A"\nPOKE 30000,123\nSTOP\n', encoding='ascii')
            result = subprocess.run(
                [sys.executable, '-B', str(ROOT / 'badig.py'), str(source),
                 '-id', 'zxspectrum', '-rh', '--tk_tokenize', '--tk_format', 'all',
                 '--tk_autorun', '0'],
                cwd=ROOT, capture_output=True, text=True, timeout=150)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for extension in ('.z80', '.sna'):
                snapshot = snapshots.Snapshot.get(str(source.with_suffix(extension)))
                registers = {'SP': snapshot.sp + 2} if extension == '.sna' else None
                simulator = from_snapshot(Simulator, snapshot, registers=registers)
                for _ in range(100000):
                    simulator.run()
                    if simulator.memory[30000] == 123:
                        break
                self.assertEqual(simulator.memory[30000], 123, extension)
                address = simulator.memory[23675] + 256 * simulator.memory[23676]
                self.assertEqual(simulator.memory[address:address + 8], rows)
                for row, value in enumerate(rows):
                    self.assertEqual(simulator.memory[16384 + 256 * row], 255)
                    self.assertEqual(simulator.memory[16385 + 256 * row], value)

    def test_sna_saves_pc_on_stack_without_mutating_ram(self):
        header = bytearray(86)
        header[30] = 54
        header[0:2] = b'\x12\x34'
        header[10:13] = b'\x3f\x05\x0f'
        header[27:30] = b'\x01\x01\x01'
        struct.pack_into('<H', header, 8, 65500)
        struct.pack_into('<H', header, 32, snapshot_zxspectrum.LOAD_RETURN)
        state = snapshot_zxspectrum.read_registers(header)
        ram = bytes(49152)
        sna = snapshot_zxspectrum.make_sna(state, ram)
        self.assertEqual(len(sna), 49179)
        self.assertEqual(sna[19:23], b'\x04\x85\x34\x12')
        self.assertEqual(sna[25:27], b'\x01\x07')
        stack = struct.unpack_from('<H', sna, 23)[0]
        self.assertEqual(stack + 2, state.sp)
        offset = 27 + stack - 16384
        self.assertEqual(int.from_bytes(sna[offset:offset + 2], 'little'), state.pc)
        restored = bytearray(sna[27:])
        restored[stack - 16384:stack - 16382] = b'\0\0'
        self.assertEqual(restored, ram)
        self.assertEqual(ram, bytes(49152))
        for invalid in (b'', bytes(86), header[:40]):
            with self.assertRaises(ValueError):
                snapshot_zxspectrum.read_registers(invalid)
        for sp, iff2, memory in ((16385, 1, ram), (65500, 0, ram),
                                  (65500, 1, ram[:-1])):
            state.sp, state.iff2 = sp, iff2
            with self.assertRaises(ValueError):
                snapshot_zxspectrum.make_sna(state, memory)

    def test_snapshot_failure_preserves_all_existing_outputs(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'demo.AZS'
            source.write_text('10 STOP\n', encoding='ascii')
            stg = SimpleNamespace(
                file_save=str(source), verbose_level=0, code_remtags={},
                c_stg=SimpleNamespace(sp_model='48'),
                args=SimpleNamespace(tk_name=None, tk_tokenize=True,
                                     tk_format='all', tk_autorun=None))
            destinations = [source.with_suffix('.' + ext)
                            for ext in ('tap', 'tzx', 'z80', 'sna')]
            for path in destinations:
                path.write_bytes(b'previous output')
            failures = (
                subprocess.CompletedProcess([], 1, '', 'optional engine unavailable'),
                subprocess.TimeoutExpired('snapshot engine', 120))
            for failure in failures:
                with patch.object(tokenizer_interface.subprocess, 'run',
                                  side_effect=[failure]):
                    with self.assertRaises(SystemExit) as error:
                        tokenizer_interface.Run(stg).run()
                    self.assertEqual(error.exception.code, 1)
                self.assertTrue(all(path.read_bytes() == b'previous output'
                                    for path in destinations))
                self.assertEqual(len(list(Path(folder).iterdir())), 5)

    @unittest.skipUnless(importlib.util.find_spec('skoolkit'), 'optional SkoolKit not installed')
    def test_engine_loads_program_and_preserves_autorun_in_both_snapshots(self):
        from skoolkit.snapshot import get_snapshot

        listing = '10 LET marker=42\n20 STOP\n'
        program = tokenize(listing)
        with tempfile.TemporaryDirectory(prefix='Spectrum snapshots ') as folder:
            source = Path(folder) / 'demo.AZS'
            source.write_text(listing, encoding='ascii')
            for autorun in (-1, 0, 9999):
                command = [sys.executable, '-B', str(ROOT / 'badig.py'), str(source),
                           '-id', 'zxspectrum', '-asc', '--tk_tokenize',
                           '--tk_format', 'all', '--tk_autorun', str(autorun)]
                result = subprocess.run(command, cwd=ROOT, capture_output=True,
                                        text=True, timeout=150)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                z80 = source.with_suffix('.z80')
                sna = source.with_suffix('.sna')
                memory = bytes(get_snapshot(str(z80)))
                restored = bytes(get_snapshot(str(sna)))
                state = snapshot_zxspectrum.read_registers(z80.read_bytes())
                self.assertEqual(state.pc, snapshot_zxspectrum.LOAD_RETURN)
                self.assertEqual(memory[23755:23755 + len(program)], program)
                self.assertEqual(int.from_bytes(memory[23627:23629], 'little'),
                                 23755 + len(program))
                self.assertEqual(memory[23755 + len(program)], 128)
                self.assertEqual(int.from_bytes(memory[23618:23620], 'little'),
                                 max(autorun, 0))
                self.assertEqual(memory[23620], 255 if autorun == -1 else 0)
                saved_sp = struct.unpack_from('<H', sna.read_bytes(), 23)[0]
                self.assertEqual(saved_sp + 2, state.sp)
                self.assertEqual(int.from_bytes(restored[saved_sp:saved_sp + 2], 'little'),
                                 state.pc)
                self.assertEqual(restored[:saved_sp], memory[:saved_sp])
                self.assertEqual(restored[saved_sp + 2:], memory[saved_sp + 2:])
                self.assertEqual(source.with_suffix('.tap').read_bytes(),
                                 make_tap(program, 'demo', None if autorun == -1 else autorun))
                self.assertEqual(source.with_suffix('.tzx').read_bytes(),
                                 make_tzx(program, 'demo', None if autorun == -1 else autorun))

    @unittest.skipUnless(importlib.util.find_spec('skoolkit'), 'optional SkoolKit not installed')
    def test_single_snapshot_formats_and_remtag_precedence(self):
        for selected, remtag in (('z80', None), ('sna', None), ('z80', 'sna')):
            with self.subTest(selected=selected, remtag=remtag), \
                    tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                source = root / ('demo.DZS' if remtag else 'demo.AZS')
                source.write_text('##BB:tk_format=sna\nSTOP\n' if remtag else '10 STOP\n',
                                  encoding='ascii')
                arguments = ['-rh'] if remtag else ['-asc']
                result = subprocess.run(
                    [sys.executable, '-B', str(ROOT / 'badig.py'), str(source),
                     '-id', 'zxspectrum', '--tk_tokenize', '--tk_format', selected] + arguments,
                    cwd=ROOT, capture_output=True, text=True, timeout=150)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                expected = {'demo.AZS', 'demo.' + (remtag or selected)}
                if remtag:
                    expected.add('demo.DZS')
                self.assertEqual({path.name for path in root.iterdir()}, expected)

    @unittest.skipUnless(importlib.util.find_spec('skoolkit'), 'optional SkoolKit not installed')
    def test_both_snapshots_resume_basic_in_the_rom(self):
        import skoolkit.snapshot as snapshots

        if not hasattr(snapshots, 'Snapshot'):
            self.skipTest('ROM continuation probe requires the newer SkoolKit snapshot API')
        from skoolkit.simulator import Simulator
        from skoolkit.simutils import from_snapshot

        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'resume.AZS'
            source.write_text('10 POKE 30000,123\n20 STOP\n', encoding='ascii')
            for autorun in (-1, 0):
                result = subprocess.run(
                    [sys.executable, '-B', str(ROOT / 'badig.py'), str(source),
                     '-id', 'zxspectrum', '-asc', '--tk_tokenize', '--tk_format', 'all',
                     '--tk_autorun', str(autorun)],
                    cwd=ROOT, capture_output=True, text=True, timeout=150)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                for extension in ('.z80', '.sna'):
                    snapshot = snapshots.Snapshot.get(str(source.with_suffix(extension)))
                    # The SNA loader consumes the stacked PC with RETN.
                    registers = {'SP': snapshot.sp + 2} if extension == '.sna' else None
                    simulator = from_snapshot(Simulator, snapshot, registers=registers)
                    self.assertNotEqual(simulator.memory[30000], 123)
                    for _ in range(50000):
                        simulator.run()
                        if simulator.memory[30000] == 123:
                            break
                    self.assertEqual(simulator.memory[30000] == 123, autorun == 0,
                                     extension)

    @unittest.skipUnless(importlib.util.find_spec('skoolkit'), 'optional SkoolKit not installed')
    def test_engine_success_status_without_loaded_state_is_rejected(self):
        header = bytearray(86)
        header[30] = 54
        struct.pack_into('<H', header, 8, 65500)
        struct.pack_into('<H', header, 32, snapshot_zxspectrum.LOAD_RETURN)
        with patch('skoolkit.tap2sna.main'), \
                patch('skoolkit.snapshot.get_snapshot', return_value=[0] * 65536), \
                patch.object(Path, 'read_bytes', side_effect=[bytes(header), b'']), \
                patch.object(Path, 'write_bytes') as write:
            self.assertEqual(snapshot_zxspectrum.build(), 1)
            write.assert_not_called()


class EmulatorTests(unittest.TestCase):
    def test_settings_select_profile_and_machine_name_per_model(self):
        for model, profile_name, machine in (
                ('48', 'eightyone48.ini', '48K Spectrum'),
                ('128', 'eightyone128.ini', 'Spectrum 128')):
            with self.subTest(model=model):
                stg = SimpleNamespace(
                    args=SimpleNamespace(em_run=None, em_path=None, em_setting=None),
                    code_remtags={}, c_stg=SimpleNamespace(sp_model=model))
                settings = emulator_interface.Settings(stg)
                self.assertEqual(settings.model, model)
                self.assertEqual(settings.setting.name, profile_name)
                profile = configparser.ConfigParser()
                profile.read(settings.setting)
                self.assertEqual(profile.get('HARDWARE', 'MachineName'), machine)

    def test_run_rejects_profile_for_the_wrong_model(self):
        with tempfile.TemporaryDirectory() as folder:
            profile = Path(folder) / 'wrong.ini'
            profile.write_text('[HARDWARE]\nMachineName=48K Spectrum\n', encoding='ascii')
            settings = SimpleNamespace(path=Path('missing.exe'), model='128', setting=profile)
            with patch.object(emulator_interface.subprocess, 'Popen') as launch:
                with self.assertRaises(SystemExit) as failure:
                    emulator_interface.run(SimpleNamespace(verbose_level=0), settings,
                                           Path('demo.tap'))
                self.assertEqual(failure.exception.code, 1)
                launch.assert_not_called()

    def test_snapshot_profile_disables_tape_autoload(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            settings = SimpleNamespace(
                path=root / 'EightyOne.exe', model='48',
                setting=ROOT / 'zxspectrum' / 'eightyone48.ini')

            def launch(arguments, **options):
                profile = configparser.ConfigParser()
                self.assertEqual(options, {'cwd': root})
                profile.read(arguments[1])
                for key in ('FlashLoad', 'AutoStart', 'AutoLoad'):
                    self.assertFalse(profile.getboolean('TZXMAN', key))
                process = MagicMock()
                process.__enter__.return_value.wait.return_value = 0
                return process

            with patch.object(emulator_interface.subprocess, 'Popen', side_effect=launch):
                for extension in ('.z80', '.sna'):
                    emulator_interface.run(SimpleNamespace(verbose_level=0), settings,
                                           root / ('demo' + extension))

    def test_launch_uses_private_profile_and_argv_with_spaces(self):
        with tempfile.TemporaryDirectory(prefix='Spectrum emulator ') as folder:
            root = Path(folder)
            original = root / 'original.ini'
            original.write_text('[HARDWARE]\nMachineName=48K Spectrum\n'
                                '[TZXMAN]\nAutoLoad=0\n', encoding='ascii')
            before = original.read_bytes()
            settings = SimpleNamespace(path=root / 'Eighty One.exe', model='48', setting=original)
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
            path=Path('missing.exe'), model='48',
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
            source = Path(folder) / 'demo.AZS'
            source.write_text('10 STOP\n', encoding='ascii')
            stg = SimpleNamespace(
                file_save=str(source), verbose_level=0, code_remtags={},
                c_stg=SimpleNamespace(sp_model='48'),
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
