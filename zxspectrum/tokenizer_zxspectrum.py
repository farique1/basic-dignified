"""Tokenize the supported Sinclair BASIC 48K subset without external tools."""

import re
from collections import namedtuple
from decimal import Decimal, InvalidOperation
from fractions import Fraction

from . import VERSION

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
# 128K ROM keywords. On 48K these same codes are the last two UDG graphics
# (%T and %U); the 128K editor ROM repurposes them as SPECTRUM and PLAY.
MODEL_128_TOKENS = {'SPECTRUM': 0xA3, 'PLAY': 0xA4}
TOKEN_CODES = {word: code for code, word in enumerate(KEYWORDS, 0xA5)}
TOKEN_CODES.update(MODEL_128_TOKENS)
CODE_KEYWORDS = {code: word for word, code in TOKEN_CODES.items()}
MODEL_128_SUPPORTED = frozenset(('SPECTRUM', 'PLAY'))
MODEL_128_STATEMENTS = MODEL_128_SUPPORTED
FUNCTIONS = (
    'RND', 'INKEY$', 'PI', 'POINT', 'SCREEN$', 'ATTR', 'VAL$', 'CODE',
    'VAL', 'LEN', 'SIN', 'COS', 'TAN', 'ASN', 'ACS', 'ATN', 'LN', 'EXP',
    'INT', 'SQR', 'SGN', 'ABS', 'PEEK', 'IN', 'USR', 'STR$', 'CHR$', 'FN',
)
SUPPORTED = frozenset((
    'PRINT', 'LET', 'IF', 'GO TO', 'REM', 'CLS', 'STOP',
    'THEN', 'AND', 'OR', 'NOT', '<=', '>=', '<>',
    'BORDER', 'INK', 'PAPER', 'PAUSE', 'BEEP', 'INPUT',
    'GO SUB', 'RETURN', 'FOR', 'NEXT', 'TO', 'STEP',
    'DIM', 'DATA', 'READ', 'RESTORE', 'RANDOMIZE',
    'AT', 'TAB', 'FLASH', 'BRIGHT', 'INVERSE', 'OVER', 'PLOT', 'DRAW',
    'CIRCLE', 'POKE', 'CLEAR', 'RUN', 'LIST', 'NEW', 'CONTINUE', 'OUT', 'BIN',
    'DEF FN', 'LOAD', 'SAVE', 'VERIFY', 'MERGE', 'LINE', 'OPEN #', 'CLOSE #',
    'LPRINT', 'LLIST', 'COPY',
) + FUNCTIONS)
STATEMENTS = frozenset(('PRINT', 'LET', 'IF', 'GO TO', 'REM', 'CLS', 'STOP',
                        'BORDER', 'INK', 'PAPER', 'PAUSE', 'BEEP', 'INPUT',
                        'GO SUB', 'RETURN', 'FOR', 'NEXT',
                        'DIM', 'DATA', 'READ', 'RESTORE', 'RANDOMIZE',
                        'FLASH', 'BRIGHT', 'INVERSE', 'OVER', 'PLOT', 'DRAW',
                        'CIRCLE', 'POKE', 'CLEAR', 'RUN', 'LIST', 'NEW',
                        'CONTINUE', 'OUT', 'DEF FN', 'LOAD', 'SAVE', 'VERIFY',
                        'MERGE', 'OPEN #', 'CLOSE #', 'LPRINT', 'LLIST', 'COPY'))
NUMBER = re.compile(r'(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?', re.ASCII)
WORD = re.compile(r'[A-Za-z][A-Za-z0-9_]*[$%!]?')
BINARY_NUMBER = re.compile(r'[ \t]*([01](?:[ \t]*[01])*)')
LINE = re.compile(r'^\s*([0-9]+)\s+(.+)$')
COMPOUND = re.compile(r'GO\s+(?:TO|SUB)\b|DEF\s+FN\b|(?:OPEN|CLOSE)\s*#', re.I)
GRAPHIC_ESCAPE = re.compile(r'\\([0-9A-Fa-f]{2})')
RAW_ESCAPE = re.compile(r'\\\{([0-9A-Fa-f]{2})\}')
REMX_ARGS = re.compile(
    r'\s*([0-9]+)\s*,\s*([0-9]+)\s*(?:,\s*([0-9]+|"(?:[^"]|"")*"|\'[^\']*\'))?\s*')
MAX_REMX_COUNT = 65532
SourceToken = namedtuple('SourceToken', 'kind value start end')


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


def encode_text(text, raw=True, model='48'):
    result = bytearray()
    index = 0
    while index < len(text):
        character = text[index]
        if text.startswith('\\\\', index) or text.startswith('%%', index):
            result.append(ord(character))
            index += 2
            continue
        if character == '\\':
            escape = RAW_ESCAPE.match(text, index) if raw else None
            if escape:
                code = int(escape.group(1), 16)
            else:
                escape = GRAPHIC_ESCAPE.match(text, index)
                if not escape:
                    raise SpectrumTokenizeError(
                        r'Invalid Spectrum escape: use \80..\A4, \\ or \{XX}')
                code = int(escape.group(1), 16)
                if not 128 <= code <= 164:
                    raise SpectrumTokenizeError(r'Graphic escape must be within \80..\A4')
                if model == '128' and code in MODEL_128_TOKENS.values():
                    raise SpectrumTokenizeError(
                        r'\A3/\A4 are the SPECTRUM/PLAY tokens with --sp_model 128; '
                        r'use \{XX} for the raw byte')
            result.append(code)
            index = escape.end()
            continue
        if character == '%' and index + 1 < len(text) and text[index + 1].isascii() \
                and text[index + 1].isalpha():
            letter = text[index + 1].upper()
            if not 'A' <= letter <= 'U':
                raise SpectrumTokenizeError('Spectrum UDG escapes use %A..%U')
            if model == '128' and letter in ('T', 'U'):
                raise SpectrumTokenizeError(
                    'UDG %T/%U are not available with --sp_model 128; '
                    'those codes are the SPECTRUM/PLAY tokens')
            result.append(144 + ord(letter) - ord('A'))
            index += 2
            continue
        code = {'\u00a3': 0x60, '\u00a9': 0x7F}.get(character, ord(character))
        if not 32 <= code <= 127 or character in ('`', '\x7f'):
            raise SpectrumTokenizeError(
                f'Unsupported Spectrum character: U+{ord(character):04X}')
        result.append(code)
        index += 1
    return bytes(result)


def quoted_end(text, start):
    end = start + 1
    while end < len(text):
        if text[end] == '"':
            end += 1
            if end < len(text) and text[end] == '"':
                end += 1
                continue
            return end
        end += 1
    raise SpectrumTokenizeError('Unterminated string')


def source_tokens(text):
    """Scan readable BASIC while keeping strings, REM and raw bytes opaque."""
    index = 0
    while index < len(text):
        start = index
        if text[index] == '"':
            index = quoted_end(text, index)
            kind = 'string'
        else:
            match = RAW_ESCAPE.match(text, index)
            kind = 'raw'
            if not match:
                match = COMPOUND.match(text, index) or WORD.match(text, index)
                kind = 'word'
            if not match:
                match = NUMBER.match(text, index)
                kind = 'number'
            index = match.end() if match else index + 1
            if not match:
                kind = 'symbol'
        value = text[start:index]
        if (kind == 'word' and value.upper() == 'REM') or (
                kind == 'raw' and int(value[2:4], 16) == TOKEN_CODES['REM']):
            yield SourceToken('rem', text[start:], start, len(text))
            return
        yield SourceToken(kind, value, start, index)


def fn_definition(text, model='48'):
    """Encode the signature, including the ROM's six-byte parameter slots."""
    match = re.match(r'(\s+[A-Za-z]\$?\s*\()([^()]*)(\)\s*=)', text)
    if not match:
        raise SpectrumTokenizeError('DEF FN requires letter[$](parameters)=expression')
    parameters = match.group(2)
    names = parameters.split(',') if parameters.strip() else []
    if any(not re.fullmatch(r'\s*[A-Za-z]\$?\s*', name) for name in names):
        raise SpectrumTokenizeError('DEF FN parameters require single letters with optional $')
    if not text[match.end():].strip() or text[match.end():].lstrip().startswith(':'):
        raise SpectrumTokenizeError('DEF FN requires an expression after =')
    encoded = bytearray(encode_text(match.group(1), model=model))
    for token in source_tokens(parameters):
        encoded.extend(encode_text(token.value, model=model))
        if token.kind == 'word':
            encoded.extend(b'\x0e' + bytes(5))
    encoded.extend(encode_text(match.group(3), model=model))
    return bytes(encoded), match.end()


def validate_fn_call(text):
    for token in source_tokens(text):
        if token.kind == 'symbol' and token.value == ':':
            break
        if token.kind == 'raw':
            return
    match = re.match(r'\s+[A-Za-z]\$?\s*\(', text)
    if not match:
        if re.match(r'\s+\\\{', text):
            return
        raise SpectrumTokenizeError('FN requires letter[$](arguments)')
    depth = 1
    for token in source_tokens(text[match.end():]):
        if token.kind != 'symbol':
            continue
        if token.value == '(':
            depth += 1
        elif token.value == ')':
            depth -= 1
            if depth == 0:
                return
    raise SpectrumTokenizeError('FN requires closing argument parentheses')


def parse_remx(arguments, model='48'):
    """Return an absolute BASIC line and its readable REM payload."""
    match = REMX_ARGS.fullmatch(arguments)
    if not match:
        raise SpectrumTokenizeError('REMX expects <line>,<count>[,<byte or quoted character>]')
    values = []
    for text, maximum, name in zip(match.group(1, 2), (9999, MAX_REMX_COUNT),
                                   ('line', 'count')):
        digits = text.lstrip('0') or '0'
        if len(digits) > len(str(maximum)) or not 1 <= int(digits) <= maximum:
            raise SpectrumTokenizeError(f'REMX {name} must be within 1..{maximum}')
        values.append(int(digits))
    fill = match.group(3)
    if fill is None:
        code = ord('0')
    elif fill[0] in ('"', "'"):
        encoded = encode_text(fill[1:-1].replace('""', '"') if fill[0] == '"'
                              else fill[1:-1], raw=True)
        if len(encoded) != 1:
            raise SpectrumTokenizeError('REMX fill must encode exactly one character')
        code = encoded[0]
    else:
        digits = fill.lstrip('0') or '0'
        if len(digits) > 3 or int(digits) > 255:
            raise SpectrumTokenizeError('REMX byte must be within 0..255')
        code = int(digits)
    if code == 92:
        character = '\\\\'
    elif code == 37:
        character = '%%'
    elif code in (96, 127):
        character = '\u00a3' if code == 96 else '\u00a9'
    elif 32 <= code <= 126:
        character = chr(code)
    elif 128 <= code <= 164 and not (model == '128' and code in MODEL_128_TOKENS.values()):
        character = f'\\{code:02X}'
    else:
        character = f'\\{{{code:02X}}}'
    return values[0], character * values[1]


def validate_identifier(name, array=False, for_control=False):
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9]*\$?', name):
        raise SpectrumTokenizeError(
            f'Invalid Sinclair name: {name}; use DECLARE name:letter for snake_case')
    if name.endswith('$'):
        valid = len(name) == 2 and not for_control
        category = 'String variables'
    else:
        valid = len(name) == 1 if array or for_control else True
        category = 'Arrays and FOR/NEXT variables'
    if not valid:
        raise SpectrumTokenizeError(
            f'{category} require a single letter: {name}; use an explicit DECLARE alias')


def _validate_command_arguments(command, text):
    for token in source_tokens(text):
        if token.kind == 'symbol' and token.value == ':':
            break
        if token.kind == 'raw':
            return
    arguments = []
    start = 0
    depth = 0
    end = len(text)
    for match in re.finditer(r'"(?:[^"]|"")*"|[(),:]', text):
        symbol = match.group()
        if symbol == ':':
            end = match.start()
            break
        if symbol == '(':
            depth += 1
        elif symbol == ')':
            depth -= 1
            if depth < 0:
                raise SpectrumTokenizeError(f'{command}: unbalanced parentheses')
        elif symbol == ',' and depth == 0:
            arguments.append(text[start:match.start()].strip())
            start = match.end()
    if depth:
        raise SpectrumTokenizeError(f'{command}: unbalanced parentheses')
    arguments.append(text[start:end].strip())
    if arguments == ['']:
        arguments = []
    if command in ('NEW', 'CONTINUE', 'COPY', 'SPECTRUM') and arguments:
        raise SpectrumTokenizeError(f'{command} takes no arguments')
    maximum = 2 if command in ('LIST', 'LLIST') and arguments \
        and arguments[0].lstrip().startswith('#') else 1
    if command in ('RUN', 'LIST', 'LLIST') and len(arguments) > maximum:
        raise SpectrumTokenizeError(f'{command} takes at most one expression')
    if command == 'OUT' and (len(arguments) != 2 or not all(arguments)):
        raise SpectrumTokenizeError('OUT requires two expressions separated by a comma')
    if command == 'OPEN #' and (len(arguments) != 2 or not all(arguments)):
        raise SpectrumTokenizeError('OPEN # requires stream,channel')
    if command == 'CLOSE #' and (len(arguments) != 1 or not arguments[0]):
        raise SpectrumTokenizeError('CLOSE # requires one stream')
    if command in ('LOAD', 'SAVE', 'VERIFY', 'MERGE') and not arguments:
        raise SpectrumTokenizeError(f'{command} requires a filename expression')
    if command == 'PLAY' and not (1 <= len(arguments) <= 3 and all(arguments)):
        raise SpectrumTokenizeError('PLAY requires 1 to 3 expressions separated by commas')


def tokenize_line(text, model='48'):
    result = bytearray()
    index = 0
    at_statement = True
    previous_keyword = None
    statement = None
    while index < len(text):
        character = text[index]
        if character in ' \t':
            result.append(32)
            index += 1
            continue
        raw_byte = RAW_ESCAPE.match(text, index)
        if raw_byte:
            code = int(raw_byte.group(1), 16)
            result.append(code)
            index = raw_byte.end()
            if CODE_KEYWORDS.get(code) in STATEMENTS:
                statement = CODE_KEYWORDS[code]
            if code == TOKEN_CODES['REM']:
                result.extend(encode_text(text[index:], model=model))
                return bytes(result) + b'\x0d'
            at_statement = False
            previous_keyword = None
            continue
        if character == '\\':
            raise SpectrumTokenizeError(r'Raw code bytes require \{XX}, exactly two hex digits')
        match = COMPOUND.match(text, index) or WORD.match(text, index)
        if match:
            raw = match.group()
            keyword = ' '.join(raw.upper().split())
            keyword = {'GOTO': 'GO TO', 'GOSUB': 'GO SUB'}.get(keyword, keyword)
            keyword = re.sub(r'^(OPEN|CLOSE)\s*#$', r'\1 #', keyword)
            if keyword in TOKEN_CODES:
                model_128_only = keyword in MODEL_128_SUPPORTED
                if model_128_only and model != '128':
                    raise SpectrumTokenizeError(f'{keyword} requires --sp_model 128')
                if not model_128_only and keyword not in SUPPORTED:
                    raise SpectrumTokenizeError(
                        f'{keyword} is not supported in Spectrum v{VERSION}')
                is_statement = keyword in STATEMENTS or (model == '128'
                                                          and keyword in MODEL_128_STATEMENTS)
                if at_statement and not is_statement:
                    raise SpectrumTokenizeError(f'Expected a statement, got {keyword}')
                if at_statement:
                    statement = keyword
                if keyword in ('RUN', 'LIST', 'LLIST', 'NEW', 'CONTINUE', 'OUT',
                               'OPEN #', 'CLOSE #', 'COPY', 'LOAD', 'SAVE', 'VERIFY', 'MERGE',
                               'PLAY', 'SPECTRUM'):
                    if not at_statement:
                        raise SpectrumTokenizeError(f'{keyword} must start a statement')
                    _validate_command_arguments(keyword, text[match.end():])
                result.append(TOKEN_CODES[keyword])
                if keyword == 'DEF FN':
                    tail = text[match.end():]
                    if not RAW_ESCAPE.search(tail.split('=', 1)[0]):
                        encoded, consumed = fn_definition(tail, model=model)
                        result.extend(encoded)
                        index = match.end() + consumed
                    else:
                        index = match.end()
                    at_statement = False
                    previous_keyword = None
                    continue
                if keyword == 'FN':
                    validate_fn_call(text[match.end():])
                if keyword == 'BIN':
                    binary = BINARY_NUMBER.match(text, match.end())
                    if not binary:
                        raise SpectrumTokenizeError('BIN requires binary digits 0 or 1')
                    suffix = text[binary.end():]
                    following = suffix.lstrip(' \t')
                    if (suffix and (suffix[0].isalnum() or suffix[0] in '._$')) \
                            or (following and following[0] in '0123456789.'):
                        raise SpectrumTokenizeError('Invalid BIN literal: use only binary digits')
                    digits = binary.group(1).replace(' ', '').replace('\t', '').lstrip('0')
                    if len(digits) > 16:
                        raise SpectrumTokenizeError('BIN value exceeds 65535')
                    result.extend(encode_text(binary.group().replace('\t', ' '), model=model))
                    result.append(0x0E)
                    result.extend(encode_number(str(int(digits or '0', 2))))
                    index = binary.end()
                    at_statement = False
                    previous_keyword = None
                    continue
                if keyword == 'REM':
                    result.extend(encode_text(text[match.end():], raw=True, model=model))
                    return bytes(result) + b'\x0d'
                at_statement = keyword == 'THEN'
                previous_keyword = keyword
            else:
                if at_statement:
                    raise SpectrumTokenizeError(
                        f'Expected a supported statement (use explicit LET): {raw}')
                after = text[match.end():].lstrip()
                validate_identifier(raw, array=after.startswith('('),
                                    for_control=previous_keyword in ('FOR', 'NEXT'))
                result.extend(raw.encode('ascii'))
                previous_keyword = None
            index = match.end()
            continue
        if at_statement:
            raise SpectrumTokenizeError('Expected a supported statement after line number, : or THEN')
        if character == '"':
            end = quoted_end(text, index)
            result.extend(encode_text(text[index:end], model=model))
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
        if character == '#' and statement not in ('PRINT', 'INPUT', 'LIST', 'LPRINT', 'LLIST'):
            raise SpectrumTokenizeError('# stream selector requires PRINT, INPUT or LIST')
        if character not in '+-*/^=<>(),;:\'#':
            raise SpectrumTokenizeError(f'Unsupported symbol: {character}')
        result.extend(encode_text(character, model=model))
        if character == ':':
            at_statement = True
        index += 1
    if at_statement:
        raise SpectrumTokenizeError('Missing statement after : or THEN')
    return bytes(result) + b'\x0d'


def tokenize(source, model='48'):
    if model not in ('48', '128'):
        raise SpectrumTokenizeError(f'Unknown Spectrum model: {model}; use 48 or 128')
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
            body = tokenize_line(match.group(2), model=model)
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
