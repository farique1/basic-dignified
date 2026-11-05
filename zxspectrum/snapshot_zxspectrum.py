"""Build 48K snapshots using the optional, locally installed SkoolKit engine."""

import struct
import sys
from pathlib import Path
from types import SimpleNamespace


LOAD_RETURN = 0x1B76


def read_registers(data):
    """Read the documented register header of the engine's 48K Z80 v3 output."""
    if (len(data) < 86 or data[6:8] != b'\0\0'
            or int.from_bytes(data[30:32], 'little') not in (54, 55)
            or data[34] != 0):
        raise ValueError('Snapshot engine must produce a 48K Z80 v3 state')
    pairs = {name: struct.unpack_from('<H', data, offset)[0] for name, offset in (
        ('bc', 2), ('hl', 4), ('sp', 8), ('de', 13), ('bc2', 15),
        ('de2', 17), ('hl2', 19), ('iy', 23), ('ix', 25), ('pc', 32))}
    return SimpleNamespace(
        **pairs, a=data[0], f=data[1], i=data[10],
        r=(data[11] & 127) | ((data[12] & 1) << 7),
        border=(data[12] >> 1) & 7, a2=data[21], f2=data[22],
        iff1=int(bool(data[27])), iff2=int(bool(data[28])), im=data[29] & 3)


def make_sna(snapshot, memory):
    ram = bytearray(memory)
    if len(ram) != 49152 or not 16386 <= snapshot.sp <= 65535:
        raise ValueError('SNA requires 48K RAM and a stack with room for the saved PC')
    if snapshot.iff1 != snapshot.iff2:
        raise ValueError('SNA cannot preserve different IFF1 and IFF2 states')
    stack = snapshot.sp - 2
    ram[stack - 16384:stack - 16382] = snapshot.pc.to_bytes(2, 'little')
    header = struct.pack(
        '<B9HBBHHBB', snapshot.i, snapshot.hl2, snapshot.de2, snapshot.bc2,
        snapshot.a2 * 256 + snapshot.f2, snapshot.hl, snapshot.de, snapshot.bc,
        snapshot.iy, snapshot.ix, snapshot.iff2 * 4, snapshot.r,
        snapshot.a * 256 + snapshot.f, stack, snapshot.im, snapshot.border)
    return header + ram


def build():
    from skoolkit import VERSION, SkoolKitError
    from skoolkit.snapshot import get_snapshot
    from skoolkit.tap2sna import main

    try:
        # Basenames avoid SkoolKit interpreting a Windows drive as a URL.
        simulation = ['--sim-load'] if VERSION.startswith('8.') else ['-c', 'machine=48']
        main(simulation + ['-c', 'fast-load=1', '-c', 'finish-tape=1',
              '-c', 'timeout=60', '--start', str(LOAD_RETURN), 'input.tap', 'state.z80'])
        snapshot = read_registers(Path('state.z80').read_bytes())
        ram = bytes(get_snapshot('state.z80')[16384:])
        tape = Path('input.tap').read_bytes()
        program = tape[24:-1]
        prog = int.from_bytes(ram[23635 - 16384:23637 - 16384], 'little')
        variables = int.from_bytes(ram[23627 - 16384:23629 - 16384], 'little')
        if (len(ram) != 49152 or snapshot.pc != LOAD_RETURN or prog != 23755
                or variables != prog + len(program)
                or variables >= snapshot.sp - 2
                or ram[prog - 16384:variables - 16384] != program
                or ram[variables - 16384] != 128):
            raise ValueError('ROM loading did not reach the expected pre-execution 48K state')
        Path('state.sna').write_bytes(make_sna(snapshot, ram))
    except (OSError, ValueError, SkoolKitError) as error:
        print(f'Spectrum snapshot: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    try:
        sys.exit(build())
    except ModuleNotFoundError as error:
        print(f'Spectrum snapshots require optional SkoolKit: {error}. '
              f'Install with "{sys.executable}" -m pip install "skoolkit>=8.10,<11"',
              file=sys.stderr)
        sys.exit(1)
