import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from .tokenizer_zx81 import ZX81TokenizeError
from .tokenizer_zx81 import tokenize_lines


class TokenizerTests(unittest.TestCase):
    def test_numbered_basic_line_has_expected_zx81_tokens(self):
        program = tokenize_lines(['10 PRINT 1'])

        self.assertEqual(
            program[116:129],
            b'\x00\x0a\x09\x00\xf5\x1d\x7e\x81\x00\x00\x00\x00\x76',
        )

    def test_inverse_video_and_graphics_escape(self):
        program = tokenize_lines(['10 PRINT "%A \\:\'"'])

        self.assertIn(b'\xa6', program)
        self.assertIn(b'\x07', program)

    def test_rem_absorbs_keyword_separator(self):
        program = tokenize_lines(['10 REM raw text'])

        self.assertIn(b'\xea\x37\x26\x3c', program)

    def test_literal_hex_escapes_have_exact_line_bytes(self):
        cases = [
            (r'600 REM \{D8}\{D8}\{D8}END OF GAME\{D8}\{D8}\{D8}',
             'EA D8 D8 D8 2A 33 29 00 34 2B 00 2C 26 32 2A D8 D8 D8 76'),
            (r'1 REM \{C9}\{00}', 'EA C9 00 76'),
            (r'10 PRINT "\{F5}"', 'F5 0B F5 0B 76'),
            (r'20 LET \{35}OKE=6000',
             'F1 35 34 30 2A 14 22 1C 1C 1C 7E 8D 3B 80 00 00 76'),
            (r'30 LET A=0\{7E}\{81}\{00}\{00}\{00}\{00}',
             'F1 26 14 1C 7E 81 00 00 00 00 76'),
            (r'30 LET A=1e999\{7e}\{81}\{00}\{00}\{00}\{00}',
             'F1 26 14 1D 2A 25 25 25 7E 81 00 00 00 00 76'),
            (r'10 PRINT "\{0b}1":\{ea}PRINT 2',
             'F5 0B 0B 1D 0B 0E EA F5 1E 7E 82 00 00 00 00 76'),
            (r'10 PRINT \{35}123',
             'F5 35 1D 1E 1F 7E 87 76 00 00 00 76'),
            (r'10 LET A=0 \{7e}\{81}\{00}\{00}\{00}\{00}',
             'F1 26 14 1C 7E 00 00 00 00 00 7E 81 00 00 00 00 76'),
        ]
        for source, expected in cases:
            with self.subTest(source=source):
                program = tokenize_lines([source])
                length = int.from_bytes(program[118:120], 'little')
                self.assertEqual(program[120:120 + length], bytes.fromhex(expected))

    def test_hidden_numbers_round_and_respect_the_exponent_range(self):
        from .tokenizer_zx81 import _number_bytes

        cases = {
            '0': '00 00 00 00 00',
            '1': '81 00 00 00 00',
            '0.5': '80 00 00 00 00',
            '10': '84 20 00 00 00',
            '16514': '8F 01 04 00 00',
            '1.9999999999': '82 00 00 00 00',
            '3.14159265': '82 49 0F DA 9E',
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(bytes(_number_bytes(text, 10)[-5:]), bytes.fromhex(expected))
        for text in ('1.8E38', '1E-39'):
            with self.subTest(text=text):
                with self.assertRaisesRegex(ZX81TokenizeError, 'out of range'):
                    _number_bytes(text, 10)

    def test_all_hex_byte_values_are_literal_in_rem(self):
        source = '10 REM ' + ''.join(f'\\{{{value:02x}}}' for value in range(256))
        program = tokenize_lines([source])
        length = int.from_bytes(program[118:120], 'little')
        self.assertEqual(program[120:120 + length], b'\xea' + bytes(range(256)) + b'\x76')

    def test_rejects_malformed_hex_escapes_in_every_context(self):
        for escape in (r'\{D}', r'\{GG}', r'\{D8', r'\{}', r'\{D80}'):
            for body in ('REM ' + escape, 'PRINT "' + escape + '"', 'LET A=' + escape):
                with self.subTest(body=body):
                    with self.assertRaisesRegex(ZX81TokenizeError, r'Line 40:'):
                        tokenize_lines(['40 ' + body])

    def test_hex_escapes_survive_dignified_conversion(self):
        repository_root = Path(__file__).resolve().parents[1]
        source_text = (
            r'REM \{D8}\{00}' + '\n'
            + r'PRINT "\{F5}\{0B}"' + '\n'
            + r'LET A=0\{7E}\{81}\{00}\{00}\{00}\{00}' + '\n'
            + r'\{EA}PRINT 2' + '\n'
        )
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'hex_escapes.dzx'
            source.write_text(source_text, encoding='latin1')
            result = subprocess.run(
                [sys.executable, str(repository_root / 'badig.py'),
                 str(source), '-id', 'zx81', '-rh'],
                capture_output=True, text=True, cwd=repository_root,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(source.with_suffix('.p').is_file(), result.stdout + result.stderr)
            program = source.with_suffix('.p').read_bytes()
            offset = 116
            for expected in ('EA D8 00 76', 'F5 0B F5 0B 0B 76',
                             'F1 26 14 1C 7E 81 00 00 00 00 76',
                             'EA F5 1E 7E 82 00 00 00 00 76'):
                length = int.from_bytes(program[offset + 2:offset + 4], 'little')
                self.assertEqual(program[offset + 4:offset + 4 + length],
                                 bytes.fromhex(expected))
                offset += 4 + length

    def test_program_pointers_follow_program_and_display_file(self):
        program = tokenize_lines(['10 PRINT 1'])
        data_file = int.from_bytes(program[3:5], 'little')
        variables = int.from_bytes(program[7:9], 'little')

        self.assertEqual(data_file, 0x407D + 13)
        self.assertEqual(variables, data_file + 793)
        self.assertEqual(program[-2:], b'\x80\x76')

    def run_badig(self, source_text, *arguments, filename='numbered.dzx'):
        repository_root = Path(__file__).resolve().parents[1]
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        source = Path(folder.name) / filename
        source.write_text(source_text, encoding='latin1')
        result = subprocess.run(
            [sys.executable, str(repository_root / 'badig.py'), str(source),
             '-id', 'zx81', *arguments],
            capture_output=True, text=True, cwd=repository_root,
        )
        return source, result

    def test_numbered_dzx_is_renumbered_into_azx(self):
        source_text = (
            '10 REM \\{D8}CAVE\n'
            '20 FOR G=20 TO 1 STEP -1\n'
            '30 IF G=5 THEN GOTO 55\n'
            '40 NEXT G\n'
            '50 GOSUB 100\n'
            '60 PAUSE 4E4\n'
            '100 LET SCORE=0\n'
            '110 RUN 10\n'
        )
        source, result = self.run_badig(source_text, '-rh', '-ls', '100', '-lp', '5')

        self.assertNotIn('***', result.stdout, result.stdout + result.stderr)
        self.assertEqual(source.read_text(encoding='latin1'), source_text)
        self.assertEqual(source.with_suffix('.AZX').read_text(encoding='latin1').splitlines(), [
            '100 REM \\{D8}CAVE',
            '105 FOR G=20 TO 1 STEP -1',
            '110 IF G=5 THEN GOTO 125',
            '115 NEXT G',
            '120 GOSUB 130',
            '125 PAUSE 4E4',
            '130 LET z=0',
            '135 RUN 100',
        ])
        program = source.with_suffix('.p').read_bytes()
        length = int.from_bytes(program[118:120], 'little')
        self.assertEqual(program[120:120 + length], bytes.fromhex('EA D8 28 26 3B 2A 76'))

    def test_numbered_dzx_accepts_remtags_and_comments(self):
        source_text = ('##BB:arguments=-ls 200 -lp 2 -rh\n'
                       '# typed from a book\n'
                       '10 PRINT 1\n'
                       '20 GOTO 10\n')
        source, result = self.run_badig(source_text, '--tk_ascii_only')

        self.assertNotIn('***', result.stdout, result.stdout + result.stderr)
        self.assertEqual(source.with_suffix('.AZX').read_text(encoding='latin1').splitlines(),
                         ['200 PRINT 1', '202 GOTO 200'])

    def test_reports_map_real_source_lines_and_variables(self):
        source_text = ('# from a book\n'
                       '10 LET SCORE=0\n'
                       '\n'
                       '20 LET SCORE=SCORE+1\n'
                       '30 IF SCORE<5 THEN GOTO 20\n')
        source, result = self.run_badig(source_text, '-rh', '--tk_ascii_only', '-lnr', '-var')

        self.assertNotIn('***', result.stdout, result.stdout + result.stderr)
        folder = source.parent
        self.assertEqual((folder / 'numbered_lines.txt').read_text(encoding='latin1').splitlines()[3:],
                         ['10 - 2', '20 - 4', '30 - 5'])
        self.assertEqual((folder / 'numbered_variables.txt').read_text(encoding='latin1').splitlines(),
                         ['1 variables assigned', '', 'z:score'])

    def test_all_26_letters_are_available_for_long_names(self):
        source_text = ''.join(f'var{chr(97 + i)} = {i}\n' for i in range(26))
        source, result = self.run_badig(source_text, '-rh', '--tk_ascii_only')

        self.assertNotIn('***', result.stdout, result.stdout + result.stderr)
        self.assertEqual(len(source.with_suffix('.AZX').read_text(encoding='latin1').splitlines()), 26)

    @staticmethod
    def line_body(program, number):
        offset = 116
        end = int.from_bytes(program[3:5], 'little') - 0x4009
        while offset < end:
            length = int.from_bytes(program[offset + 2:offset + 4], 'little')
            if int.from_bytes(program[offset:offset + 2], 'big') == number:
                return program[offset + 4:offset + 4 + length]
            offset += 4 + length
        return None

    def test_remx_generates_machine_code_rem_lines(self):
        source_text = 'remx 0,4,118\nremx 9000,3,"A"\nremx 1,10\nprint usr 16514\n'
        source, result = self.run_badig(source_text, '-rh', filename='remx.dzx')

        self.assertNotIn('***', result.stdout, result.stdout + result.stderr)
        self.assertEqual(source.with_suffix('.AZX').read_text(encoding='latin1').splitlines(), [
            '0 REM \\{76}\\{76}\\{76}\\{76}',
            '1 REM 0000000000',
            '10 print usr 16514',
            '9000 REM AAA',
        ])
        program = source.with_suffix('.p').read_bytes()
        self.assertEqual(self.line_body(program, 0), bytes.fromhex('EA 76 76 76 76 76'))
        self.assertEqual(self.line_body(program, 1), b'\xea' + b'\x1c' * 10 + b'\x76')
        self.assertEqual(self.line_body(program, 9000), bytes.fromhex('EA 26 26 26 76'))

    def test_remx_in_numbered_and_classic_listings(self):
        source, result = self.run_badig('remx 1,5,255\n10 PRINT 1\n20 GOTO 10\n', '-rh', '-ls', '100')
        self.assertNotIn('***', result.stdout, result.stdout + result.stderr)
        self.assertEqual(source.with_suffix('.AZX').read_text(encoding='latin1').splitlines(),
                         ['1 REM \\{FF}\\{FF}\\{FF}\\{FF}\\{FF}', '100 PRINT 1', '110 GOTO 100'])

        source, result = self.run_badig('remx 1,6\n10 PRINT 1\n', '-asc', filename='classic.AZX')
        self.assertNotIn('***', result.stdout, result.stdout + result.stderr)
        program = source.with_suffix('.p').read_bytes()
        self.assertEqual(self.line_body(program, 1), b'\xea' + b'\x1c' * 6 + b'\x76')

    def test_remx_rejects_invalid_arguments(self):
        for source_text, message in (('remx 1\n', 'remx expects'),
                                     ('remx 1,0\n', 'count must be 1..49152'),
                                     ('remx 1,49153\n', 'count must be 1..49152'),
                                     ('remx 1,5,256\n', 'byte must be 0..255'),
                                     ('remx 10000,5\n', 'line number must be 0..9999'),
                                     ('remx 10,5\nprint 1\n', 'already used'),
                                     ('remx 1,49152\nprint 1\n', 'cannot exceed')):
            with self.subTest(source_text=source_text):
                source, result = self.run_badig(source_text, '-rh')
                self.assertIn(message, result.stdout)
                self.assertFalse(source.with_suffix('.p').exists())

    def test_numbered_dzx_rejects_unrenumberable_jumps(self):
        for line, message in (('20 GOTO 10*X', 'computed jump'),
                              ('20 GOTO 900', 'after the last line')):
            with self.subTest(line=line):
                source, result = self.run_badig(f'10 PRINT 1\n{line}\n', '-rh')
                self.assertIn(message, result.stdout)
                self.assertFalse(source.with_suffix('.p').exists())

    def test_numbered_azx_without_asc_is_not_overwritten(self):
        source_text = '10 PRINT 1\n20 GOTO 10\n'
        source, result = self.run_badig(source_text, '--tk_del_ascii', filename='listing.AZX')

        self.assertNotIn('***', result.stdout, result.stdout + result.stderr)
        self.assertEqual(source.read_text(encoding='latin1'), source_text)
        self.assertTrue(source.with_suffix('.p').is_file())

    def test_numbered_detection_is_limited_to_zx81(self):
        repository_root = Path(__file__).resolve().parents[1]

        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'numbered.dmx'
            source.write_text('10 PRINT 1\n', encoding='latin1')
            result = subprocess.run(
                [sys.executable, str(repository_root / 'badig.py'), str(source), '-id', 'msx'],
                capture_output=True, text=True, cwd=repository_root,
            )

            self.assertIn('Line starting with number', result.stdout)

    def test_compound_operators_use_their_zx81_tokens(self):
        program = tokenize_lines(['10 1<>2 1<=2 1>=2 2**3'])

        self.assertIn(bytes((221,)), program)
        self.assertIn(bytes((219,)), program)
        self.assertIn(bytes((220,)), program)
        self.assertIn(bytes((216,)), program)

    def test_for_to_is_a_reserved_keyword(self):
        from support.badig_dignified import Description as DignifiedDescription
        from .badig_zx81 import Description

        class CombinedDescription(DignifiedDescription, Description):
            pass

        description = CombinedDescription()

        self.assertIn('TO', description.c_reserved_kw)

    def test_builtin_print_at_define_expands_and_tokenizes(self):
        repository_root = Path(__file__).resolve().parents[1]
        source_text = '[?](10,5) "ZX-81"\n[?](12) "ROW ONLY"\n[?] "DEFAULT"\n'

        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'print_at.dzx'
            source.write_text(source_text, encoding='latin1')
            result = subprocess.run(
                [sys.executable, str(repository_root / 'badig.py'),
                 str(source), '-id', 'zx81'],
                capture_output=True,
                text=True,
                cwd=repository_root,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            output = source.with_suffix('.AZX').read_text(encoding='latin1').lower()
            self.assertIn('print at 10,5;"zx-81"', output)
            self.assertIn('print at 12,0;"row only"', output)
            self.assertIn('print at 0,0;"default"', output)
            self.assertTrue(source.with_suffix('.p').is_file())

    def test_doubled_and_backslash_quotes_inside_dignified_strings(self):
        repository_root = Path(__file__).resolve().parents[1]
        source_text = (
            'print "TESTE ""123"" OK"\n'
            + r'print "LEGACY \"123\" OK"' + '\n'
        )

        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'doubled_quotes.dzx'
            source.write_text(source_text, encoding='latin1')
            result = subprocess.run(
                [sys.executable, str(repository_root / 'badig.py'),
                 str(source), '-id', 'zx81'],
                capture_output=True,
                text=True,
                cwd=repository_root,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            output = source.with_suffix('.AZX').read_text(encoding='latin1').lower()
            self.assertIn('print "teste ""123"" ok"', output)
            self.assertIn(r'print "legacy \"123\" ok"', output)
            self.assertEqual(source.with_suffix('.p').read_bytes().count(b'\xc0'), 4)

    def test_long_variables_allocate_from_z_down_and_honor_declare(self):
        repository_root = Path(__file__).resolve().parents[1]
        source_text = (
            'declare message:c\n'
            'temperature$ = "warm"\n'
            'counter = 1\n'
            'print temperature$\n'
            'print message$\n'
        )

        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'variables.dzx'
            source.write_text(source_text, encoding='latin1')
            result = subprocess.run(
                [sys.executable, str(repository_root / 'badig.py'),
                 str(source), '-id', 'zx81', '--tk_ascii_only'],
                capture_output=True,
                text=True,
                cwd=repository_root,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            output = source.with_suffix('.AZX').read_text(encoding='latin1').lower()
            self.assertIn('z$="warm"', output)
            self.assertIn('y=1', output)
            self.assertIn('print z$', output)
            self.assertIn('print c$', output)

    def test_rejects_unordered_line_numbers(self):
        with self.assertRaises(ZX81TokenizeError):
            tokenize_lines(['20 PRINT 1', '10 PRINT 2'])

    def test_rejects_unrepresentable_characters(self):
        with self.assertRaises(ZX81TokenizeError):
            tokenize_lines(['10 PRINT "é"'])

    def test_rejects_program_larger_than_reference_limit(self):
        lines = [f'{line_number} REM ' + 'A' * 32
                 for line_number in range(1, 1500)]

        with self.assertRaises(ZX81TokenizeError):
            tokenize_lines(lines)


class DignifierTests(unittest.TestCase):
    SOURCE = (
        '10 REM DEMO\n'
        '20 LET S=0\n'
        '30 GO TO 45\n'
        '40 REM\n'
        '50 PRINT AT 2,X;"\\{0C}";S\n'
        '60 IF S>9 THEN GOTO 20\n'
        '70 GOTO 70\n'
        '80 GOSUB 10*X\n'
    )

    def dignify(self, *arguments, source_text=None):
        repository_root = Path(__file__).resolve().parents[1]
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        source = Path(folder.name) / 'book.AZX'
        source.write_text(source_text or self.SOURCE, encoding='latin1')
        result = subprocess.run(
            [sys.executable, str(repository_root / 'zx81' / 'zx81bader.py'), str(source), *arguments],
            capture_output=True, text=True, cwd=repository_root,
        )
        output = source.with_suffix('.DZX')
        text = output.read_text(encoding='latin1') if output.exists() else ''
        return result, text.splitlines(), output

    def test_default_conversion(self):
        result, lines, _ = self.dignify()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(lines, [
            'rem DEMO',
            '',
            '{l_20}',
            '\tlet s=0',
            '\tgoto {l_50}',
            '\trem',
            '',
            '{l_50}',
            '\t[?](2,x) "\\{0C}";s',
            '\tif s>9 then goto {l_20}',
            '\tgoto {@}',
            '\tgosub 10*x',
        ])
        self.assertIn('Computed_jump_kept', result.stdout)

    def test_options_from_command_line(self):
        result, lines, _ = self.dignify('-tl', '-cp', '-fl', '', '-fr', 'b', '-ut', 'nt',
                                        '-rv', 's:score')

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(lines, [
            'REM DEMO',
            '{l_20}',
            'LET score=0',
            'GOTO {l_50}',
            '',
            '{l_50}',
            'PRINT AT 2,X;"\\{0C}";score',
            'IF score>9 _',
            '\tTHEN _',
            '\tGOTO {l_20}',
            'GOTO {@}',
            'GOSUB 10*X',
        ])

    def test_rem_lines_can_be_removed_and_labels_kept(self):
        result, lines, _ = self.dignify('-fr', 'l', '-fl', '',
                                        source_text='10 REM START\n20 GOTO 10\n')

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(lines, ['{l_10}', 'goto {l_10}'])

    def test_round_trip_renumbers_and_renames(self):
        repository_root = Path(__file__).resolve().parents[1]
        source_text = '10 LET S=0\n20 LET S=S+1\n30 IF S<5 THEN GOTO 20\n40 PRINT S\n'
        result, _, output = self.dignify('-rv', 's:score', source_text=source_text)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        result = subprocess.run(
            [sys.executable, str(repository_root / 'badig.py'), str(output), '-id', 'zx81',
             '-rh', '-ls', '100', '-lp', '5', '--tk_ascii_only'],
            capture_output=True, text=True, cwd=repository_root,
        )
        self.assertNotIn('***', result.stdout, result.stdout + result.stderr)
        self.assertEqual(output.with_suffix('.AZX').read_text(encoding='latin1').splitlines(), [
            '100 let z=0',
            '105 let z=z+1',
            '110 if z<5 then goto 105',
            '115 print z',
        ])

    def test_invalid_input_is_rejected(self):
        for arguments, source_text, message in (
                (['-rv', 's:print'], None, 'Rename_is_a_keyword'),
                (['-rv', 's$:name'], None, 'Invalid_rename'),
                ([], '20 PRINT 1\n10 PRINT 2\n', 'Line_number_out_of_order'),
                ([], 'PRINT 1\n', 'No_line_number')):
            with self.subTest(arguments=arguments, source_text=source_text):
                result, _, output = self.dignify(*arguments, source_text=source_text)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stdout)
                self.assertFalse(output.exists())


@unittest.skipUnless(shutil.which('pwsh'), 'PowerShell is required for helper tests')
class PowerShellHelperTests(unittest.TestCase):
    def test_source_extensions_and_base_names_regenerate_output(self):
        repository_root = Path(__file__).resolve().parents[1]
        cases = [
            ('program.DZX', False, 'print 1\n'),
            ('program.DZX', True, 'print 1\n'),
            ('program.dzx', True, 'print 1\n'),
            ('numbered.DZX', True, '10 PRINT 1\n'),
            ('classic.AZX', True, '10 PRINT 1\n'),
            ('listing.txt', True, '10 PRINT 1\n'),
            ('program.v1.DZX', True, 'print 1\n'),
        ]
        for filename, use_extension, source_text in cases:
            with self.subTest(filename=filename, use_extension=use_extension):
                with tempfile.TemporaryDirectory(prefix='zx81 helper ') as folder:
                    source = Path(folder) / filename
                    source.write_text(source_text, encoding='latin1')
                    binary = source.with_suffix('.p')
                    binary.write_bytes(b'old program')
                    argument = source if use_extension else source.with_suffix('')
                    result = subprocess.run(
                        ['pwsh', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                         str(repository_root / 'zx81' / 'convert-zx81.ps1'), str(argument)],
                        capture_output=True, text=True, cwd=repository_root,
                        env={**os.environ, 'PYTHON': sys.executable},
                    )
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertGreater(binary.stat().st_size, 116)
                    self.assertTrue(source.with_suffix('.AZX').is_file())
                    self.assertEqual(source.read_text(encoding='latin1'), source_text)

    def test_failed_conversion_removes_old_binary_and_reports_failure(self):
        repository_root = Path(__file__).resolve().parents[1]
        for source_text in ('10 REM \\{GG}\n', 'print "\\{GG}"\n'):
            with self.subTest(source_text=source_text):
                with tempfile.TemporaryDirectory() as folder:
                    source = Path(folder) / 'broken.DZX'
                    source.write_text(source_text, encoding='latin1')
                    binary = source.with_suffix('.p')
                    binary.write_bytes(b'old program')
                    result = subprocess.run(
                        ['pwsh', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                         str(repository_root / 'zx81' / 'convert-zx81.ps1'), str(source)],
                        capture_output=True, text=True, cwd=repository_root,
                        env={**os.environ, 'PYTHON': sys.executable},
                    )
                    self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertFalse(binary.exists())
                    self.assertNotIn('Created ', result.stdout)


if __name__ == '__main__':
    unittest.main()