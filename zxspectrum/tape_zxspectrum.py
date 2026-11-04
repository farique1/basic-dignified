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


def make_tap(program, name):
    if not program:
        raise SpectrumTokenizeError('Cannot save an empty BASIC program')
    if len(program) > MAX_PROGRAM_BYTES:
        raise SpectrumTokenizeError(
            f'BASIC exceeds the initial 48K program area ({MAX_PROGRAM_BYTES} bytes); '
            'runtime variables and stacks need additional space')
    if not 1 <= len(name) <= 10 or any(not 32 <= ord(char) <= 126 for char in name):
        raise SpectrumTokenizeError('Tape name must contain 1..10 printable ASCII characters')
    size = len(program).to_bytes(2, 'little')
    header = b'\x00\x00' + name.encode('ascii').ljust(10, b' ')
    header += size + b'\x00\x80' + size
    return tap_block(header) + tap_block(b'\xff' + program)
