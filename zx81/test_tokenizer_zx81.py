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

    def test_program_pointers_follow_program_and_display_file(self):
        program = tokenize_lines(['10 PRINT 1'])
        data_file = int.from_bytes(program[3:5], 'little')
        variables = int.from_bytes(program[7:9], 'little')

        self.assertEqual(data_file, 0x407D + 13)
        self.assertEqual(variables, data_file + 793)
        self.assertEqual(program[-2:], b'\x80\x76')

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


if __name__ == '__main__':
    unittest.main()