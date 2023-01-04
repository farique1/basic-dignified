#!/usr/bin/env python3
"""
MSX Basic Tokenizer
v2.0
Convert ASCII MSX Basic to tokenized format

Copyright (C) 2019-2022 - Fred Rique (farique)
https://github.com/farique1/basic-dignified

The complete suite includes:
Basic Dignified
    A modern take on 8 bit classic Basics
    Support for any classic Basic though description modules
Basic DignifieR
    Convert classic Basic to Dignified format
Syntax Highlight, Theme, Build System, Comment Preference and Auto Completion
    for Sublime Text 3 and 4

msxbatoken.py <source> <destination> [args...]
msxbatoken.py -h for help.

New: 2.0v 25/03/2022
    Modular design for integration with Basic Dignified v2.0

Notes:
    Known discrepancies:
        MSX &b (binary notation) tokenizes anything after it as characters except when a tokenized command is reached.
            The implementation here only looks for 0 and 1, reverting back to the normal parsing when other characters are found.
        Spaces at the end of a line are removed.
            The MSX does not remove them if loading from an ASCII file, only if typed on the machine.
        The MSX seems to split overflowed numbers on branching instructions (preceded by 0e), here it throw an error.
        Syntax errors generates wildly different results from the ones generated by the MSX.
    Conversion stopping errors:
        Line number too high, Line number out of order, Lines not starting with numbers, Branching lines too high
        Numbers bigger than their explicit type (in some cases they are converted up as per on the MSX)
    Tested with over 100 random basic programs from magazines and other sources, some crated to stress the conversions
        However there should be still some (several?) fringe cases not covered here. Be careful.
"""

import re
import os.path
import binascii
from datetime import datetime
from os import remove as osremove
from collections import namedtuple
import time

# Whether part of Badig or standalone
try:
    from .msxbatoken_settings import Settings
except (ImportError, ModuleNotFoundError):
    from msxbatoken_settings import Settings

# Whether part of Badig or standalone
try:
    from Modules.Support import infolog
except (ImportError, ModuleNotFoundError):
    import infolog

BASE = 0x8001

TOKENS = [('>', 'ee'), ('PAINT', 'bf'), ('=', 'ef'), ('ERROR', 'a6'), ('ERR', 'e2'), ('<', 'f0'), ('+', 'f1'),
          ('FIELD', 'b1'), ('PLAY', 'c1'), ('-', 'f2'), ('FILES', 'b7'), ('POINT', 'ed'), ('*', 'f3'), ('POKE', '98'),
          ('/', 'f4'), ('FN', 'de'), ('^', 'f5'), ('FOR', '82'), ('PRESET', 'c3'), ('\\', 'fc'), ('PRINT', '91'), ('?', '91'),
          ('PSET', 'c2'), ('AND', 'f6'), ('GET', 'b2'), ('PUT', 'b3'), ('GOSUB', '8d'), ('READ', '87'), ('GOTO', '89'),
          ('ATTR$', 'e9'), ('RENUM', 'aa'), ('AUTO', 'a9'), ('IF', '8b'), ('RESTORE', '8c'), ('BASE', 'c9'), ('IMP', 'fa'),
          ('RESUME', 'a7'), ('BEEP', 'c0'), ('INKEY$', 'ec'), ('RETURN', '8e'), ('BLOAD', 'cf'), ('INPUT', '85'),
          ('BSAVE', 'd0'), ('INSTR', 'e5'), ('RSET', 'b9'), ('CALL', 'ca'), ('_', '5f'), ('RUN', '8a'), ('IPL', 'd5'), ('SAVE', 'ba'),
          ('KEY', 'cc'), ('SCREEN', 'c5'), ('KILL', 'd4'), ('SET', 'd2'), ('CIRCLE', 'bc'), ('CLEAR', '92'), ('CLOAD', '9b'),
          ('LET', '88'), ('SOUND', 'c4'), ('CLOSE', 'b4'), ('LFILES', 'bb'), ('CLS', '9f'), ('LINE', 'af'), ('SPC(', 'df'),
          ('CMD', 'd7'), ('LIST', '93'), ('SPRITE', 'c7'), ('COLOR', 'bd'), ('LLIST', '9e'), ('CONT', '99'), ('LOAD', 'b5'),
          ('STEP', 'dc'), ('COPY', 'd6'), ('LOCATE', 'd8'), ('STOP', '90'), ('CSAVE', '9a'), ('CSRLIN', 'e8'),
          ('STRING$', 'e3'), ('LPRINT', '9d'), ('SWAP', 'a4'), ('LSET', 'b8'), ('TAB(', 'db'), ('MAX', 'cd'), ('DATA', '84'),
          ('MERGE', 'b6'), ('THEN', 'da'), ('TIME', 'cb'), ('TO', 'd9'), ('DEFDBL', 'ae'), ('DEFINT', 'ac'), ('DEFSTR', 'ab'),
          ('TROFF', 'a3'), ('DEFSNG', 'ad'), ('TRON', 'a2'), ('DEF', '97'), ('MOD', 'fb'), ('USING', 'e4'),
          ('DELETE', 'a8'), ('MOTOR', 'ce'), ('USR', 'dd'), ('DIM', '86'), ('NAME', 'd3'), ('DRAW', 'be'), ('NEW', '94'),
          ('VARPTR', 'e7'), ('NEXT', '83'), ('VDP', 'c8'), ('DSKI$', 'ea'), ('NOT', 'e0'), ('DSKO$', 'd1'), ('VPOKE', 'c6'),
          ('OFF', 'eb'), ('WAIT', '96'), ('END', '81'), ('ON', '95'), ('WIDTH', 'a0'), ('OPEN', 'b0'), ('XOR', 'f8'),
          ('EQV', 'f9'), ('OR', 'f7'), ('ERASE', 'a5'), ('OUT', '9c'), ('ERL', 'e1'), ('REM', '8f'),

          ('PDL', 'ffa4'), ('EXP', 'ff8b'), ('PEEK', 'ff97'), ('FIX', 'ffa1'), ('POS', 'ff91'), ('FPOS', 'ffa7'),
          ('ABS', 'ff86'), ('FRE', 'ff8f'), ('ASC', 'ff95'), ('ATN', 'ff8e'), ('HEX$', 'ff9b'), ('BIN$', 'ff9d'),
          ('INP', 'ff90'), ('RIGHT$', 'ff82'), ('RND', 'ff88'), ('INT', 'ff85'), ('CDBL', 'ffa0'), ('CHR$', 'ff96'),
          ('CINT', 'ff9e'), ('LEFT$', 'ff81'), ('SGN', 'ff84'), ('LEN', 'ff92'), ('SIN', 'ff89'), ('SPACE$', 'ff99'),
          ('SQR', 'ff87'), ('LOC(', 'ffac28'), ('STICK', 'ffa2'), ('COS', 'ff8c'), ('LOF', 'ffad'), ('STR$', 'ff93'),
          ('CSNG', 'ff9f'), ('LOG', 'ff8a'), ('STRIG', 'ffa3'), ('LPOS', 'ff9c'), ('CVD', 'ffaa'), ('CVI', 'ffa8'),
          ('CVS', 'ffa9'), ('TAN', 'ff8d'), ('MID$', 'ff83'), ('MKD$', 'ffb0'), ('MKI$', 'ffae'), ('MKS$', 'ffaf'),
          ('VAL', 'ff94'), ('DSKF', 'ffa6'), ('VPEEK', 'ff98'), ('OCT$', 'ff9a'), ('EOF', 'ffab'), ('PAD', 'ffa5'),

          ("'", '3a8fe6'), ('ELSE', '3aa1'), ('AS', '4153')]

JUMPS = ['RESTORE', 'AUTO', 'RENUM', 'DELETE', 'RESUME', 'ERL', 'ELSE', 'RUN', 'LIST', 'LLIST', 'GOTO', 'RETURN', 'THEN', 'GOSUB']


# Load file -------------------------------------------------------------------
def load_file(file_load, encoding='latin1'):
    '''Load the ASCII code.
       file_load = Name of the file
       encoding = File encoding format'''

    ascii_code = []
    if file_load:
        try:
            with open(file_load, 'r', encoding=encoding) as f:
                for line in f:
                    if line.strip() == "" or line.strip().isdigit():
                        continue
                    ascii_code.append(line.strip() + '\r\n')
        except IOError:
            Info.log(1, f'File not found: {file_load}')
    else:
        Info.log(1, 'File name not given.')

    return ascii_code


# Save file -------------------------------------------------------------------
def save_file(tokenized_code, file_save):
    '''Save the tokenized code
       tokenized_code = File to be saved
       file_save = File name'''

    try:
        with open(file_save, 'wb') as f:
            for line in tokenized_code:
                f.write(binascii.unhexlify(line))
    except IOError:
        Info.log(1, f'Save folder not found: {file_save}')


class Info():
    def log(lvl, desc, data=None, bullet=None, show_file=False):
        if data:
            data_pack = namedtuple('data_pack', 'lin col offset text file')
            data = data_pack(data[0], 0, 0, data[1], data[2])

        infolog.log(lvl, desc, data, bullet, show_file)


class Tokenize:
    '''Tokenize'''

    def __init__(self, stg):
        self.source = 0
        self.compiled = ''
        self.line_compiled = ''
        self.line_source = ''
        self.stg = stg

    def update_lines(self):
        if len(self.line_source) > 2:
            self.line_source = self.line_source[self.source:]
            self.line_compiled = self.line_compiled + self.compiled
            self.show_steps()

    def parse_numeric_bases(self, log_data, line_number, nugget_comp, token, base):
        if not nugget_comp:
            nugget_comp = ''
            hexa = '0000'
        else:
            if int(nugget_comp, base) > 65535:
                Info.log(1, f'Number overflow: {nugget_comp}', log_data)
            hexa = '{0:04x}'.format(int(nugget_comp, base))
        return token + hexa[2:] + hexa[:-2]

    def parse_sgn_dbl(self, header, precision, nugget_integer, nugget_fractional, nugget_group_1_orig, nugget_number):
        nugget_stripped = nugget_integer.lstrip('0')
        if nugget_stripped == '':
            if nugget_fractional == '' or int(str(nugget_fractional[1:]) + '0') == 0:
                nugget_stripped = '0'
                hexa_precision = '00'
            else:
                nugget_integer = nugget_group_1_orig
                if str(nugget_fractional[1]) == '0':
                    nugget_zeros = nugget_fractional[1:].rstrip('0')
                    hexa_precision = '{0:02x}'.format(64 - (len(nugget_zeros) - len(nugget_zeros.lstrip('0'))))
                else:
                    hexa_precision = '40'
        else:
            hexa_precision = '{0:02x}'.format(len(nugget_stripped) + 64)
        hexa = header + hexa_precision
        cropped = str(int(nugget_number))
        round_digit = int(cropped[precision:precision + 1]) if cropped[precision:precision + 1].isdigit() else 0
        nugget_cropped = cropped[0:precision] if round_digit < 5 else str(int(cropped[:precision]) + 1)
        hexa += nugget_cropped

        return hexa, nugget_integer

    def show_steps(self):
        Info.log(5, f'{self.line_compiled} | {self.line_source.rstrip()}')

    def make_list_line(self, base_prev, line_base):
        line_inc = 12
        line_temp = []
        next_addr = str(self.line_compiled[0:4])
        curr_line = str(self.line_compiled[4:8])
        line_byte = str(self.line_compiled[8:])
        line_splt = [line_byte[i:i + self.stg.width_byte] for i in range(0, len(line_byte), self.stg.width_byte)]
        for line in line_splt:
            curr_addr = str(hex(base_prev)[2:][:-2]) + str(hex(base_prev)[2:][2:])

            byte_splt = ' '.join([line[i:i + 2] for i in range(0, len(line), 2)])

            line_list = curr_addr + ': ' + next_addr + ' ' + curr_line + ' ' \
                + byte_splt + (' ' * (self.stg.width_line - len(byte_splt))) + line_base.rstrip()

            line_temp.append(line_list)
            next_addr, curr_line, line_base = '        ', '', ''
            base_prev += line_inc
            line_inc = len(line) // 2

        return line_temp

    def tok(self, ascii_code):
        line_address = BASE
        line_order = 0
        line_number = 0
        list_core = []
        tokenized_code = ['ff']

        for n, self.line_source in enumerate(ascii_code, 1):
            log_data = (n, self.line_source, self.stg.file_load)

            line_base = self.line_source
            self.line_compiled = ''

            if self.line_source == '':
                continue

            if ord(self.line_source[0]) < 48 or ord(self.line_source[0]) > 57:
                if ord(self.line_source[0]) == 26:  # Avoid '' on last line of some listings
                    continue
                else:
                    Info.log(1, f'Line not starting with number.', log_data)

            self.show_steps()

            # Get line number
            nugget = re.match(r'\s*\d+\s?', self.line_source).group()
            line_number = nugget.strip()
            if int(line_number) <= line_order:
                Info.log(1, f'Line number out of order: {line_number}', log_data)
            if int(line_number) > 65529:
                Info.log(1, f'Line number too high: {line_number}', log_data)
            line_order = int(line_number)
            self.line_source = self.line_source[len(nugget):]
            hexa = '{0:04x}'.format(int(nugget))
            self.line_compiled += hexa[2:] + hexa[:-2]

            self.show_steps()

            # Look for instructions
            while len(self.line_source) > 2:
                for command, token in TOKENS:
                    if self.line_source.upper().startswith(command):
                        self.compiled = token
                        self.source = len(command)
                        self.update_lines()

                        if command == 'AS':
                            nugget = re.match(r'(\s*)(\d{1,2})', self.line_source)
                            if nugget:
                                nugget_spaces = nugget.group(1)
                                nugget_line = nugget.group(2)
                                hex_spaces = '20' * len(nugget_spaces)
                                hexa = '{0:02x}'.format(ord(nugget_line))
                                self.compiled = hex_spaces + hexa
                                self.source = len(nugget_spaces) + len(nugget_line)
                                self.update_lines()

                        # Is a jumping instructions
                        if command in JUMPS:
                            while True:
                                nugget = re.match(r'(\s*)(\d+|,+)', self.line_source)
                                if nugget:
                                    nugget_spaces = nugget.group(1)
                                    nugget_line = nugget.group(2)
                                    if nugget_line.isdigit():
                                        if int(nugget_line) > 65529:
                                            Info.log(1, f'Line number jump too high: {nugget_line}', log_data)
                                        hex_spaces = '20' * len(nugget_spaces)
                                        hexa = '{0:04x}'.format(int(nugget_line))
                                        self.compiled = hex_spaces + '0e' + hexa[2:] + hexa[:-2]
                                        self.source = len(nugget_spaces) + len(nugget_line)
                                        self.update_lines()
                                    # Has several jumps (on goto/gosub)
                                    else:
                                        hex_spaces = '20' * len(nugget_spaces)
                                        hexa = '2c' * len(nugget_line)
                                        self.compiled = hex_spaces + hexa
                                        self.source = len(nugget_spaces) + len(nugget_line)
                                        self.update_lines()
                                else:
                                    break

                        # Instruction with literal data after it
                        if command == 'DATA' or command == 'REM' or command == "'" or command == 'CALL' or command == '_':
                            while True:
                                character = self.line_source[0]
                                if command == 'CALL' or command == '_':
                                    character = character.upper()
                                hexa = '{0:02x}'.format(ord(character))
                                self.compiled = hexa
                                self.source = 1
                                self.update_lines()

                                if len(self.line_source) <= 2 \
                                        or (command == 'DATA' and self.line_source[0] == ':') \
                                        or (command == '_' and (self.line_source[0] == ':' or self.line_source[0] == '('))\
                                        or (command == 'CALL' and (self.line_source[0] == ':' or self.line_source[0] == '(')):
                                    break
                        break

                # Look each character
                else:
                    # Is a number
                    is_int = False
                    nugget = self.line_source[0].upper()
                    if nugget.isdigit() or nugget == '.':
                        nugget = re.match(r'(\d*)\s*(.)\s*(.?)', self.line_source)
                        nugget_number = nugget.group(1)
                        nugget_integer = nugget.group(1)
                        nugget_fractional = ''
                        nugget_signal = nugget.group(2)
                        nugget_notif_confirm = nugget.group(3)

                        # Is floating point
                        if nugget_signal == '.':
                            nugget = re.match(r'(\d*)\s*(.)\s*(\d*)\s*(.)\s*(.?)', self.line_source)
                            nugget_group1 = '0' if nugget.group(1) == '' else nugget.group(1)
                            nugget_number = nugget_group1 + nugget.group(3)
                            nugget_integer = nugget_group1
                            nugget_fractional = '.' + nugget.group(3)
                            nugget_signal = nugget.group(4)
                            nugget_notif_confirm = nugget.group(5)

                        # Has integer signal
                        if nugget_signal == '%':
                            nugget_number = nugget_integer
                            is_int = True
                            if int(nugget_number) >= 32768:
                                Info.log(1, f'Integer overflow: {nugget_number}', log_data)
                        elif nugget_signal != '%' and nugget_signal != '!' and nugget_signal != '#' and \
                                ((nugget_signal.lower() != 'e' and nugget_signal.lower() != 'd')
                                 or (nugget_notif_confirm != '-' and nugget_notif_confirm != '+')):
                            nugget_signal = ''
                            if nugget_fractional == '':
                                is_int = True

                        # Is scientific notation
                        if (nugget_signal.lower() == 'e' or nugget_signal.lower() == 'd') \
                                and (nugget_notif_confirm == '-' or nugget_notif_confirm == '+'):  # Avoid matching E from ELSE after a number
                            exp = re.match(r'\d*\s*.\s*\d*\s*.\s*(\+|-)\s*(\d+)', self.line_source)

                            nugget_exp_size = len(nugget_integer.lstrip('0')) + int(exp.group(1) + exp.group(2))
                            nugget_man_size = nugget_exp_size - len(nugget_fractional[1:]) - len(nugget_integer.lstrip('0'))

                            if nugget_exp_size > 63 or nugget_exp_size < -64:
                                Info.log(1, f'Float overflow: {nugget_number}', log_data)

                            fractional = abs(nugget_man_size) if nugget_man_size < 0 else 0
                            notation = '%.*f' % (fractional, int(nugget_number) * (10 ** (nugget_man_size)))
                            notation_parts = re.match(r'(\d+)(\.\d+)?', notation)
                            notation_integer = notation_parts.group(1)
                            notation_fractional = notation_parts.group(2) if notation_parts.group(2) else ''
                            notation_number = notation.replace('.', '')
                            notation_size = nugget_number.lstrip('0')

                            if nugget_signal.lower() == 'e' and len(notation_size) < 7:
                                hexa, _ = self.parse_sgn_dbl('1d', 6, notation_integer, notation_fractional,
                                                             nugget.group(1), notation_number)
                                hexa += '0' * (10 - len(hexa))
                            else:
                                hexa, _ = self.parse_sgn_dbl('1f', 14, notation_integer, notation_fractional,
                                                             nugget.group(1), notation_number)
                                hexa += '0' * (18 - len(hexa))
                                hexa = hexa[0:18]

                            nugget_integer = nugget.group(1) if nugget_integer.lstrip('0') == '' else nugget_integer
                            nugget_signal += exp.group(1) + exp.group(2)

                        # Is single precision
                        elif (int(nugget_number) >= 32768 and int(nugget_number) <= 999999 and nugget_signal != '#') \
                                or (nugget_signal == '!' and int(nugget_number) <= (10 ** 63 - 1)) \
                                or (not is_int and int(nugget_number) <= 999999 and nugget_signal != '#'):

                            hexa, nugget_integer = self.parse_sgn_dbl('1d', 6, nugget_integer, nugget_fractional,
                                                                      nugget.group(1), nugget_number)
                            hexa += '0' * (10 - len(hexa))

                        # Is double precision
                        elif (int(nugget_number) >= 1000000 and int(nugget_number) <= (10 ** 63 - 1)) \
                                or (nugget_signal == '#' and int(nugget_number) <= (10 ** 63 - 1)) \
                                or (not is_int and int(nugget_number) <= (10 ** 63 - 1)):

                            hexa, nugget_integer = self.parse_sgn_dbl('1f', 14, nugget_integer, nugget_fractional,
                                                                      nugget.group(1), nugget_number)
                            hexa += '0' * (18 - len(hexa))
                            hexa = hexa[0:18]

                        # Is normal integer
                        elif int(nugget_number) >= 0 and int(nugget_number) <= 9:
                            nugget_add = str(int(nugget_number) + 17)
                            hexa = '{0:02x}'.format(int(nugget_add))

                        elif int(nugget_number) >= 10 and int(nugget_number) <= 255:
                            hexa = '0f' + '{0:02x}'.format(int(nugget_number))

                        elif int(nugget_number) >= 256 and int(nugget_number) <= 32767:
                            hexa = '{0:04x}'.format(int(nugget_number))
                            hexa = '1c' + hexa[2:] + hexa[:-2]

                        else:
                            Info.log(1, f'Number too high: {nugget_number.lstrip("0")}', log_data)

                        self.compiled = hexa
                        self.source = len(nugget_integer) + len(nugget_fractional) + len(nugget_signal)
                        self.update_lines()

                    # Other bases
                    elif nugget == '&':
                        nugget = self.line_source[0:2].upper()
                        if nugget == '&H':
                            nugget_comp = re.match(r'[0-9a-f]*', self.line_source[2:].lower()).group()
                            hexa = self.parse_numeric_bases(log_data, line_number, nugget_comp, '0c', 16)
                        elif nugget == '&O':
                            nugget_comp = re.match(r'[0-7]*', self.line_source[2:]).group()
                            hexa = self.parse_numeric_bases(log_data, line_number, nugget_comp, '0b', 8)
                        elif nugget == '&B':
                            nugget_comp = re.match(r'[01]*', self.line_source[2:]).group()
                            hexa = '2642'
                            if nugget_comp:
                                for character in nugget_comp:
                                    hexa += '{0:02x}'.format(ord(character))
                            else:
                                nugget_comp = ''
                        else:
                            nugget = '&'
                            hexa = '{0:02x}'.format(ord(nugget))
                            nugget_comp = ''
                        self.compiled = hexa
                        self.source = len(nugget) + len(nugget_comp)
                        self.update_lines()

                    # Quotes
                    else:
                        nugget = self.line_source[0].upper()
                        if nugget == '"':
                            num_quotes = 0
                            while True:
                                if self.line_source[0] == '"':
                                    num_quotes += 1
                                hexa = '{0:02x}'.format(ord(self.line_source[0]))
                                self.compiled = hexa
                                self.source = 1
                                self.update_lines()
                                if num_quotes > 1 or len(self.line_source) <= 2:
                                    break
                        # And the rest
                        else:
                            if ord(nugget) >= 65 and ord(nugget) <= 90:
                                is_var = True
                                while True:
                                    nugget = self.line_source[0].upper()
                                    for command, token in TOKENS:
                                        if self.line_source.upper().startswith(command):
                                            is_var = False
                                    if (ord(nugget) < 48 or ord(nugget) > 57) \
                                            and (ord(nugget) < 65 or ord(nugget) > 90) \
                                            or not is_var:
                                        is_var = False
                                        break
                                    hexa = '{0:02x}'.format(ord(nugget.upper()))
                                    self.compiled = hexa
                                    self.source = 1
                                    self.update_lines()
                            else:
                                self.compiled = '{0:02x}'.format(ord(nugget.upper()))
                                self.source = 1
                                self.update_lines()

            base_prev = line_address
            line_address += (len(self.line_compiled) + 6) // 2
            hexa = '{0:04x}'.format(line_address)
            self.line_compiled = hexa[2:] + hexa[:-2] + self.line_compiled
            self.line_compiled += '00'
            tokenized_code.append(self.line_compiled)

            if self.stg.export_list:
                list_core.extend(self.make_list_line(base_prev, line_base))

        tokenized_code.append('0000')

        list_data = namedtuple('list_data', 'core hexa adrs line')
        return tokenized_code, list_data(list_core, hexa, line_address, len(ascii_code))


def save_list(stg, list_data):
    list_code = ["' -------------------------------------",
                 "' MSX Basic Tokenizer: " + '"' + os.path.basename(stg.file_load) + '"',
                 "' Date: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                 "' -------------------------------------", ""]
    list_code.append(hex(BASE - 1)[2:] + ': ' + 'ff' + (' ' * (stg.width_line + 8)) + 'start')

    list_code.extend(list_data.core)

    list_code.append(str(list_data.hexa) + ': 0000' + (' ' * (stg.width_line + 6)) + 'end')

    list_code.extend(["", "' -------------------------------------",
                          "' Statistics",
                          "' -------------------------------------", ""])
    list_code.append('lines ' + str(list_data.line))
    list_code.append('start &h' + '{0:04x}'.format(BASE - 1) + ' | ' + str(BASE - 1))
    list_code.append('end   &h' + '{0:04x}'.format(list_data.adrs + 1) + ' | ' + str(list_data.adrs + 1))
    list_code.append('size  &h' + '{0:04x}'.format((list_data.adrs - BASE) + 3) + ' | ' + str((list_data.adrs - BASE) + 3))

    try:
        with open(stg.file_list, 'w', encoding='latin1') as f:
            for line in list_code:
                try:
                    f.write(line + '\n')
                except UnicodeEncodeError as e:
                    Info.log(1, f'Saving encode error: {str(e)}\n'
                                f'    {stg.file_list}')
    except IOError:
        Info.log(1, f'Save folder not found: {stg.file_list}')


# Main class ------------------------------------------------------------------
class Main:
    def __init__(self):
        self.stg = Settings()

    def execute(self):

        Info.log(3, f'MSX Basic Tokenizer', bullet='')
        Info.log(3, f'Tokenizing: {os.path.basename(self.stg.file_load)}', bullet='')

        # Load ASCII code ---------------------------------------------------------
        Info.log(3, f'Loading file: {self.stg.file_load}')
        ascii_code = load_file(self.stg.file_load)

        # Tokenize it -------------------------------------------------------------
        Info.log(3, 'Tokenizing.')

        tok = Tokenize(self.stg)
        tokenized, list_data = tok.tok(ascii_code)

        # Save tokenized code -----------------------------------------------------
        Info.log(1, f'Saving file: {self.stg.file_save}', bullet='    ')
        save_file(tokenized, self.stg.file_save)

        # Save list ---------------------------------------------------------------
        if self.stg.export_list:
            Info.log(1, f'Saving file: {self.stg.file_list}', bullet='    ')
            save_list(self.stg, list_data)

        # Delete ASCII code -------------------------------------------------------
        if self.stg.delete_original:
            if os.path.isfile(self.stg.file_save):
                Info.log(1, f'Deleting file: {self.stg.file_load}', bullet='    ')
                time.sleep(0.5)
                osremove(self.stg.file_load)
            else:
                Info.log(2, None, f'Converted not found: {self.stg.file_save}')
                Info.log(2, None, f'Source not deleted: {self.stg.file_load}')


# Main function ---------------------------------------------------------------
def main():
    '''Do the thing'''

    tok_main = Main()
    tok_main.stg.init()
    infolog.level = tok_main.stg.verbose_level
    tok_main.execute()


if __name__ == '__main__':
    main()
