import math
import re


TOKEN_CODES = {
    'copy': 255,
    'return': 254,
    'clear': 253,
    'unplot': 252,
    'cls': 251,
    'if': 250,
    'randomize': 249,
    'rand': 249,
    'save': 248,
    'run': 247,
    'plot': 246,
    'print': 245,
    'poke': 244,
    'next': 243,
    'pause': 242,
    'let': 241,
    'list': 240,
    'load': 239,
    'input': 238,
    'go sub': 237,
    'gosub': 237,
    'go to': 236,
    'goto': 236,
    'for': 235,
    'rem': 234,
    'dim': 233,
    'continue': 232,
    'cont': 232,
    'scroll': 231,
    'new': 230,
    'fast': 229,
    'slow': 228,
    'stop': 227,
    'llist': 226,
    'lprint': 225,
    'step': 224,
    'to': 223,
    'then': 222,
    '<>': 221,
    '>=': 220,
    '<=': 219,
    'and': 218,
    'or': 217,
    '**': 216,
    'not': 215,
    'chr$': 214,
    'str$': 213,
    'usr': 212,
    'peek': 211,
    'abs': 210,
    'sgn': 209,
    'sqr': 208,
    'int': 207,
    'exp': 206,
    'ln': 205,
    'atn': 204,
    'acs': 203,
    'asn': 202,
    'tan': 201,
    'cos': 200,
    'sin': 199,
    'len': 198,
    'val': 197,
    'code': 196,
    'tab': 194,
    'at': 193,
    'pi': 66,
    'inkey$': 65,
    'rnd': 64,
}

CHAR_CODES = {
    ' ': 0,
    '"': 11,
    '#': 12,
    '$': 13,
    ':': 14,
    '?': 15,
    '(': 16,
    ')': 17,
    '>': 18,
    '<': 19,
    '=': 20,
    '+': 21,
    '-': 22,
    '*': 23,
    '/': 24,
    ';': 25,
    ',': 26,
    '.': 27,
}

GRAPHICS_CODES = {
    '  ': 0,
    "' ": 1,
    " '": 2,
    "''": 3,
    '. ': 4,
    ': ': 5,
    ".'": 6,
    ":'": 7,
    '##': 8,
    ',,': 9,
    '~~': 10,
    '::': 128,
    '.:': 129,
    ':.' : 130,
    '..': 131,
    "':": 132,
    ' :': 133,
    "'.": 134,
    ' .': 135,
    '@@': 136,
    ';;': 137,
    '!!': 138,
}

TOKEN_MATCHES = tuple(sorted(TOKEN_CODES, key=len, reverse=True))
HEX_ESCAPE_MATCH = re.compile(r'\\\{([0-9a-fA-F]{2})\}')
NUMBER_MATCH = re.compile(r'(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?')
LINE_MATCH = re.compile(r'^\s*(\d+)(?:\s+|$)(.*)$')
REMX_IGNORE = r'\s*remx(?![A-Za-z0-9_$])'
REMX_MATCH = re.compile(fr'^{REMX_IGNORE}(.*?)\s*$', re.I)
REMX_ARGS = re.compile(r'^\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(\d+|"[^"]"|\'[^\']\'))?$')
REMX_MAX = 49152
PROGRAM_START = 0x407D
# Display file (793) and variables end marker (3) must also fit below 64 KB.
PROGRAM_MAX = 0x10000 - PROGRAM_START - 793 - 3


class ZX81TokenizeError(ValueError):
    pass


def parse_remx(arguments, source_line):
    '''Return (line number, count, byte) for remx <line>,<count>[,<byte>]'''
    args = REMX_ARGS.match(arguments)
    if not args:
        raise ZX81TokenizeError(
            f'Input line {source_line}: remx expects <line>,<count>[,<byte>]'
        )
    number, count, fill = int(args.group(1)), int(args.group(2)), args.group(3)
    if number > 9999:
        raise ZX81TokenizeError(
            f'Input line {source_line}: remx line number must be 0..9999'
        )
    if not 1 <= count <= REMX_MAX:
        raise ZX81TokenizeError(
            f'Input line {source_line}: remx count must be 1..{REMX_MAX}'
        )
    if fill is None:
        code = _character_code('0', source_line)
    elif fill[0] in '"\'':
        code = _character_code(fill[1], source_line)
    else:
        code = int(fill)
        if code > 255:
            raise ZX81TokenizeError(
                f'Input line {source_line}: remx byte must be 0..255'
            )
    return number, count, code


def _character_code(char, line_number):
    if char.isascii() and char.isalpha():
        return ord(char.lower()) - 59
    if char.isascii() and char.isdigit():
        return ord(char) - 20
    if char in CHAR_CODES:
        return CHAR_CODES[char]
    if char in "!%&'@":
        raise ZX81TokenizeError(
            f'Line {line_number}: character {char!r} cannot be represented'
        )
    if ord(char) < 128:
        return ord(char)
    raise ZX81TokenizeError(
        f'Line {line_number}: non-ASCII character {char!r} cannot be represented'
    )


def _number_bytes(text, line_number):
    value = float(text)
    magnitude = abs(value)
    if magnitude == 0:
        exponent = 0
        mantissa = 0
    else:
        fraction, binary_exponent = math.frexp(magnitude)
        exponent = binary_exponent + 128
        mantissa = round((fraction * 2 - 1) * 0x80000000)
        if mantissa == 0x80000000:
            mantissa = 0
            exponent += 1
        # Exponent byte 0 means the number zero on the ZX-81.
        if not 1 <= exponent <= 255:
            raise ZX81TokenizeError(
                f'Line {line_number}: number exponent out of range: {text}'
            )

    encoded = bytearray(_character_code(char, line_number) for char in text)
    encoded.append(0x7E)
    encoded.append(exponent)
    encoded.extend(mantissa.to_bytes(4, 'big'))
    return encoded


def _match_token(text, index):
    lower_text = text.lower()
    for token in TOKEN_MATCHES:
        if token in ('go to', 'go sub'):
            match = re.match(r'go\s+' + token[3:], lower_text[index:])
            if not match:
                continue
            end = index + match.end()
        else:
            if not lower_text.startswith(token, index):
                continue
            end = index + len(token)

        if token[0].isalpha() and index and text[index - 1].isalpha():
            continue
        if token[-1].isalpha() and end < len(text) and text[end].isalpha():
            continue
        return end, TOKEN_CODES[token], token
    return None


def _tokenize_line(text, line_number):
    output = bytearray()
    index = 0
    in_quotes = False
    in_rem = False

    while index < len(text):
        char = text[index]

        if text.startswith('\\{', index):
            escape = HEX_ESCAPE_MATCH.match(text, index)
            if not escape:
                raise ZX81TokenizeError(
                    f'Line {line_number}: invalid hexadecimal escape; expected \\{{XX}}'
                )
            output.append(int(escape.group(1), 16))
            index = escape.end()
            continue

        if in_quotes and not in_rem and char == '"' \
                and index + 1 < len(text) and text[index + 1] == '"':
            output.append(192)
            index += 2
            continue

        if char == '"':
            in_quotes = not in_quotes
            output.append(CHAR_CODES['"'])
            index += 1
            continue

        if not in_quotes and not in_rem and char.isspace():
            index += 1
            continue

        if not in_rem and char == '%' and index + 1 < len(text):
            output.append(_character_code(text[index + 1], line_number) | 0x80)
            index += 2
            continue

        if not in_rem and char == '\\' and index + 1 < len(text):
            escaped = text[index + 1]
            if escaped == '"':
                output.append(192)
                index += 2
                continue
            graphic = text[index + 1:index + 3]
            if graphic in GRAPHICS_CODES:
                output.append(GRAPHICS_CODES[graphic])
                index += 3
                continue
            output.append(_character_code(escaped, line_number))
            index += 2
            continue

        if not in_quotes and not in_rem:
            token = _match_token(text, index)
            if token:
                index, code, token_text = token
                output.append(code)
                if token_text == 'rem':
                    in_rem = True
                    if text[index:index + 1] == ' ':
                        index += 1
                continue

            preceding = text[index - 1] if index else ''
            if (not preceding.isalpha() and
                    (char.isdigit() or
                     (char in '+-.' and index + 1 < len(text) and
                      (text[index + 1].isdigit() or
                       (text[index + 1] == '.' and index + 2 < len(text)
                        and text[index + 2].isdigit()))))):
                number = NUMBER_MATCH.match(text, index + (char in '+-'))
                if number:
                    end = number.end()
                    if char in '+-':
                        number_text = char + number.group()
                    else:
                        number_text = number.group()
                    if text[end:end + 5].lower() == r'\{7e}':
                        output.extend(_character_code(digit, line_number)
                                      for digit in number_text)
                    else:
                        output.extend(_number_bytes(number_text, line_number))
                    index = end
                    continue

        output.append(_character_code(char, line_number))
        index += 1

    output.append(0x76)
    if len(output) > 0xFFFF:
        raise ZX81TokenizeError(f'Line {line_number}: line is too long')
    return output


def _word(value):
    return bytes((value & 0xFF, (value >> 8) & 0xFF))


def tokenize_lines(lines):
    program = bytearray()
    line_numbers = []

    for source_line, text in enumerate(lines, 1):
        text = text.rstrip('\r\n')
        if not text.strip() or text.lstrip().startswith('#'):
            continue

        remx = REMX_MATCH.match(text)
        if remx:
            line_number, count, code = parse_remx(remx.group(1), source_line)
            encoded_line = bytes((TOKEN_CODES['rem'],)) + bytes((code,)) * count + b'\x76'
        else:
            match = LINE_MATCH.match(text)
            if not match:
                raise ZX81TokenizeError(
                    f'Input line {source_line}: expected a numbered BASIC line'
                )
            line_number = int(match.group(1))
            encoded_line = None

        if line_number > 9999:
            raise ZX81TokenizeError(
                f'Input line {source_line}: line number must be 0..9999'
            )
        if line_numbers and line_number <= line_numbers[-1]:
            raise ZX81TokenizeError(
                f'Input line {source_line}: line numbers must increase'
            )

        if encoded_line is None:
            encoded_line = _tokenize_line(match.group(2), line_number)
        if len(program) + 4 + len(encoded_line) > PROGRAM_MAX:
            raise ZX81TokenizeError(
                f'Program is too large for a ZX-81 .P file: the program area '
                f'cannot exceed {PROGRAM_MAX} bytes'
            )
        program.extend(((line_number >> 8) & 0xFF, line_number & 0xFF))
        program.extend((len(encoded_line) & 0xFF, (len(encoded_line) >> 8) & 0xFF))
        program.extend(encoded_line)
        line_numbers.append(line_number)

    return _program_file(program, line_numbers[0] if line_numbers else 0)


def _program_file(program, first_line):
    data_file = PROGRAM_START + len(program)
    vars_address = data_file + 793
    system_vars = bytearray(116)
    system_vars[1:3] = _word(first_line)
    system_vars[3:5] = _word(data_file)
    system_vars[5:7] = _word(data_file + 1)
    system_vars[7:9] = _word(vars_address)
    system_vars[11:13] = _word(vars_address + 1)
    system_vars[13:15] = _word(vars_address + 2)
    system_vars[17:19] = _word(vars_address + 3)
    system_vars[19:21] = _word(vars_address + 3)
    system_vars[22:24] = _word(0x405D)
    system_vars[25] = 2
    system_vars[28:30] = b'\xFF\xFF'
    system_vars[30] = 0x0F
    system_vars[31] = 55
    system_vars[32:34] = _word(data_file)
    system_vars[39:41] = _word(0x0C6B)
    system_vars[43:45] = _word(0xFD7D)
    system_vars[47] = 0xBC
    system_vars[48] = 0x21
    system_vars[49] = 0x18
    system_vars[50] = 0x40
    system_vars[83] = 0x76

    display_file = bytearray((0x76,))
    display_line = bytes(32) + b'\x76'
    display_file.extend(display_line * 24)
    variables = b'\x80\x76'
    return bytes(system_vars + program + display_file + variables)


def tokenize_file(source_path, output_path):
    with open(source_path, 'r', encoding='latin1') as source:
        encoded = tokenize_lines(source)
    with open(output_path, 'wb') as output:
        output.write(encoded)