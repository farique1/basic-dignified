"""Convert numbered Sinclair text to Spectrum Dignified, without reading binaries."""

import argparse
import subprocess
import sys
import tempfile
from bisect import bisect_left
from pathlib import Path

from . import VERSION
from .tokenizer_interface import write_output
from .tokenizer_zxspectrum import (
    LINE, MODEL_128_STATEMENTS, STATEMENTS, SpectrumTokenizeError, source_tokens, tokenize,
)


def dignify(source: str, lowercase: bool = True, model: str = '48') -> str:
    tokenize(source, model=model)
    lines = []
    for text in source.splitlines():
        if text.strip():
            match = LINE.fullmatch(text)
            if match is None:
                raise SpectrumTokenizeError('Expected a numbered Sinclair BASIC line')
            lines.append((int(match.group(1)), match.group(2)))
    numbers = [number for number, _ in lines]
    step = numbers[1] - numbers[0] if len(numbers) > 1 else 1
    regular = all(b - a == step for a, b in zip(numbers, numbers[1:]))
    start, step = (numbers[0], step) if regular else (1, 1)
    labels = set()
    converted = []
    for number, body in lines:
        tokens = [token for token in source_tokens(body) if token.value.strip()]
        replacements = []
        statement = None
        for index, token in enumerate(tokens):
            if token.kind == 'rem':
                prefix = 3 if token.value[:3].upper() == 'REM' else 5
                replacements.append((token.start, token.end, r'\{EA}' + token.value[prefix:]))
                break
            if token.kind == 'symbol' and token.value == ':':
                statement = None
                continue
            if token.kind != 'word':
                continue
            keyword = ' '.join(token.value.upper().split())
            if statement is None and (keyword in STATEMENTS
                                      or (model == '128' and keyword in MODEL_128_STATEMENTS)):
                statement = keyword
            if keyword == 'THEN':
                statement = None
            if lowercase:
                replacements.append((token.start, token.end, token.value.lower()))
            if keyword not in ('GO TO', 'GOTO', 'GO SUB', 'GOSUB', 'RUN', 'RESTORE',
                               'LIST', 'LLIST') and not (keyword == 'LINE' and statement == 'SAVE'):
                continue
            operands = []
            for item in tokens[index + 1:]:
                if item.kind == 'rem' or (item.kind == 'symbol' and item.value == ':'):
                    break
                operands.append(item)
            if keyword in ('LIST', 'LLIST') and operands and operands[0].value == '#':
                separator = None
                depth = 0
                for i, item in enumerate(operands):
                    if item.value == '(':
                        depth += 1
                    elif item.value == ')':
                        depth -= 1
                    elif depth == 0 and item.value in (';', ','):
                        separator = i
                        break
                operands = operands[separator + 1:] if separator is not None else []
            if not operands:
                continue
            if len(operands) != 1 or operands[0].kind != 'number' \
                    or not operands[0].value.isdecimal():
                if not regular:
                    raise SpectrumTokenizeError(
                        f'BASIC line {number}: dynamic line reference cannot be safely renumbered')
                continue
            target = int(operands[0].value)
            destination = bisect_left(numbers, target)
            if destination == len(numbers):
                raise SpectrumTokenizeError(
                    f'BASIC line {number}: destination {target} is after the program')
            label = numbers[destination]
            labels.add(label)
            operand = operands[0]
            replacements.append((operand.start, operand.end, f'{{line_{label}}}'))
        for begin, end, value in sorted(replacements, reverse=True):
            body = body[:begin] + value + body[end:]
        converted.append((number, body))
    output = [f'##BB:arguments=-rh -ls {start} -lp {step}']
    for number, body in converted:
        if number in labels:
            output.append(f'{{line_{number}}}')
        output.append(body)
    return '\n'.join(output) + '\n\n'


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=f'ZX Spectrum DignifieR {VERSION}: numbered AZS to DZS')
    parser.add_argument('input', type=Path)
    parser.add_argument('output', nargs='?', type=Path)
    parser.add_argument('-tl', dest='lowercase', action='store_false',
                        help='Keep the case of nonliteral text (default: lowercase)')
    parser.add_argument('-tr', action='store_true', help='Read/write UTF-8 instead of Latin-1')
    parser.add_argument('-vb', type=int, choices=range(6), default=3, help='Verbosity 0..5')
    parser.add_argument('--force', action='store_true', help='Replace an existing destination')
    parser.add_argument('--sp_model', choices=('48', '128'), default='48',
                        help='Target ROM token set of the source (default: 48)')
    args = parser.parse_args(argv)
    destination = args.output or args.input.with_suffix('.DZS')
    try:
        if destination.resolve() == args.input.resolve():
            raise SpectrumTokenizeError('Source and destination must be different files')
        source = args.input.read_text(encoding='utf-8-sig' if args.tr else 'latin-1')
        result = dignify(source, args.lowercase, args.sp_model)
        if destination.exists() and not args.force:
            raise SpectrumTokenizeError('Destination already exists; use --force to replace it')
        with tempfile.TemporaryDirectory(prefix='spectrum-dignifier-') as folder:
            validation = Path(folder) / 'validate.DZS'
            validation.write_text(
                '##BB:em_run=False\n##BB:tk_tokenize=False\n' + result, encoding='latin-1')
            checked = subprocess.run(
                [sys.executable, '-B', str(Path(__file__).resolve().parents[1] / 'badig.py'),
                 str(validation), '-id', 'zxspectrum', '--tk_format', 'tap', '-vb', '0',
                 '--sp_model', args.sp_model],
                capture_output=True, text=True, timeout=30)
            if checked.returncode:
                detail = (checked.stdout + checked.stderr).strip()
                raise SpectrumTokenizeError(
                    f'Generated DZS failed validation (status {checked.returncode}): {detail}')
        write_output(destination, result.encode('utf-8' if args.tr else 'latin-1'))
    except (OSError, UnicodeError, subprocess.TimeoutExpired, SpectrumTokenizeError) as error:
        parser.exit(1, f'*** Spectrum DignifieR: {error}\n')
    if args.vb >= 3:
        print(f'--- Spectrum DignifieR: {destination}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
