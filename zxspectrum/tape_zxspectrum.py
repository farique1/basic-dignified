"""Standard ROM-loadable Spectrum TAP programs."""

from .tokenizer_zxspectrum import SpectrumTokenizeError


# Default 48K PROG=23755 and RAMTOP=65367; runtime workspace is additional.
MAX_PROGRAM_BYTES = 65367 - 23755


def tap_block(data):
    checksum = 0
    for value in data:
        checksum ^= value
    block = data + bytes((checksum,))
    if len(block) > 65535:
        raise SpectrumTokenizeError('TAP block exceeds 65535 bytes')
    return len(block).to_bytes(2, 'little') + block


def make_tap(program, name, autorun=None):
    if not program:
        raise SpectrumTokenizeError('Cannot save an empty BASIC program')
    if len(program) > MAX_PROGRAM_BYTES:
        raise SpectrumTokenizeError(
            f'BASIC exceeds the initial 48K program area ({MAX_PROGRAM_BYTES} bytes); '
            'runtime variables and stacks need additional space')
    if not 1 <= len(name) <= 10 or any(not 32 <= ord(char) <= 126 for char in name):
        raise SpectrumTokenizeError('Tape name must contain 1..10 printable ASCII characters')
    if autorun is not None and (type(autorun) is not int or not 0 <= autorun <= 9999):
        raise SpectrumTokenizeError('Autorun must be a line within 0..9999 or None')
    size = len(program).to_bytes(2, 'little')
    header = b'\x00\x00' + name.encode('ascii').ljust(10, b' ')
    header += size + (32768 if autorun is None else autorun).to_bytes(2, 'little') + size
    return tap_block(header) + tap_block(b'\xff' + program)


def make_tzx(program, name, autorun=None):
    """TZX 1.20 with standard-speed blocks and one-second pauses."""
    tape = make_tap(program, name, autorun)
    result = bytearray(b'ZXTape!\x1a\x01\x14')
    offset = 0
    while offset < len(tape):
        size = int.from_bytes(tape[offset:offset + 2], 'little')
        result.extend(b'\x10\xe8\x03')
        result.extend(tape[offset:offset + size + 2])
        offset += size + 2
    return bytes(result)
