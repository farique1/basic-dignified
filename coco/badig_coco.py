import re
import os.path
import argparse
import configparser
from collections import namedtuple

from support.helper import Infolog

infolog = Infolog()


# Description class -----------------------------------------------------------
class Description:
    '''A description of this system classic basic'''

    def sysinfo(self):
        '''General information about the system. Name, extensions, etc'''
        self.system_name = 'Tandy Color Computer'
        self.dignified_ext = '.DCC'
        self.ascii_ext = '.ACC'
        self.binary_ext = '.BCC'

    def __init__(self):
        super(Description, self).__init__()

        # Instructions
        c_instrc = ['ATTR', 'AUDIO', 'BACKUP', 'CIRCLE', 'CLEAR', 'CLOAD',
                    'CLOSE', 'CLS', 'CMP', 'COLOR', 'CONT', 'COPY', 'CSAVE', 'CVN',
                    'DATA', 'DEF', 'DIM', 'DIR', 'DLOAD', 'DOS', 'DRAW', 'DRIVE',
                    'DSKINI', 'END', 'EVAL', 'EXEC', 'FIELD',
                    'FILES', 'FOR', 'FREE', 'GET', 'HBUFF', 'HCIRCLE', 'HCLS',
                    'HCOLOR', 'HDRAW', 'HGET', 'HLINE', 'HPAINT', 'HPRINT', 'HPUT',
                    'HRESET', 'HSCREEN', 'HSET', 'HSTAT', 'IF', 'INPUT', 'KILL', 'LET',
                    'LINE', 'LOAD', 'LOCATE', 'LOC', 'LOF', 'LPOKE',
                    'LSET', 'MERGE', 'MOTOR', 'NEW', 'NEXT', 'OFF', 'ON', 'OPEN', 'PAINT',
                    'PALETTE', 'PCLEAR', 'PCLS', 'PCOPY', 'PLAY', 'PMODE', 'POKE', 'PRESET',
                    'PRINT', 'PSET', 'PUT', 'READ', 'REM', 'RENAME', 'RESET',
                    'RESTORE', 'RETURN', 'RGB', 'RSET', 'SAVE', 'SCREEN', 'SET',
                    'SKIPF', 'SOUND', 'STEP', 'STOP', 'SUB', 'TAB', 'TO', 'TROFF',
                    'TRON', 'UNLOAD', 'VERIFY', 'WIDTH', 'WRITE', r'DSKI\$', r'DSKO\$',
                    r'MKN\$', r'\?', r'DEFUSR(\d)?']

        # Functions ending with \$
        c_funcdl = [r'CHR\$', r'HEX\$', r'INKEY\$', r'LEFT\$', r'RIGHT\$', r'MID\$', r'STR\$']

        # Normal functions
        c_funcnm = ['ABS', 'ASC', 'ATN', 'BUTTON', 'COS', 'EOF', 'ERLIN', 'ERRNO', 'EXP',
                    'FIX', 'HPOINT', 'INSTR', 'INT', 'JOYSTK', 'LEN', 'LOG', 'LPEEK', 'MEM',
                    'PEEK', 'POINT', 'POS', 'PPOINT', 'RND', 'SGN', 'SIN', 'STRING', 'SQR',
                    'TAN', 'TIMER', r'USR(\d)?', 'VAL', 'VARPTR']

        # Jump instructions
        c_jumpin = ['GOTO', 'GOSUB', 'RENUM', 'RUN', 'DEL', 'ELSE',
                    'LIST', 'LLIST', 'THEN', 'BRK', 'ERR', 'EDIT']

        # Logical operators
        c_operat = ['NOT', 'AND', 'OR']

        # Symbols
        c_symbol = ['>', '=', '<', r'\+', r'\*', r'/', r'\^', '-',
                    r',', r'\(', r'\)', r';', r'#', r'@']

        # Translation
        # Characters for Unicode ASCII translation
        # These two blocks must have index parity
        self.c_original = ('█▛▜▀▙▌▚▘▟▞▐▝▄▖▗')
        self.c_translat = ('\u0080\u0081\u0082\u0083\u0084\u0085\u0086\u0087'
                           '\u0088\u0089\u008A\u008B\u008C\u008D\u008E')

        # Symbols for space separation
        c_symbol_str = [s.replace('\\', '') for s in c_symbol]
        c_symbol_str.remove('#')
        self.c_symb_comp = c_symbol_str + [':'] + ['_']

        # Extended classic symbols
        c_e_symb = [r'\+\+', '--', r'\+=', r'-=', r'\*=', '/=', r'\^=']

        # Reserved keywords (removing regex and escape characters)
        self.c_reserved_kw = c_instrc + c_jumpin + c_funcdl \
                                      + c_funcnm + c_operat + ['DATA']
        self.c_reserved_kw = [s.replace('\\d', '') for s in self.c_reserved_kw]
        self.c_reserved_kw = [s.replace('\\', '') for s in self.c_reserved_kw]

        # Numbers
        # Decimal
        c_numdec = r'(^(\d*\.?)?\d+((E)(\+|-)\d+)?$)'  # TEST THIS
        # Hexadecimal
        c_numhex = r'(^&H[a-fA-F0-9]+$)'
        # Octal
        c_numoct = r'(^&O[0-7]+$)'

        # Literals
        # Quotes
        c_litquo = r'(^"$)'
        self.c_quotes = '"'
        # Open extended rem block
        c_o_brem = r"(^''$)"
        # Classic rem
        self.c_altrem = "'"
        c_linrem = r"(^'$|^REM$)"
        # Label report rem
        self.c_lab_rep_rem = " '"
        # Data
        c_dataln = r"(^DATA$)"
        self.c_datasepar = ","
        # Literal tokens
        self.c_lit_toks = ['C_LITREM', 'C_LIBREM', 'C_LITQUO', 'C_LITDAT']

        # Print instruction and alternate
        self.c_print_ins = 'print'
        self.c_print_alt = '?'

        # Variables
        # Hard coded short variable names
        self.c_hard_short_vars = set()
        # Kept long named variables
        self.c_hard_long_vars = set()
        # Short names without type
        self.c_varsna = r'^[a-zA-z][a-zA-Z0-9]?$'
        # Variable character letters. First and second chars
        self.c_var_chr = 'abcdefghijklmnopqrstuvwxyz'
        # Variable character numbers. Only second chars
        self.c_var_num = '0123456789'
        # Identifier with type and groups for match
        self.c_idnttp_grp = r'^([a-zA-Z][a-zA-Z_0-9]*)([$]?)$'
        # Number of valid chars to identify a long variable
        self.c_var_valid_chars = 2
        # Number of alpabet letter combinations 26*26
        # 2 alphabet letters ('xx') 26 mod 26
        self.c_var_max = 676
        self.c_var_mod = 26

        # Command separator
        # Use _ for line separation if there isn't a
        # instruction separator in the Classic basic
        c_instsp = r'^:$'
        self.c_instsp_str = ':'

        # Equal sign
        self.c_equal = '='

        # Loop labels loop back classic token equivalent
        self.c_loop_back = 'goto'

        # Function calls classic equivalent
        self.c_func_call = 'gosub'
        # Function return classic equivalent
        self.c_func_ret = 'return'
        # Delimiter keywords stops function calls looking for variables
        self.c_func_stop_kw = c_instrc + c_jumpin + c_funcdl + c_funcnm

        # Hack so the regex match partially until it get to the correct match
        c_partls = [r'&(h|o)?']

        # Additional tokens
        # (These token are not used for match, they are entered directly on the code
        # and are here only for reference)
        # Line numbers
        r'(?P<c_linenb>)'
        # Close extended rem block
        r'(?P<c_c_brem>)'
        # Literal part of rem block
        r'(?P<c_librem>)'
        # Literal part of quotes
        r'(?P<c_litquo>)'
        # Literal part of line rem
        r'(?P<c_litrem>)'
        # literal parts of data
        r'(?P<c_litdat>)'
        # Call instruction (shared with dignified line separator)
        # Decided in parser based on position relative to start of next line
        r'(?P<c_calins>)'
        # Call identifier to differentiate from variables and avoid conversion
        r'(?P<c_calidf>)'

        # Regex groups
        clc_func = fr"(?P<c_functs>{self.join_commands(c_funcnm, c_funcdl)})"
        clc_symb = fr"(?P<c_symbol>{self.join_commands(c_symbol)})"
        clc_esym = fr"(?P<c_e_symb>{self.join_commands(c_e_symb)})"
        clc_oper = fr"(?P<c_operat>{self.join_commands(c_operat)})"
        clc_jump = fr"(?P<c_jumpin>{self.join_commands(c_jumpin)})"
        clc_inst = fr"(?P<c_instrc>{self.join_commands(c_instrc)})"
        clc_part = fr"(?P<c_partls>{self.join_commands(c_partls)})"
        clc_lrem = fr'(?P<c_linrem>{c_linrem})'
        clc_data = fr'(?P<c_dataln>{c_dataln})'
        clc_brem = fr'(?P<c_o_brem>{c_o_brem})'
        clc_insp = fr'(?P<c_instsp>{c_instsp})'
        clc_litr = fr'(?P<c_quotes>{c_litquo})'
        clc_numb = fr'(?P<c_number>({c_numdec}|{c_numhex}|{c_numoct}))'

        # Groups assembled for compiling (order is important)
        self.classic_groups = (''
                               rf'{clc_oper}|'
                               rf'{clc_symb}|'
                               rf'{clc_esym}|'
                               rf'{clc_func}|'
                               rf'{clc_jump}|'
                               rf'{clc_inst}|'
                               rf'{clc_numb}|'
                               rf'{clc_lrem}|'
                               rf'{clc_data}|'
                               rf'{clc_brem}|'
                               rf'{clc_part}|'
                               rf'{clc_insp}|'
                               rf'{clc_litr}')


# Convert information to the logger module format -----------------------------
class Info():
    '''Convert the information to the infolog module and send it
       lvl = Message level
       desc = Message description
       tok = Current token being addressed
       bullet = Bullet format override
       show_file = Show filename on the message'''

    def log(lvl, desc, tok=None, bullet=None, show_file=False):
        if tok:
            data_pack = namedtuple('data_pack', 'lin col offset text file')
            tok = data_pack(tok.pos.lin,
                            tok.pos.col,
                            tok.pos.offset,
                            tok.pos.text,
                            tok.pos.file)

        infolog.log(lvl, desc, tok, bullet, show_file)


class Settings:
    def __init__(self):
        '''Initialize variables, .ini, arguments and process the user input information'''

        # Files
        self.CLASSIC_INI = 'badig_coco.ini'

        # Variables
        self.convert_print = ''          # Convert ? to PRINT or vice-versa: ?=? p=PRINT
        self.strip_then_goto = ''        # Strip adjacent THEN/ELSE or GOTO: t=THEN/ELSE g=GOTO

    def get_ini(self):
        '''Read the .ini file if present using the defaults from the variables'''

        local_path = os.path.split(os.path.abspath(__file__))[0]
        ini_path = os.path.join(local_path, self.CLASSIC_INI)
        config = configparser.ConfigParser()
        if os.path.isfile(ini_path):
            config.sections()
            try:
                config.read(ini_path)
                configs_sec = config['CONFIGS']
                self.convert_print = configs_sec.get('convert_print') or self.convert_print
                self.strip_then_goto = configs_sec.get('strip_then_goto') or self.strip_then_goto
            except (ValueError, KeyError, configparser.NoOptionError) as e:
                Info.log(1, f'Problem with: {self.CLASSIC_INI}:{str(e)}')

        return config

    def properties(self, stg):
        '''Called from badig_settings to process the classic arguments
        Variables are added to Badig Settings in the .c_stg namespace'''

        self.convert_print = stg.args.cp.upper() if stg.args.cp else None
        self.strip_then_goto = stg.args.tg.upper()

        return self


# Expose elements to Badig ----------------------------------------------------
class Expose:
    '''Expose values up the dignified chain'''

    def __init__(self):
        stg = Settings()
        stg.get_ini()

        # remTAGs
        # remTAGs (Uncomment the namedtuple and populate the dictionary to add remtags)
        # With this format:
        # remtag = namedtuple('remtag', 'name help metavar')
        # self.remtags = {'CoCo Module': [remtag('CoCo Module REMTAG', 'Testing', 'Test')]}
        self.remtags = {}

        # Command line arguments
        self.parser = argparse.ArgumentParser(add_help=False)  # None if no arguments to expose
        arg_group = self.parser.add_argument_group('CoCo Module')

        arg_group.add_argument('-cp', metavar='?|p',
                               default=stg.convert_print, choices=['?', 'p'], type=str.lower,
                               help='Convert ? to PRINT or vice-versa (def %(default)s)')

        arg_group.add_argument('-tg', metavar='t|g',
                               default=stg.strip_then_goto, choices=['t', 'g'], type=str.lower,
                               help='Remove adjacent THEN/ELSE or GOTO: '
                                    't=THEN/ELSE, g=GOTO (def %(default)s)')


# Lexer -----------------------------------------------------------------------
class Lexer:
    '''Execute the Lexer Classic specific duties
       lex = The Main lexer object
       stg = The settings object
       Tok = The token class
       When returning to the main Badig module:
       False = go on with the execution of the pass loop
       None = "continue" command. Return to the start of the pass loop
       Token = pass the token to the lexer token (self.tk) and go on'''

    def __init__(self, lex, stg, Tok):
        self.lex = lex
        self.pos = lex.pos
        self.des = lex.des
        self.stg = stg
        self.Tok = Tok

    # Initialization ----------------------------------------------------------
    def initialization(self):
        '''Classic Lexer initialization'''
        pass

    # Pass --------------------------------------------------------------------
    def lexing(self):
        '''Classic Lexer Tokens lexing'''

        # Process data line
        # Here for the quirks of the literals handling on DATA lines
        if self.lex.tk.tok == 'C_DATALN':
            self.lex.lexer.append(self.lex.tk)

            data_line = self.get_data_line()
            if data_line:
                self.lex.lexer.extend(data_line)

            return None

        return False

    # Methods -----------------------------------------------------------------
    def get_data_line(self):
        '''Get literals of the data instruction and perform the line joining'''
        nl = self.des.newline
        se = self.des.c_instsp_str
        ds = self.des.c_datasepar
        qs = self.des.c_quotes
        di = self.des.d_instsp_str
        part = ''
        join = ''
        data_line = []
        l_pos = self.pos.copy(col=self.pos.col + 1)

        while self.lex.lookahead() == ' ':
            self.lex.advance()
            pass

        if self.lex.lookahead() == se:
            return

        while True:
            last_chr = self.lex.advance()
            part += last_chr

            if not part.strip():
                part = ''
                continue

            if part == qs:
                next_char = ''

                while True:
                    last_chr = self.lex.advance()
                    part += last_chr
                    next_char = self.lex.lookahead()
                    l = re.match(qs, last_chr)
                    n = re.match(nl, next_char)
                    if l or n:
                        break

            next_char = self.lex.lookahead()

            l = re.match(ds, last_chr)
            n = re.match(fr'{se}|{nl}', next_char)
            if l or n:
                if l:
                    part = part.rstrip(ds)

                data_line.append(self.Tok(tok='C_LITDAT',
                                          val=join + part,
                                          pos=l_pos))

                if l:
                    new_pos = self.pos.copy(col=self.pos.col - 1)
                    data_line.append(self.Tok(tok='C_SYMBOL',
                                              val=ds,
                                              pos=new_pos))
                    l_pos = self.pos.copy()
                    part = ''
                    join = ''

                if n:
                    if n.group() == se or not part:
                        break
                    elif part[-1] != di:
                        break
                    join = data_line.pop().val.rstrip(di)
                    part = ''
                    self.lex.advance()

        return data_line


# Parser ----------------------------------------------------------------------
class Parser:
    '''Execute the Parser Classic specific duties
       par = The main parser object
       stg = The settings object
       Tok = The token class
       When returning to the main Badig module:
       False = go on with the execution of the pass loop
       None = "continue" command. Return to the start of the pass loop
       Token = pass the token to the parser token (self.tk) and go on'''

    def __init__(self, par, stg, Tok):
        self.par = par
        self.des = par.des
        self.stg = stg
        self.Tok = Tok
        self.var_index = self.des.c_var_max

    # Initialization ----------------------------------------------------------
    def initialization(self):
        '''Classic Parser initialization'''

        # Insert the default [?] define in the dictionary
        # replace [?](x,y) for D_SPCIAL x,y D_SPCIAL
        # D_SPCIAL will later tell the x,y component to be processed
        tok0 = self.Tok(tok='D_SPCIAL', val='?', pos=self.par.tk.pos.copy())
        tok1 = self.Tok(tok='D_DEFVAR', val='var', pos=self.par.tk.pos.copy())
        tok2 = self.Tok(tok='D_SPCIAL', val='??', pos=self.par.tk.pos.copy())
        def_var = self.Tok(tok='C_NUMBER', val='0', pos=self.par.tk.pos.copy())
        # Create a define namedtuple structure
        def_grp = namedtuple('def_grp', 'repl varv')
        print_at_dict = {'?': (def_grp([tok0, tok1, tok2], [def_var]))}
        # Add print_at_dict to self.des.d_defines
        self.des.d_defines = {**self.des.d_defines, **print_at_dict}

    # Methods -----------------------------------------------------------------
    def get_hard_variable(self, tk):
        '''Get a list of hardcoded short variables'''

        vc = self.des.c_var_valid_chars

        g = re.match(self.des.c_idnttp_grp, tk.lval)
        variable = g.group(1)

        # If variable preceded by ~
        if self.par.last_tok().val == self.des.d_keepid:
            if len(variable) <= vc:
                Info.log(1, f"Can't use {self.des.d_keepid} "
                            f"on a short named variable: "
                            f"{variable}", tk)

            if variable in self.des.d_declares:
                Info.log(1, f'Long variable already declared: '
                            f'{variable}:{self.des.d_declares[variable]}', tk)

            for var in self.des.c_hard_long_vars:
                if variable != var.var_name \
                        and (var.var_name.startswith(variable)
                             or variable.startswith(var.var_name)):
                    Info.log(2, f'Reserved long variable conflict: '
                                f'{variable} {var.var_name}', tk)

            # Remove the ~ and update long hard vars list
            self.par.tok_list_out.pop()
            self.des.c_hard_long_vars.update({tk})

            return

        # Leave if variable is already declared
        if variable in self.des.d_declares.keys():

            return

        for var in self.des.c_hard_short_vars:
            if len(variable) > vc and variable[:vc] == var:
                Info.log(2, f'Reserved short variable conflict: '
                            f'{variable} {var}', tk)

        for var in self.des.c_hard_long_vars:
            if (variable != var.var_name) \
                    and ((variable == var.var_name[:vc])
                         or (variable in [lng_var.var_name for lng_var in self.des.c_hard_long_vars]
                             and var.var_name.startswith(variable))):
                Info.log(2, f'Reserved long variable conflict: '
                            f'{variable} {var.var_name}', tk)

        if len(variable) <= vc:
            self.des.c_hard_short_vars.update({variable})

        return

    def process_variable(self, tk):
        '''Transform long named variables into short, two characters, ones'''

        vc = self.des.c_var_valid_chars

        g = re.match(self.des.c_idnttp_grp, tk.lval)
        variable = g.group(1)
        var_type = g.group(2)

        # Leave if variable is short
        if len(variable) <= vc:

            return tk

        # Leave if variable already kept as long named
        for var in self.des.c_hard_long_vars:
            if variable == var.var_name and tk.pos.file == var.pos.file:
                return tk

        variable += tk.pos.file
        # Return declared short named variable
        if variable in self.des.d_declares:

            tk.val = self.des.d_declares[variable] + var_type

            return tk

        # Create new short variable
        # Get xx format by decomposing 676 in two base 26 digits (a-z)
        short_var = '--'
        while self.var_index > 0:
            self.var_index -= 1

            idx_h = int(self.var_index / self.des.c_var_mod)
            idx_l = round(self.var_index % self.des.c_var_mod)

            short_var = self.des.c_var_chr[idx_h] + self.des.c_var_chr[idx_l]

            if short_var not in self.des.d_declares.items() \
                    and short_var not in self.des.c_hard_short_vars \
                    and short_var not in [var.var_name[:vc] for var in self.des.c_hard_long_vars]:

                self.des.d_declares[variable] = short_var
                tk.val = short_var + var_type

                return tk

        Info.log(1, f'Too many variables used (max={self.des.c_var_max}): '
                    f'{self.par.tk.val}', self.par.tk)

    def trans_char(self, text):
        '''Convert unicode characters into ASCII equivalents'''

        translation = text.maketrans(self.des.c_original, self.des.c_translat)
        text = text.translate(translation)

        return text

    def replace_print_at(self):
        '''Get the passed special token indicating a [?] and process the elements
        Deal with the type and amount of the x,y terms according to each case
        Get the terms tokens'''

        term, term1, term2 = [], [], []
        comma = False
        while True:
            tok = self.par.next_tok()
            if tok.tok == 'D_SPCIAL' and tok.val == '??':
                self.par.next_tok()
                if comma:
                    term2 = term
                else:
                    term1 = term
                break
            term.append(tok)
            if tok.tok == 'C_SYMBOL' and tok.val == ',':
                term1 = term[:-1]
                term = []
                comma = True

        # Deal with them
        prt_list = self.par.tok_str('?@')
        if not term1 and not term2:
            prt_list.extend(self.par.tok_str('0'))
        elif term1 and not term2:
            prt_list.extend(term1)
        else:
            if not term1:
                term1 = self.par.tok_str('0')
            if (len(term1) == 1 and term1[0].val.isnumeric()) \
                    and (len(term2) == 1 and term2[0].val.isnumeric()):
                prt_sum = 32 * int(term2[0].val) + int(term1[0].val)
                prt_list.extend(self.par.tok_str(str(prt_sum)))
            else:
                mult32 = self.par.tok_str('32*(')
                addto = self.par.tok_str(')+(')
                close = self.par.tok_str(')')
                prt_list.extend(mult32 + term2 + addto + term1 + close)

        # Insert them mindind the use or not of ,
        prt_sep = self.par.tok_str(',')
        self.par.tok_list_out.extend(prt_list)
        next_tk = self.par.tk
        if next_tk.tok != 'C_INSTSP' and next_tk.tok != 'NEWLINE':
            self.par.tok_list_out.extend(prt_sep)

    # Pass 1 ------------------------------------------------------------------
    def pass_1(self):
        '''Parser Tokens processing'''

        return False

    # Pass 2 ------------------------------------------------------------------
    def pass_2(self):
        '''Parser Tokens processing'''

        # Replace [?](x,y)
        if self.par.tk.tok == 'D_SPCIAL' and self.par.tk.val == '?':
            self.replace_print_at()

        return False

    # Pass 3 ------------------------------------------------------------------
    def pass_3(self):
        '''Parser Tokens processing'''

        # Get hardcoded short named variables
        if self.par.tk.tok == 'D_IDNTTP':
            self.get_hard_variable(self.par.tk)

        return False

    # Pass 4 ------------------------------------------------------------------
    def pass_4(self):
        '''Parser Tokens processing'''

        # Replace long named variables for short named ones
        if self.par.tk.tok == 'D_IDNTTP':
            var = self.process_variable(self.par.tk)
            self.par.tk = var

        return False

    # Pass 5 ------------------------------------------------------------------
    def pass_5(self):
        '''Parser Tokens processing'''

        # Force capitalization
        self.par.stg.capitalise_all = True

        # Convert ? to print or vice versa
        if self.par.tk.tok == 'C_INSTRC' \
                and (self.par.tk.val == '?'
                     or self.par.tk.uval == 'PRINT') \
                and self.stg.c_stg.convert_print:

            if self.stg.c_stg.convert_print == '?':
                self.par.tk.val = self.des.c_print_alt
            else:
                self.par.tk.val = self.des.c_print_ins

            return self.par.tk

        # Strip THEN before GOTO
        elif self.stg.c_stg.strip_then_goto.upper() == 'T' \
            and self.par.tk.tok == 'C_JUMPIN' \
            and self.par.tk.uval == 'THEN' \
                and self.par.tok_list_in[self.par.index + 1].uval == 'GOTO':

            return None

        # Strip GOTO after THEN/ELSE
        elif self.stg.c_stg.strip_then_goto.upper() == 'G' \
            and self.par.tk.tok == 'C_JUMPIN' \
            and self.par.tk.uval == 'GOTO' \
            and (self.par.tok_list_out[-1].uval == 'THEN'
                 or self.par.tok_list_out[-1].uval == 'ELSE'):

            return None

        # Replace unary and assignment operator
        elif self.par.tk.tok == 'C_E_SYMB':
            operand_tok = self.par.tok_list_out[-1]
            operator_val = self.par.tk.val
            self.par.tok_list_out.extend(self.par.tok_str('='))
            self.par.tok_list_out.append(operand_tok)
            self.par.tok_list_out.extend(self.par.tok_str(operator_val[0]))
            if operator_val.count(operator_val[0]) == len(operator_val):
                self.par.tok_list_out.extend(self.par.tok_str('1'))

            return None

        # Replace true and false
        elif self.par.tk.tok == 'D_OPERAT':
            if self.par.tk.uval == 'FALSE':
                self.par.tok_list_out.extend(self.par.tok_str('0'))

                return None

            elif self.par.tk.uval == 'TRUE':
                self.par.tok_list_out.extend(self.par.tok_str('-1'))

                return None

        # Translate unicode characters to ASCII equivalent
        elif self.stg.translate \
                and self.par.tk.tok in self.des.c_lit_toks:
            self.par.tk.val = self.trans_char(self.par.tk.val)
            self.par.tok_list_out.append(self.par.tk)

            return None

        return False

    # Generate ----------------------------------------------------------------
    def generate(self):
        '''Generate the output code'''

        # Separate X from OR to avoid XOR
        if self.par.token.uval == 'OR' \
                and self.par.c_line[-1].upper() == 'X':
            self.par.c_line += ' '

        # Separate hex numbers from text begining with 'acbdef'
        elif self.par.token.uval[0] in 'ABCDEF' \
                and self.par.line[self.par.n - 1].tok == 'C_NUMBER':
            self.par.c_line += ' '

        return False
