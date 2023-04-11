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
        self.system_name = 'MSX'
        self.dignified_ext = '.dmx'
        self.ascii_ext = '.amx'
        self.binary_ext = '.bmx'

    def __init__(self):
        super(Description, self).__init__()

        # Instructions
        c_instrc = ['AS', 'BASE', 'BEEP', 'BLOAD', 'BSAVE', 'CALL', 'CIRCLE',
                    'CLEAR', 'CLOAD', 'CLOSE', 'CLS', 'CMD', 'COLOR', 'CONT',
                    'COPY', 'CSAVE', 'CSRLIN', 'DEF', 'DEFDBL', 'DEFINT', 'MAXFILES',
                    'DEFSNG', 'DEFSTR', 'DIM', 'DRAW', 'DSKI', 'END', 'EQV',
                    'ERASE', 'ERR', 'ERROR', 'FIELD', 'FILES', 'FN', 'FOR', 'GET',
                    'IF', 'INPUT', 'INTERVAL', 'IMP', 'IPL', 'KILL', 'LET',
                    'LFILES', 'LINE', 'LOAD', 'LOCATE', 'LPRINT', 'LSET', 'MAX',
                    'MERGE', 'MOTOR', 'NAME', 'NEW', 'NEXT', 'OFF', 'ON', 'OPEN',
                    'OUT', 'OUTPUT', 'PAINT', 'POINT', 'POKE', 'PRESET', 'PRINT',
                    'PSET', 'PUT', 'READ', 'RSET', 'SAVE', 'SCREEN', 'SET',
                    'SOUND', 'STEP', 'STOP', 'SWAP', 'TIME', 'TO', 'TROFF',
                    'TRON', 'USING', 'VPOKE', 'WAIT', 'WIDTH', r'\?', r'DEFUSR(\d)?']

        # Functions ending with $
        c_funcdl = [r'ATTR\$', r'BIN\$', r'CHR\$', r'DSKO\$', r'HEX\$',
                    r'INKEY\$', r'INPUT\$', r'LEFT\$', r'MID\$', r'MKD\$',
                    r'MKI\$', r'MKS\$', r'OCT\$', r'RIGHT\$', r'SPACE\$',
                    r'SPRITE\$', r'STR\$', r'STRING\$']

        # Normal functions
        c_funcnm = ['ABS', 'ASC', 'ATN', 'CDBL', 'CINT', 'COS', 'CSNG', 'CVD',
                    'CVI', 'CVS', 'DSKF', 'EOF', 'EXP', 'FIX', 'FPOS', 'FRE',
                    'INP', 'INSTR', 'INT', 'KEY', 'LEN', 'LOC', 'LOF', 'LOG',
                    'LPOS', 'PAD', 'PDL', 'PEEK', 'PLAY', 'POS', 'RND', 'SGN',
                    'SIN', 'SPC', 'SPRITE', 'SQR', 'STICK', 'STRIG', 'TAB', 'TAN',
                    r'USR(\d)?', 'VAL', 'VARPTR', 'VDP', 'VPEEK']

        # Jump instructions
        c_jumpin = ['RESTORE', 'AUTO', 'RENUM', 'DELETE', 'RESUME', 'ERL', 'ELSE',
                    'RUN', 'LIST', 'LLIST', 'GOTO', 'RETURN', 'THEN', 'GOSUB']

        # Logical operators
        c_operat = ['AND', 'MOD', 'NOT', 'OR', 'XOR']

        # Symbols
        c_symbol = ['>', '=', '<', r'\+', r'\*', r'/', r'\^', r'\\', '-',
                    r',', r'\(', r'\)', r';', r'#']

        # Translation
        # Characters for simple replacement: ☺☻♥♦♣♠·◘○◙♂♀♪♬☼┿┴┬┤├┼│─┌┐└┘╳╱╲╂
        self.c_replacements = {'☺': 'A', '☻': 'B', '♥': 'C', '♦': 'D', '♣': 'E', '♠': 'F',
                               '·': 'G', '◘': 'H', '○': 'I', '◙': 'J', '♂': 'K', '♀': 'L',
                               '♪': 'M', '♬': 'N', '☼': 'O', '┿': 'P', '┴': 'Q', '┬': 'R',
                               '┤': 'S', '├': 'T', '┼': 'U', '│': 'V', '─': 'W', '┌': 'X',
                               '┐': 'Y', '└': 'Z', '┘': '[', '╳': ']', '╱': '\\', '╲': '^',
                               '╂': '_'}

        # Characters for Unicode ASCII translation
        # These two blocks must have index parity
        self.c_original = ('ÇüéâäàåçêëèïîìÄÅÉæÆôöòûùÿÖÜ¢£¥₧ƒáíóúñÑªº¿⌐¬½¼¡«»ÃãĨĩÕõŨũĲĳ¾∽◇‰¶§'
                           '▂▚▆▔◾▇▎▞▊▕▉▨▧▼▲▶◀⧗⧓▘▗▝▖▒Δǂω█▄▌▐▀αβΓπΣσμτΦθΩδ∞φ∈∩≡±≥≤⌠⌡÷≈°∙‐√ⁿ²❚■')
        self.c_translat = ('\u0080\u0081\u0082\u0083\u0084\u0085\u0086\u0087\u0088\u0089\u008A\u008B\u008C\u008D\u008E\u008F'
                           '\u0090\u0091\u0092\u0093\u0094\u0095\u0096\u0097\u0098\u0099\u009A\u009B\u009C\u009D\u009E\u009F'
                           '\u00A0\u00A1\u00A2\u00A3\u00A4\u00A5\u00A6\u00A7\u00A8\u00A9\u00AA\u00AB\u00AC\u00AD\u00AE\u00AF'
                           '\u00B0\u00B1\u00B2\u00B3\u00B4\u00B5\u00B6\u00B7\u00B8\u00B9\u00BA\u00BB\u00BC\u00BD\u00BE\u00BF'
                           '\u00C0\u00C1\u00C2\u00C3\u00C4\u00C5\u00C6\u00C7\u00C8\u00C9\u00CA\u00CB\u00CC\u00CD\u00CE\u00CF'
                           '\u00D0\u00D1\u00D2\u00D3\u00D4\u00D5\u00D6\u00D7\u00D8\u00D9\u00DA\u00DB\u00DC\u00DD\u00DE\u00DF'
                           '\u00E0\u00E1\u00E2\u00E3\u00E4\u00E5\u00E6\u00E7\u00E8\u00E9\u00EA\u00EB\u00EC\u00ED\u00EE\u00EF'
                           '\u00F0\u00F1\u00F2\u00F3\u00F4\u00F5\u00F6\u00F7\u00F8\u00F9\u00FA\u00FB\u00FC\u00FD\u00FE\u00FF')

        # Symbols for space separation
        c_symbol_str = [s.replace('\\', '') for s in c_symbol]
        c_symbol_str.remove('#')
        self.c_symb_comp = c_symbol_str + [':'] + ['_']

        # Extended classic symbols
        c_e_symb = [r'\+\+', '--', r'\+=', r'-=', r'\*=', '/=', r'\^=']

        # Reserved keywords
        self.c_reserved_kw = c_instrc + c_jumpin + c_funcdl \
                                      + c_funcnm + c_operat + ['DATA']
        self.c_reserved_kw = [s.replace('\\d', '') for s in self.c_reserved_kw]
        self.c_reserved_kw = [s.replace('\\', '') for s in self.c_reserved_kw]

        # Numbers
        # Decimal
        c_numdec = r'(^(\d*\.?)?\d+((D|E)(\+|-)\d+)?([%#!])?$)'  # TEST THIS
        # Hexadecimal
        c_numhex = r'(^&H[a-fA-F0-9]+$)'
        # Octal
        c_numoct = r'(^&O[0-7]+$)'
        # Binary
        c_numbin = r'(^&B[0-1]+$)'

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
        self.c_idnttp_grp = r'^([a-zA-Z][a-zA-Z_0-9]*)([%!#$]?)$'
        # Number of valid chars to identify a long variable
        self.c_var_valid_chars = 2
        # Number of alphabet letter combinations 26*26
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
        c_partls = [r'&(h|o|b)?']

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
        clc_numb = fr'(?P<c_number>({c_numdec}|{c_numhex}|{c_numoct}|{c_numbin}))'

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
        self.CLASSIC_INI = 'badig_msx.ini'

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
        # self.remtags = {'MSX Module': [remtag('MSX Module REMTAG', 'Testing', 'Test')]}
        # remtag = namedtuple('remtag', 'name help metavar')
        self.remtags = {}

        # Command line arguments
        self.parser = argparse.ArgumentParser(add_help=False)  # None if no arguments to expose
        arg_group = self.parser.add_argument_group('MSX Module')

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
        # replace [?](x,y) for locate x,y:print
        # Create a define namedtuple structure
        def_rep = self.par.tok_str('locate VAR:?')
        def_rep[1].tok = 'D_DEFVAR'
        def_var = self.par.tok_str('0,0')
        def_grp = namedtuple('def_grp', 'repl varv')
        print_at_dict = {'?': (def_grp(def_rep, def_var))}
        # Add print_at_dict to self.des.d_defines
        self.des.d_defines = {**self.des.d_defines, **print_at_dict}

    # Methods -----------------------------------------------------------------
    def get_hard_variable(self, tk):
        '''Get a list of hardcoded short variables'''

        vc = self.des.c_var_valid_chars

        # If variable preceded by ~
        if self.par.last_tok().val == self.des.d_keepid:
            if len(tk.var_name) <= vc:
                Info.log(1, f"Can't use {self.des.d_keepid} "
                            f"on a short named variable: "
                            f"{tk.var_name}", tk)

            if tk.val_w_file in self.des.d_declares:
                Info.log(1, f'Long variable already declared: '
                            f'{tk.lval} '
                            f'{tk.var_name}:{self.des.d_declares[tk.val_w_file]}', tk)

            for var in self.des.c_hard_long_vars:
                if tk.var_name != var.var_name \
                        and (var.var_name.startswith(tk.var_name)
                             or tk.var_name.startswith(var.var_name)):
                    Info.log(2, f'Reserved long variable conflict: '
                                f'{tk.var_name} {var.var_name}', tk)

            # Remove the ~ and update long hard vars list
            self.par.tok_list_out.pop()
            self.des.c_hard_long_vars.update({tk})

            return

        # Leave if variable is already declared
        if tk.val_w_file in self.des.d_declares.keys():

            return

        for var in self.des.c_hard_short_vars:
            if len(tk.var_name) > vc and tk.var_name[:vc] == var:
                Info.log(2, f'Reserved short variable conflict: '
                            f'{tk.var_name} {var}', tk)

        for var in self.des.c_hard_long_vars:
            if (tk.var_name != var.var_name) \
                    and ((tk.var_name == var.var_name[:vc])
                         or (tk.var_name in [lng_var.var_name for lng_var in self.des.c_hard_long_vars]
                             and var.var_name.startswith(tk.var_name))):
                Info.log(2, f'Reserved long variable conflict: '
                            f'{tk.var_name} {var.var_name}', tk)

        if len(tk.var_name) <= vc:
            self.des.c_hard_short_vars.update({tk.var_name})

        return

    def process_variable(self, tk):
        '''Transform long named variables into short, two characters, ones'''

        vc = self.des.c_var_valid_chars

        # Leave if variable is short
        if len(tk.var_name) <= vc:

            return tk

        # Leave if variable already kept as long named
        for var in self.des.c_hard_long_vars:
            if tk.var_name == var.var_name and tk.pos.file == var.pos.file:
                return tk

        # Return declared short named variable
        if tk.val_w_file in self.des.d_declares:

            tk.val = self.des.d_declares[tk.val_w_file] + tk.var_type

            return tk

        # Create new short variable
        # Get xx format by decomposing 676 in two base 26 digits (a-z)
        while self.var_index > 0:
            self.var_index -= 1

            idx_h = int(self.var_index / self.des.c_var_mod)
            idx_l = round(self.var_index % self.des.c_var_mod)

            short_var = self.des.c_var_chr[idx_h] + self.des.c_var_chr[idx_l]

            if short_var not in self.des.d_declares.items() \
                    and short_var not in self.des.c_hard_short_vars \
                    and short_var not in [var.var_name[:vc] for var in self.des.c_hard_long_vars]:

                self.des.d_declares[tk.val_w_file] = short_var
                tk.val = short_var + tk.var_type

                return tk

        Info.log(1, f'Too many variables used (max={self.des.c_var_max}): '
                    f'{self.par.tk.val}', self.par.tk)

    def trans_char(self, text):
        '''Convert unicode characters into ASCII equivalents'''

        text = ''.join([self.des.c_replacements.get(c, c) for c in text])
        translation = text.maketrans(self.des.c_original, self.des.c_translat)
        text = text.translate(translation)

        return text

    # Pass 1 ------------------------------------------------------------------
    def pass_1(self):
        '''Parser Tokens processing'''

        # Convert _ separator to call if not at end of line
        if self.par.tk.tok == 'D_INSTSP' \
                and self.par.tok_list_in[self.par.index + 1].tok != 'NEWLINE':
            self.par.tk.tok = 'C_CALINS'

            return False

        # Convert generic identifier to call identifier if after _
        if self.par.tk.tok == 'D_IDNTTP' \
                and self.par.tok_list_out[-1].tok == 'C_CALINS':
            self.par.tk.tok = 'C_CALIDF'

            return False

        return False

    # Pass 2 ------------------------------------------------------------------
    def pass_2(self):
        '''Parser Tokens processing'''

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
