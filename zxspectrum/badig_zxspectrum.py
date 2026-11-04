"""Sinclair BASIC 48K dialect and Dignified transformations."""

import argparse
import re
from collections import namedtuple

from msx.badig_msx import Description as MSXDescription
from msx.badig_msx import Info
from msx.badig_msx import Lexer as MSXLexer
from msx.badig_msx import Parser as MSXParser
from . import VERSION
from .tokenizer_zxspectrum import (
    FUNCTIONS, SpectrumTokenizeError, TOKEN_CODES, tokenize, validate_identifier,
)


def fail(message, token=None):
    Info.log(1, message, token, bullet='*** ')
    raise SystemExit(1)


def postprocess(code, stg):
    try:
        tokenize(''.join(code))
    except SpectrumTokenizeError as error:
        fail(str(error))
    return code


class Description(MSXDescription):
    def sysinfo(self):
        self.system_name = f'ZX Spectrum 48K (module {VERSION} preview)'
        self.dignified_ext = '.DSP'
        self.ascii_ext = '.ASP'
        self.binary_ext = '.tap'

    def __init__(self):
        super().__init__()
        instructions = ['PRINT', 'LET', 'IF', 'CLS', 'STOP', 'BORDER', 'INK',
                        'PAPER', 'PAUSE', 'BEEP', 'INPUT', 'RETURN', 'FOR', 'NEXT',
                        'TO', 'STEP', 'DIM', 'DATA', 'READ', 'RESTORE', 'RANDOMIZE',
                        'AT', 'TAB', 'FLASH', 'BRIGHT', 'INVERSE', 'OVER',
                        'PLOT', 'DRAW', 'CIRCLE', 'POKE', 'CLEAR', '?']
        jumps = ['GOTO', 'GO TO', 'GOSUB', 'GO SUB', 'THEN']
        operators = ['AND', 'OR', 'NOT']
        symbols = ['<=', '>=', '<>', '>', '=', '<', '+', '*', '/', '^',
                   '-', ',', '(', ')', ';', "'", '#']
        self.c_reserved_kw = instructions + jumps + operators + list(FUNCTIONS) + ['REM']
        self.c_quotes = '"'
        self.c_altrem = 'REM'
        self.c_lab_rep_rem = ' : REM '
        self.c_lit_toks = ['C_LITREM', 'C_LIBREM', 'C_LITQUO']
        self.c_replacements = {}
        self.c_original = ''
        self.c_translat = ''
        self.c_symb_comp = symbols + [':', '_']
        self.c_varsna = r'^[a-zA-Z]$'
        self.c_idnttp_grp = r'^([a-zA-Z][a-zA-Z_0-9]*)([%!#$]?)$'
        self.c_var_valid_chars = 1
        self.c_loop_back = 'GOTO'
        self.c_func_stop_kw = self.c_reserved_kw

        number = r'(?:\d+(?:\.\d*)?|\.\d+)(?:E[+-]?\d+)?'
        groups = [
            ('c_operat', self.join_commands(operators)),
            ('c_symbol', self.join_commands([re.escape(s) for s in symbols])),
            ('c_jumpin', self.join_commands(['GOTO', 'GO +TO', 'GOSUB', 'GO +SUB', 'THEN'])),
            ('c_instrc', self.join_commands([re.escape(word) for word in instructions])),
            ('c_e_symb', r'^(?:\+\+|--|\+=|-=|\*=|/=|\^=)$'),
            ('c_functs', self.join_commands([re.escape(word) for word in FUNCTIONS])),
            ('c_number', f'^{number}$'),
            ('c_linrem', '^REM$'),
            ('c_partls', r'^(?:GO(?: +(?:T|S|SU)?)?|\d+(?:\.\d*)?E[+-]?|\.)$'),
            ('c_instsp', '^:$'),
            ('c_quotes', '^"$'),
        ]
        self.classic_groups = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in groups)


class Settings:
    def properties(self, stg):
        if not 1 <= stg.line_start <= 9999 or stg.line_step < 1:
            fail('Spectrum requires line start 1..9999 and a positive line step')
        return self


class Expose:
    def __init__(self):
        self.remtags = {}
        self.parser = argparse.ArgumentParser(add_help=False)
        self.parser.add_argument('--spectrum-version', action='version',
                                 version=f'ZX Spectrum module {VERSION}')


class Lexer(MSXLexer):
    def lexing(self):
        tk = self.lex.tk
        if tk.tok == 'D_IDNTTP' and tk.val == 'PROGRAM' \
                and tk.pos.lin >= self.pos.code_len - 1:
            return None
        return False

    def quoted_string(self, token_type, end, part, position):
        part += self.lex.advance()
        while self.lex.lookahead() != self.des.newline_str:
            char = self.lex.advance()
            part += char
            if char == end:
                if self.lex.lookahead() == end:
                    part += self.lex.advance()
                    continue
                return self.Tok(tok=token_type, val=part, pos=position)
        fail('Unterminated Spectrum string', self.lex.tk)


class Parser(MSXParser):
    def initialization(self):
        replacement = self.par.tok_str('PRINT AT VAR;')
        replacement[2].tok = 'D_DEFVAR'
        definition = namedtuple('def_grp', 'repl varv')
        self.des.d_defines['?'] = definition(replacement, self.par.tok_str('0,0'))

    def pass_1(self):
        return False

    def pass_2(self):
        return False

    def pass_3(self):
        return False

    def pass_4(self):
        tk = self.par.tk
        if tk.tok == 'D_IDNTTP':
            if self.par.last_tok().val == '~':
                self.par.tok_list_out.pop()
            if tk.val_w_file in self.des.d_declares:
                tk.val = self.des.d_declares[tk.val_w_file] + tk.var_type
            try:
                validate_identifier(tk.val, array=self.par.peek_ahead().val == '(',
                                    for_control=self.par.last_tok().uval in ('FOR', 'NEXT'))
            except SpectrumTokenizeError as error:
                fail(str(error), tk)
            if tk.uval in TOKEN_CODES:
                fail(f'{tk.val} is reserved by Sinclair BASIC', tk)
        return False

    def pass_5(self):
        tk = self.par.tk
        previous = self.par.last_tok()
        if tk.tok == 'D_IDNTTP' and (
                previous.tok in ('C_LINENB', 'C_INSTSP') or previous.uval == 'THEN'):
            self.par.tok_list_out.extend(self.par.tok_str('LET'))
        if tk.tok == 'C_E_SYMB':
            operand = previous
            if operand.tok != 'D_IDNTTP' or self.par.last_tok(-2).uval != 'LET':
                fail('Compound assignment requires a scalar LET target', tk)
            operation = tk.val
            if operand.var_type and operation != '+=':
                fail('Strings support only += compound assignment', tk)
            rhs = []
            while self.par.peek_ahead().tok not in ('NEWLINE', 'EOF', 'C_INSTSP'):
                rhs.append(self.par.next_tok())
            if operation in ('++', '--'):
                if rhs or operand.var_type:
                    fail('Increment/decrement requires a numeric scalar and no right operand', tk)
                rhs = self.par.tok_str('1')
            elif not rhs:
                fail('Compound assignment requires a right operand', tk)
            if any(token.tok == 'C_E_SYMB' for token in rhs):
                fail('Nested compound assignments are not supported', tk)
            self.par.tok_list_out.extend(self.par.tok_str('='))
            self.par.tok_list_out.append(operand.copy())
            self.par.tok_list_out.extend(self.par.tok_str(operation[0] + '('))
            for token in rhs:
                if token.tok == 'D_OPERAT':
                    token.val = '1' if token.uval == 'TRUE' else '0'
                    token.tok = 'C_NUMBER'
                elif token.uval in self.des.c_reserved_kw:
                    token.val = token.uval
                if self.stg.capitalise_all and token.tok not in self.des.c_lit_toks:
                    token.val = token.uval
                self.par.tok_list_out.append(token)
            self.par.tok_list_out.extend(self.par.tok_str(')'))
            return None
        if tk.tok == 'D_OPERAT':
            tk.tok = 'C_NUMBER'
            tk.val = '1' if tk.uval == 'TRUE' else '0'
        elif tk.tok == 'C_INSTRC' and tk.val == '?':
            tk.val = 'PRINT'
        elif tk.tok == 'C_JUMPIN' and re.fullmatch(r'GO\s*TO', tk.uval):
            tk.val = 'GO TO'
        elif tk.tok == 'C_JUMPIN' and re.fullmatch(r'GO\s*SUB', tk.uval):
            tk.val = 'GO SUB'
        elif tk.uval in self.des.c_reserved_kw:
            tk.val = tk.uval
        return False

    def generate(self):
        token = self.par.token
        if token.tok == 'C_LINENB' and not 1 <= int(token.val) <= 9999:
            fail('Spectrum line number exceeds 9999; reduce -ls or -lp', token)
        if self.par.n > 0:
            previous = self.par.line[self.par.n - 1]
            need_space = previous.tok == 'C_LINENB' \
                or (previous.uval in self.des.c_reserved_kw
                    and token.val not in self.des.c_symb_comp) \
                or (token.uval in self.des.c_reserved_kw
                    and previous.val not in self.des.c_symb_comp)
            if need_space and not self.par.c_line.endswith(' '):
                self.par.c_line += ' '
        return False
