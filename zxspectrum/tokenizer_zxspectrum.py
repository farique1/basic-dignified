"""Tokenize the supported Sinclair BASIC 48K subset without external tools."""

import re
from decimal import Decimal, InvalidOperation
from fractions import Fraction


KEYWORDS = (
    'RND', 'INKEY$', 'PI', 'FN', 'POINT', 'SCREEN$', 'ATTR', 'AT', 'TAB',
    'VAL$', 'CODE', 'VAL', 'LEN', 'SIN', 'COS', 'TAN', 'ASN', 'ACS', 'ATN',
    'LN', 'EXP', 'INT', 'SQR', 'SGN', 'ABS', 'PEEK', 'IN', 'USR', 'STR$',
    'CHR$', 'NOT', 'BIN', 'OR', 'AND', '<=', '>=', '<>', 'LINE', 'THEN',
    'TO', 'STEP', 'DEF FN', 'CAT', 'FORMAT', 'MOVE', 'ERASE', 'OPEN #',
    'CLOSE #', 'MERGE', 'VERIFY', 'BEEP', 'CIRCLE', 'INK', 'PAPER', 'FLASH',
    'BRIGHT', 'INVERSE', 'OVER', 'OUT', 'LPRINT', 'LLIST', 'STOP', 'READ',
    'DATA', 'RESTORE', 'NEW', 'BORDER', 'CONTINUE', 'DIM', 'REM', 'FOR',
    'GO TO', 'GO SUB', 'INPUT', 'LOAD', 'LIST', 'LET', 'PAUSE', 'NEXT',
    'POKE', 'PRINT', 'PLOT', 'RUN', 'SAVE', 'RANDOMIZE', 'IF', 'CLS', 'DRAW',
    'CLEAR', 'RETURN', 'COPY',
)
TOKEN_CODES = {word: code for code, word in enumerate(KEYWORDS, 0xA5)}
SUPPORTED = frozenset((
    'PRINT', 'LET', 'IF', 'GO TO', 'REM', 'CLS', 'STOP',
    'THEN', 'AND', 'OR', 'NOT', '<=', '>=', '<>',
))
STATEMENTS = frozenset(('PRINT', 'LET', 'IF', 'GO TO', 'REM', 'CLS', 'STOP'))
NUMBER = re.compile(r'(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?', re.ASCII)
WORD = re.compile(r'[A-Za-z][A-Za-z0-9_]*[$%!#]?')
LINE = re.compile(r'^\s*([0-9]+)\s+(.+)$')
COMPOUND = re.compile(r'(GO\s+(?:TO|SUB)|DEF\s+FN|OPEN\s*#|CLOSE\s*#)\b', re.I)


class SpectrumTokenizeError(ValueError):
    """Source cannot be represented by this Spectrum module."""


def encode_number(text):
    """Encode a nonnegative literal as a Sinclair five-byte number."""
    if not NUMBER.fullmatch(text):
        raise SpectrumTokenizeError(f'Invalid number: {text}')
    try:
        decimal = Decimal(text)
    except InvalidOperation as error:
        raise SpectrumTokenizeError(f'Number outside Sinclair range: {text}') from error
    if decimal.is_zero():
        return bytes(5)
    if not -39 <= decimal.adjusted() <= 38:
        raise SpectrumTokenizeError(f'Number outside Sinclair range: {text}')
    value = Fraction(decimal)
    if value.denominator == 1 and value <= 65535:
        return b'\x00\x00' + int(value).to_bytes(2, 'little') + b'\x00'

    numerator, denominator = value.numerator, value.denominator
    exponent = numerator.bit_length() - denominator.bit_length()
    if exponent >= 0:
        below = numerator < denominator << exponent
    else:
        below = numerator << -exponent < denominator
    if below:
        exponent -= 1
    shift = 31 - exponent
    if shift >= 0:
        numerator <<= shift
    else:
        denominator <<= -shift
    mantissa, remainder = divmod(numerator, denominator)
    if remainder * 2 >= denominator:
        mantissa += 1
    if mantissa == 1 << 32:
        mantissa >>= 1
        exponent += 1
    if not 1 <= exponent + 129 <= 255:
        raise SpectrumTokenizeError(f'Number outside Sinclair range: {text}')
    return bytes((exponent + 129,)) + (mantissa & 0x7FFFFFFF).to_bytes(4, 'big')


def encode_text(text):
    result = bytearray()
    for character in text:
        code = {'\u00a3': 0x60, '\u00a9': 0x7F}.get(character, ord(character))
        if not 32 <= code <= 127 or character in ('`', '\x7f'):
            raise SpectrumTokenizeError(
                f'Unsupported Spectrum character: U+{ord(character):04X}')
        result.append(code)
    return bytes(result)


def tokenize_line(text):
    result = bytearray()
    index = 0
    at_statement = True
    while index < len(text):
        character = text[index]
        if character in ' \t':
            result.append(32)
            index += 1
            continue
        compound = COMPOUND.match(text, index)
        word = WORD.match(text, index)
        if compound or word:
            match = compound or word
            raw = match.group()
            keyword = ' '.join(raw.upper().split())
            keyword = {'GOTO': 'GO TO', 'GOSUB': 'GO SUB'}.get(keyword, keyword)
            if keyword in TOKEN_CODES:
                if keyword not in SUPPORTED:
                    raise SpectrumTokenizeError(
                        f'{keyword} is not supported in Spectrum v1.1.0')
                if at_statement and keyword not in STATEMENTS:
                    raise SpectrumTokenizeError(f'Expected a statement, got {keyword}')
                result.append(TOKEN_CODES[keyword])
                if keyword == 'REM':
                    result.extend(encode_text(text[match.end():]))
                    return bytes(result) + b'\x0d'
                at_statement = keyword == 'THEN'
            else:
                if at_statement:
                    raise SpectrumTokenizeError(
                        f'Expected a supported statement (use explicit LET): {raw}')
                if not re.fullmatch(r'[A-Za-z][A-Za-z0-9]*', raw):
                    raise SpectrumTokenizeError(
                        f'Only alphanumeric numeric scalars are supported: {raw}')
                after = text[match.end():].lstrip()
                if after.startswith('('):
                    raise SpectrumTokenizeError('Arrays and functions are not supported yet')
                result.extend(raw.encode('ascii'))
            index = match.end()
            continue
        if at_statement:
            raise SpectrumTokenizeError('Expected a supported statement after line number, : or THEN')
        if character == '"':
            end = index + 1
            while end < len(text):
                if text[end] == '"':
                    end += 1
                    if end < len(text) and text[end] == '"':
                        end += 1
                        continue
                    break
                end += 1
            else:
                raise SpectrumTokenizeError('Unterminated string')
            result.extend(encode_text(text[index:end]))
            index = end
            continue
        number = NUMBER.match(text, index)
        if number:
            raw = number.group()
            if number.end() < len(text) and text[number.end()] in '.Ee':
                raise SpectrumTokenizeError(f'Invalid number near: {text[index:]}')
            result.extend(raw.encode('ascii'))
            result.append(0x0E)
            result.extend(encode_number(raw))
            index = number.end()
            continue
        pair = text[index:index + 2]
        if pair in ('<=', '>=', '<>'):
            result.append(TOKEN_CODES[pair])
            index += 2
            continue
        if character not in '+-*/^=<>(),;:\'':
            raise SpectrumTokenizeError(f'Unsupported symbol: {character}')
        result.extend(encode_text(character))
        if character == ':':
            at_statement = True
        index += 1
    if at_statement:
        raise SpectrumTokenizeError('Missing statement after : or THEN')
    return bytes(result) + b'\x0d'


def tokenize(source):
    program = bytearray()
    previous = 0
    for source_line, text in enumerate(source.splitlines(), 1):
        if not text.strip():
            continue
        match = LINE.fullmatch(text)
        if not match:
            raise SpectrumTokenizeError(f'Source line {source_line}: expected a numbered BASIC line')
        digits = match.group(1).lstrip('0') or '0'
        if len(digits) > 4:
            raise SpectrumTokenizeError(f'Source line {source_line}: line number exceeds 9999')
        number = int(digits)
        if not previous < number <= 9999:
            raise SpectrumTokenizeError(
                f'Source line {source_line}: line numbers must increase within 1..9999')
        try:
            body = tokenize_line(match.group(2))
        except SpectrumTokenizeError as error:
            raise SpectrumTokenizeError(f'BASIC line {number}: {error}') from error
        if len(body) > 65535:
            raise SpectrumTokenizeError(f'BASIC line {number}: tokenized line too long')
        program.extend(number.to_bytes(2, 'big'))
        program.extend(len(body).to_bytes(2, 'little'))
        program.extend(body)
        previous = number
    if not program:
        raise SpectrumTokenizeError('No BASIC program to tokenize')
    return bytes(program)
