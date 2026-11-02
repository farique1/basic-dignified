import argparse
import re
from collections import namedtuple

from msx.badig_msx import Description as MSXDescription
from msx.badig_msx import Info
from msx.badig_msx import Lexer as MSXLexer
from msx.badig_msx import Parser as MSXParser


class Description(MSXDescription):
    def sysinfo(self):
        self.system_name = 'Sinclair ZX-81'
        self.dignified_ext = '.DZX'
        self.ascii_ext = '.AZX'
        self.binary_ext = '.p'

    def __init__(self):
        super().__init__()

        c_instrc = ['COPY', 'CLEAR', 'UNPLOT', 'CLS', 'IF', 'RANDOMIZE', 'RAND',
                    'SAVE', 'RUN', 'PLOT', 'PRINT', 'POKE', 'NEXT', 'PAUSE',
                    'LET', 'LIST', 'LOAD', 'INPUT', 'FOR', 'TO', 'DIM',
                    'CONTINUE', 'CONT', 'SCROLL', 'NEW', 'FAST', 'SLOW', 'STOP',
                    'LLIST', 'LPRINT']
        c_funcdl = [r'CHR\$', r'STR\$', r'INKEY\$']
        c_funcnm = ['USR', 'PEEK', 'ABS', 'SGN', 'SQR', 'INT', 'EXP', 'LN',
                    'ATN', 'ACS', 'ASN', 'TAN', 'COS', 'SIN', 'LEN', 'VAL',
                    'CODE', 'TAB', 'AT', 'PI', 'RND']
        c_jumpin = ['GOTO', 'GOSUB', 'RETURN', 'THEN']
        c_operat = ['AND', 'OR', 'NOT']
        c_symbol = [r'<>', r'>=', r'<=', r'\*\*', '>', '=', '<', r'\+', r'\*',
                r'/', '-', r',', r'\(', r'\)', r';', r'\?', r'\#', r'\\']
        c_e_symb = [r'\+\+', '--', r'\+=', r'-=', r'\*=', '/=', r'\^=']

        self.c_replacements = {}
        self.c_original = ''
        self.c_translat = ''
        self.c_symb_comp = [s.replace('\\', '') for s in c_symbol] + [':', '_']
        self.c_reserved_kw = c_instrc + c_jumpin + c_funcdl + c_funcnm + c_operat + ['REM']
        self.c_reserved_kw = [keyword.replace('\\', '') for keyword in self.c_reserved_kw]
        self.c_quotes = '"'
        self.c_altrem = 'REM'
        self.c_lab_rep_rem = ' REM'
        self.c_print_ins = 'print'
        self.c_print_alt = '?'
        self.c_varsna = r'^[a-zA-Z]$'
        self.c_var_chr = 'abcdefghijklmnopqrstuvwxyz'
        self.c_var_num = '0123456789'
        self.c_idnttp_grp = r'^([a-zA-Z][a-zA-Z_0-9]*)([$]?)$'
        self.c_var_valid_chars = 1
        self.c_var_max = 26
        self.c_var_mod = 26
        self.c_instsp_str = ':'
        self.c_loop_back = 'goto'
        self.c_func_call = 'gosub'
        self.c_func_ret = 'return'
        self.c_func_stop_kw = c_instrc + c_jumpin + [keyword.replace('\\', '')
                                   for keyword in c_funcdl] + c_funcnm

        c_numdec = r'(^([+-]?)((\d*\.?)?\d+)((E)(\+|-)?\d+)?$)'
        c_litquo = r'(^"$)'
        c_linrem = r'(^REM$)'
        c_instsp = r'(^:$)'

        clc_func = fr"(?P<c_functs>{self.join_commands(c_funcnm, c_funcdl)})"
        clc_symb = fr"(?P<c_symbol>{self.join_commands(c_symbol)})"
        clc_esym = fr"(?P<c_e_symb>{self.join_commands(c_e_symb)})"
        clc_oper = fr"(?P<c_operat>{self.join_commands(c_operat)})"
        clc_jump = fr"(?P<c_jumpin>{self.join_commands(c_jumpin)})"
        clc_inst = fr"(?P<c_instrc>{self.join_commands(c_instrc)})"
        clc_part = r'(?P<c_partls>(?!))'
        clc_lrem = fr'(?P<c_linrem>{c_linrem})'
        clc_insp = fr'(?P<c_instsp>{c_instsp})'
        clc_litr = fr'(?P<c_quotes>{c_litquo})'
        clc_numb = fr'(?P<c_number>{c_numdec})'

        self.classic_groups = (''
                               rf'{clc_oper}|'
                               rf'{clc_symb}|'
                               rf'{clc_esym}|'
                               rf'{clc_func}|'
                               rf'{clc_jump}|'
                               rf'{clc_inst}|'
                               rf'{clc_numb}|'
                               rf'{clc_lrem}|'
                               rf'{clc_part}|'
                               rf'{clc_insp}|'
                               rf'{clc_litr}')


class Settings:
    def properties(self, stg):
        self.convert_print = None
        self.strip_then_goto = ''
        return self


class Expose:
    def __init__(self):
        self.remtags = {}
        self.parser = argparse.ArgumentParser(add_help=False)


class Lexer(MSXLexer):
    def quoted_string(self, token_type, end, part, position):
        source = self.lex
        part += source.advance()

        while True:
            current_char = source.advance()
            if current_char is None:
                break

            part += current_char
            if current_char == '\\' and source.lookahead() == end:
                part += source.advance()
                continue

            if current_char == end:
                if source.lookahead() == end:
                    part += source.advance()
                    continue
                break

            if re.match(source.des.newline, source.lookahead()):
                break

        return self.Tok(tok=token_type, val=part, pos=position)


class Parser(MSXParser):
    def initialization(self):
        position = self.par.tk.pos.copy()
        marker_start = self.Tok(tok='D_SPCIAL', val='?', pos=position.copy())
        variable = self.Tok(tok='D_DEFVAR', val='var', pos=position.copy())
        marker_end = self.Tok(tok='D_SPCIAL', val='??', pos=position.copy())
        default_row = self.par.tok_str('0', pos=position.copy())[0]
        default_column = self.par.tok_str('0', pos=position.copy())[0]
        comma = self.par.tok_str(',', pos=position.copy())[0]
        define_group = namedtuple('define_group', 'repl varv')
        print_at_define = {
            '?': (define_group([marker_start, variable, marker_end],
                               [default_row, comma, default_column]))
        }
        self.des.d_defines = {**self.des.d_defines, **print_at_define}

    def replace_print_at(self):
        position = self.par.tk.pos.copy()
        coordinates = [[]]
        nesting = 0

        while True:
            token = self.par.next_tok()
            if token.tok == 'D_SPCIAL' and token.val == '??':
                self.par.next_tok()
                break

            if token.val == '(':
                nesting += 1
            elif token.val == ')' and nesting:
                nesting -= 1
            elif token.tok == 'C_SYMBOL' and token.val == ',' and nesting == 0:
                if len(coordinates) == 1:
                    coordinates.append([])
                    continue

            coordinates[-1].append(token)

        if not coordinates[0]:
            coordinates[0] = self.par.tok_str('0', pos=position.copy())
        if len(coordinates) == 1 or not coordinates[1]:
            coordinates.append(self.par.tok_str('0', pos=position.copy()))

        output = self.par.tok_str('print at', pos=position.copy())
        output.extend(coordinates[0])
        output.extend(self.par.tok_str(',', pos=position.copy()))
        output.extend(coordinates[1])
        output.extend(self.par.tok_str(';', pos=position.copy()))
        self.par.tok_list_out.extend(output)

    def pass_2(self):
        if self.par.tk.tok == 'D_SPCIAL' and self.par.tk.val == '?':
            self.replace_print_at()
        return False

    def process_variable(self, token):
        variable_name = token.var_name
        if len(variable_name) <= self.des.c_var_valid_chars:
            return token

        for kept_variable in self.des.c_hard_long_vars:
            if variable_name == kept_variable.var_name \
                    and token.pos.file == kept_variable.pos.file:
                Info.log(1, 'ZX-81 variables must be one letter, optionally followed by $.',
                         token)

        variable_key = token.val_w_file
        if variable_key in self.des.d_declares:
            token.val = self.des.d_declares[variable_key] + token.var_type
            return token

        used_variables = set(self.des.c_hard_short_vars)
        used_variables.update(self.des.d_declares.values())
        used_variables.update(variable.var_name for variable in self.des.c_hard_long_vars)

        for short_variable in reversed(self.des.c_var_chr):
            if short_variable not in used_variables:
                self.des.d_declares[variable_key] = short_variable
                token.val = short_variable + token.var_type
                return token

        Info.log(1, 'Too many variables used (max=26).', token)

    def generate(self):
        if self.par.n > 0:
            previous = self.par.line[self.par.n - 1]
            current = self.par.token
            previous_is_keyword = previous.uval in self.des.c_reserved_kw
            current_is_keyword = current.uval in self.des.c_reserved_kw
            needs_space = previous.tok == 'C_LINENB' \
                or (previous_is_keyword and current.val not in self.des.c_symb_comp) \
                or (current_is_keyword and previous.val not in self.des.c_symb_comp) \
                or current.val == '**' \
                or previous.val == '**' \
                or (current.tok == 'C_LITREM' and previous.tok == 'C_LINREM') \
                or (current.tok == 'C_LINREM' and previous.tok == 'C_LINREM')
            if needs_space and not self.par.c_line.endswith(' '):
                self.par.c_line += ' '
        return False