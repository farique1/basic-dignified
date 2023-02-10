#!/usr/bin/env python3
"""
CoCo to CAS
Convert BAS, ASC or BIN files to CAS.

Part of the Basic Dignified Suite
https://github.com/farique1/basic-dignified

Copyright (C) 2020 - Fred Rique (farique)

For help use:
cocotocas.py -h
"""

import os
import binascii
import argparse
from argparse import RawDescriptionHelpFormatter


class Convert:
    def __init__(self):
        self.file_load = ''
        self.file_save = ''
        self.file_format = ''

    def arguments(self):
        parser = argparse.ArgumentParser(description='Convert CoCo programs to .cas format.\n'
                                                     'Guess input format based on extension:\n'
                                                     'asc: ASCII Basic programs.\n'
                                                     'bas: binary Basic programs.\n'
                                                     'bin: binary programs\n'
                                                     'Can be forced with -ff <type>.', formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("input", nargs='?', default=self.file_load, help='File to convert')
        parser.add_argument("output", nargs='?', default=self.file_save, help='.cas file to export')
        parser.add_argument("-ff", default=self.file_format, choices=['bas', 'bin', 'asc'], type=str.lower, help="Override type: bas, bin, asc")
        args = parser.parse_args()

        self.file_load = args.input
        self.file_save = args.output
        self.file_format = args.ff

    def bytes_from_file(self, filename, chunksize=8192):
        with open(filename, "rb") as f:
            while True:
                chunk = f.read(chunksize)
                if chunk:
                    for b in chunk:
                        yield b
                else:
                    break

    def get_checksum(self, string):
        chksum = 0
        for (l, h) in zip(string[0::2], string[1::2]):
            byte = int(l + h, 16)
            chksum = (chksum + byte) % 256
        return '{0:02x}'.format(chksum)

    def execute(self):
        bin_file = []               # Loaded file
        cas_file = ''               # Export file
        b_leader = '55' * 127       # Sync gap. Last '55' on b_magic_bytes
        b_magic_bytes = '55553c'    # Magic bytes
        b_block_type = '00'         # 00=filename, 01=data, FF=EOF
        b_file_type = '00'          # 00=BASIC, 01=data, 02=machine code
        b_ascii_flag = '00'         # 00=binary, FF=ASCII
        b_gap_flag = '00'           # 00=no gaps, FF=gaps
        b_exec_addrs = '0000'       # Machine code start address
        b_strt_addrs = '0000'       # Machine code load address
        b_chksum = '00'             # Block checksum byte
        b_block_len = '00'          # Block length
        b_filename = '02' * 8       # Filename

        file_ext = os.path.splitext(self.file_load)[1][1:].lower() if self.file_format == '' else self.file_format
        file_temp = self.file_load if self.file_save == '' else self.file_save
        file_path = os.path.split(os.path.realpath(file_temp))[0]
        file_name = os.path.split(os.path.splitext(file_temp)[0])[1]
        self.file_save = os.path.join(file_path, file_name) + '.CAS'

        if self.file_load == '':
            print('*** No file given.')
            raise SystemExit(0)

        if not os.path.isfile(self.file_load):
            print('*** File not found.')
            raise SystemExit(0)

        if file_ext == '':
            print('*** No extension or override given.')
            raise SystemExit(0)

        for b in self.bytes_from_file(self.file_load):
            bin_file.append('{0:02x}'.format(b))

        if file_ext == 'bas' and bin_file[0] == 'ff':
            del bin_file[:3]

        # Filename Block
        b_block_type = '00'     # filename block
        b_block_len = '0f'      # filename block length
        b_filename = ''.join(['{0:02x}'.format(ord(elem)) for elem in file_name[:8].upper()])
        b_filename += '20' * ((16 - len(b_filename)) // 2)
        b_file_type = '00' if file_ext == 'bas' or file_ext == 'asc' else '02' if file_ext == 'bin' else '01'
        b_ascii_flag = '00' if file_ext == 'bas' or file_ext == 'bin' else 'ff'
        b_gap_flag = '00' if file_ext == 'bas' or file_ext == 'bin' else 'ff'
        if file_ext == 'bin':
            # Byte 1 and 2 file size, byte 3 and 4 start address, last two bytes exec address
            b_strt_addrs = ''.join(bin_file[3:5])  # bytes 3 and 4
            b_exec_addrs = ''.join(bin_file[-2:])  # last two bytes
            del bin_file[:5]
        block_filename = b_block_type + b_block_len + b_filename + \
            b_file_type + b_ascii_flag + b_gap_flag + b_exec_addrs + b_strt_addrs
        b_chksum = self.get_checksum(block_filename)
        cas_file = b_leader + b_magic_bytes + block_filename + b_chksum + b_leader
        b_leader = '' if b_gap_flag == '00' else b_leader

        # Data Block
        b_block_type = '01'  # data block
        pointer = 0
        data_block_len = 255
        while data_block_len == 255:
            data_block = bin_file[pointer:pointer + 255]
            data_block_len = len(data_block)
            b_block_len = '{0:02x}'.format(data_block_len)
            block_chksum = b_block_type + b_block_len + ''.join(data_block)
            b_chksum = self.get_checksum(block_chksum)
            block_data = b_magic_bytes[2:] + block_chksum + b_chksum
            cas_file += block_data + b_leader
            pointer += 255

        # EOF Block
        b_block_type = 'ff'  # EOF block
        b_block_len = '00'  # EOF block length
        b_chksum = 'ff'  # EOF block checksum
        cas_file += b_magic_bytes + b_block_type + b_block_len + b_chksum + b_magic_bytes[:2]

        with open(self.file_save, 'wb') as f:
            for (l, h) in zip(cas_file[0::2], cas_file[1::2]):
                f.write(binascii.unhexlify(l + h))


def main():
    conv = Convert()
    conv.arguments()
    conv.execute()


if __name__ == '__main__':
    main()
