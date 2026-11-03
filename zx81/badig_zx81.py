import argparse
import re
from collections import namedtuple

from msx.badig_msx import Description as MSXDescription
from msx.badig_msx import Info
from msx.badig_msx import Lexer as MSXLexer
from msx.badig_msx import Parser as MSXParser
from .tokenizer_zx81 import HEX_ESCAPE_MATCH
from .tokenizer_zx81 import REMX_IGNORE
from .tokenizer_zx81 import REMX_MATCH
from .tokenizer_zx81 import ZX81TokenizeError
from .tokenizer_zx81 import parse_remx


NUMBERED_LINE_MATCH = re.compile(r'^\s*(\d+)\s?(.*?)\s*$')
JUMP_MATCH = re.compile(r'(?i)(?<![A-Za-z0-9$])(?:GO\s*TO|GO\s*SUB|RUN|LLIST|LIST)(?![A-Za-z])')
REM_MATCH = re.compile(r'(?i)(?<![A-Za-z0-9$])REM(?![A-Za-z0-9])')


def _byte_text(code):
    '''Readable text for a ZX-81 byte inside a REM, or its \\{XX} escape'''
    if 28 <= code <= 37:
        return chr(code + 20)
    if 38 <= code <= 63:
        return chr(code + 59).upper()
    return f'\\{{{code:02X}}}'


def remx_line(arguments, line):
    '''Build the numbered REM line for remx <line>,<count>[,<byte>]'''
    try:
        number, count, code = parse_remx(arguments, line.nmbr)
    except ZX81TokenizeError as error:
        Info.log(1, f'{error}: {line.text.strip()}')
    return number, f'{number} REM {_byte_text(code) * count}'


def preprocess(d_code, stg):
    '''Take remx lines out of the code and convert numbered listings'''
    stg.remx_lines = []
    code = [d_code[0]]
    for line in d_code[1:]:
        remx = REMX_MATCH.match(line.text)
        if remx:
            stg.remx_lines.append(remx_line(remx.group(1), line))
            line = line._replace(text='\n')
        code.append(line)

    if stg.code_is_numbered:
        Info.log(4, 'Numbered listing: converting line numbers to labels.')
        code = dignify_numbered(code)
    return code


def postprocess(c_code, stg):
    '''Insert the remx REM lines into the generated code, in line order'''
    if not stg.remx_lines:
        return c_code
    ending = re.search(r'[\r\n]*$', c_code[0]).group() if c_code else '\n'
    lines = [(int(re.match(r'\d+', text).group()), text) for text in c_code]
    used = {number for number, _ in lines}
    for number, text in stg.remx_lines:
        if number in used:
            Info.log(1, f'remx line {number} is already used by the program. '
                        'Choose another number or change -ls/-lp.')
        used.add(number)
        lines.append((number, text + ending))
    return [text for _, text in sorted(lines, key=lambda line: line[0])]


def _mask_code(text):
    '''Blank string contents and drop REM text so only code is searched'''
    masked = []
    in_quotes = False
    for char in text:
        if char == '"':
            in_quotes = not in_quotes
            masked.append(char)
        else:
            masked.append(' ' if in_quotes else char)
    masked = ''.join(masked)
    rem = REM_MATCH.search(masked)
    return masked[:rem.start()] if rem else masked


def dignify_numbered(d_code):
    '''Turn a numbered classic listing into Dignified code with jump labels'''
    numbered = []
    for line in d_code[1:]:
        if not line.text.strip() or line.text.lstrip().startswith('#'):
            continue
        match = NUMBERED_LINE_MATCH.match(line.text)
        if not match:
            Info.log(1, f'Line {line.nmbr}: numbered listing line expected: {line.text.strip()}')
        number = int(match.group(1))
        if numbered and number <= numbered[-1][0]:
            Info.log(1, f'Line {number}: line numbers must increase.')
        numbered.append((number, match.group(2), line))

    line_numbers = [number for number, _, _ in numbered]
    targets = set()
    converted = []
    for number, text, line in numbered:
        masked = _mask_code(text)
        jump = JUMP_MATCH.search(masked)
        if jump:
            argument = masked[jump.end():].strip()
            if argument.isdigit():
                wanted = int(argument)
                target = next((n for n in line_numbers if n >= wanted), None)
                if target is None:
                    Info.log(1, f'Line {number}: jump target {wanted} is after the last line.')
                targets.add(target)
                text = f'{text[:jump.end()].rstrip()} {{line{target}}}'
            elif argument:
                Info.log(1, f'Line {number}: computed jump target cannot be renumbered: '
                            f'{text[jump.end():].strip()}. Use -asc to keep the original numbering.')
        converted.append((number, text, line))

    dignified = [d_code[0]]
    converted = {line: (number, text) for number, text, line in converted}
    for line in d_code[1:]:
        if line not in converted:
            keep = line.text if line.text.lstrip().startswith('##') else '\n'
            dignified.append(line._replace(text=keep))
            continue
        number, text = converted[line]
        label = f'{{line{number}}} ' if number in targets else ''
        dignified.append(line._replace(text=f'{label}{text}\n'))
    return dignified


class Description(MSXDescription):
    def sysinfo(self):
        self.system_name = 'Sinclair ZX-81'
        self.dignified_ext = '.DZX'
        self.ascii_ext = '.AZX'
        self.binary_ext = '.p'
        self.dignify_numbered = True
        self.numbered_ignore = REMX_IGNORE

    def __init__(self):
        super().__init__()

        c_instrc = ['COPY', 'CLEAR', 'UNPLOT', 'CLS', 'IF', 'RANDOMIZE', 'RAND',
                    'SAVE', 'RUN', 'PLOT', 'PRINT', 'POKE', 'NEXT', 'PAUSE',
                    'LET', 'LIST', 'LOAD', 'INPUT', 'FOR', 'TO', 'STEP', 'DIM',
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
        # Lets the lexer continue through the exponent of numbers like 4E4.
        clc_part = r'(?P<c_partls>(^(\d*\.?)?\d+E[+-]?$))'
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
    def lexing(self):
        source = self.lex
        # The lexer repeats a PROGRAM line at the end; it is not a user variable.
        if source.tk.tok == 'D_IDNTTP' and source.tk.val == 'PROGRAM' \
                and source.tk.pos.lin >= source.pos.code_len - 1:
            return None
        if source.tk.val == '\\' and source.lookahead() == '{':
            escape = source.tk.val
            while not re.match(source.des.newline, source.lookahead()):
                escape += source.advance()
                if escape.endswith('}'):
                    break
            if not HEX_ESCAPE_MATCH.fullmatch(escape):
                Info.log(1, 'Invalid hexadecimal escape; expected \\{XX}.', source.tk)
            return self.Tok(tok='C_HEXBYT', val=escape, pos=source.tk.pos)
        return super().lexing()

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
        current = self.par.token
        if current.tok == 'C_HEXBYT' and current.val not in self.des.c_symb_comp:
            self.des.c_symb_comp.append(current.val)
        if self.par.n > 0:
            previous = self.par.line[self.par.n - 1]
            if previous.tok == 'C_LINREM' and current.tok == 'C_LITREM' \
                    and current.val.startswith(' ') and self.stg.general_spaces:
                current.val = current.val[1:]
            previous_is_keyword = previous.uval in self.des.c_reserved_kw
            current_is_keyword = current.uval in self.des.c_reserved_kw
            needs_space = previous.tok == 'C_LINENB' \
                or (previous_is_keyword and current.val not in self.des.c_symb_comp) \
                or (current_is_keyword and previous.val not in self.des.c_symb_comp) \
                or current.val == '**' \
                or previous.val == '**' \
                or (current.tok == 'C_LITREM' and previous.tok == 'C_LINREM') \
                or (current.tok == 'C_LINREM' and previous.tok == 'C_LINREM')
            if needs_space and not self.par.c_line.endswith(' ') \
                    and (previous.tok == 'C_LINENB' or
                         (previous.tok != 'C_HEXBYT' and current.tok != 'C_HEXBYT')):
                self.par.c_line += ' '
            # ZX-81 statements must start with a keyword, so assignments need LET.
            if current.tok == 'D_IDNTTP' \
                    and (previous.tok == 'C_LINENB' or previous.uval == 'THEN'):
                self.par.c_line += 'LET ' if self.stg.capitalise_all else 'let '
        return False