import re
from collections import namedtuple

TOK_EXISTS = True
try:
    from . import msxbatoken as Tokenizer
except (ImportError, ModuleNotFoundError):
    TOK_EXISTS = False


# Description class -----------------------------------------------------------
class Description:
    '''A description of this system classic basic'''

    def __init__(self):
        super(Description, self).__init__()
        self.TOK_EXISTS = TOK_EXISTS

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
                    'TRON', 'USING', 'VPOKE', 'WAIT', 'WIDTH', r'\?', r'DEFUSR\d']

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
                    r'USR\d', 'VAL', 'VARPTR', 'VDP', 'VPEEK']

        # Jump instructions
        c_jumpin = ['RESTORE', 'AUTO', 'RENUM', 'DELETE', 'RESUME', 'ERL', 'ELSE',
                    'RUN', 'LIST', 'LLIST', 'GOTO', 'RETURN', 'THEN', 'GOSUB']

        # Logical operators
        c_operat = ['AND', 'MOD', 'NOT', 'OR', 'XOR']

        # Symbols
        c_symbol = ['>', '=', '<', r'\+', r'\*', r'/', r'\^', r'\\', '-',
                    r',', r'\(', r'\)', r';', r'#']

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
        self.c_lit_toks = ['C_LINREM', 'C_LIBREM', 'C_LITQUO', 'C_LITDAT']

        # Print instruction and alternate
        self.c_print_ins = 'print'
        self.c_print_alt = '?'

        # Variables
        # Used variable names with forbidden ones already added
        self.c_used_short_vars = {''}
        # Hard coded short variable names
        self.c_pure_short_vars = {''}
        # Short names without type
        self.c_varsna = r'^[a-zA-z][a-zA-Z0-9]?$'
        # Variable character letters. First and second chars
        self.c_var_chr = 'abcdefghijklmnopqrstuvwxyz'
        # Variable character numbers. Only second chars
        self.c_var_num = '0123456789'
        # Number of alpabet letter combinations 26*26
        # 2 alphabet letters ('xx') 26 mod 26
        self.c_var_max = 676

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


# Lexer -----------------------------------------------------------------------
class Lexer:
    '''Execute the Lexer Classic specific duties
       lex = The Main lexer object
       stg = The settings object
       Tok = The token class'''

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

            return None, None

        return '', None

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
       Tok = The token class'''

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
        def_grp = namedtuple('def_grp', 'repl varv')
        def_rep = self.par.tok_str('locate VAR:?')
        def_rep[1].tok = 'D_DEFVAR'
        print_at_dict = {'?': (def_grp(def_rep, []))}
        self.des.d_defines = {**self.des.d_defines, **print_at_dict}
        return None

    # Pass 1 ------------------------------------------------------------------
    def pass_1(self):
        '''Parser Tokens processing'''

        # Convert _ separator to call if not at end of line
        if self.par.tk.tok == 'D_INSTSP' \
                and self.par.tok_list_in[self.par.index + 1].tok != 'NEWLINE':
            self.par.tk.tok = 'C_CALINS'
            return '', None

        # Convert generic identifier to call identifier if after _
        if self.par.tk.tok == 'D_IDNTTP' \
                and self.par.tok_list_out[-1].tok == 'C_CALINS':
            self.par.tk.tok = 'C_CALIDF'
            return '', None

        return '', None

    # Pass 2 ------------------------------------------------------------------
    def pass_2(self):
        '''Parser Tokens processing'''
        return '', None

    # Pass 3 ------------------------------------------------------------------
    def pass_3(self):
        '''Parser Tokens processing'''

        # Replace long named variables for short named ones
        # Here to account for different classic variable needs
        if self.par.tk.tok == 'D_IDNTTP':
            response, new_var = self.get_short_var(self.par.tk)

            if response:
                return response, None

            self.par.tk.val = new_var

        return '', None

    # Pass 4 ------------------------------------------------------------------
    def pass_4(self):
        '''Parser Tokens processing'''

        return '', None

    # Pass 5 ------------------------------------------------------------------
    def pass_5(self):
        '''Parser Tokens processing'''

        # Convert ? to print or vice versa
        if self.par.tk.tok == 'C_INSTRC' \
                and (self.par.tk.val == '?'
                     or self.par.tk.uval == 'PRINT') \
                and self.stg.convert_print:

            if self.stg.convert_print == '?':
                self.par.tk.val = self.des.c_print_alt
            else:
                self.par.tk.val = self.des.c_print_ins

            return '', self.par.tk

        # Strip THEN before GOTO
        elif self.stg.strip_then_goto == 'T' \
            and self.par.tk.tok == 'C_JUMPIN' \
            and self.par.tk.uval == 'THEN' \
                and self.par.tok_list_in[self.par.index + 1].uval == 'GOTO':
            return None, None

        # Strip GOTO after THEN/ELSE
        elif self.stg.strip_then_goto == 'G' \
            and self.par.tk.tok == 'C_JUMPIN' \
            and self.par.tk.uval == 'GOTO' \
            and (self.par.tok_list_out[-1].uval == 'THEN'
                 or self.par.tok_list_out[-1].uval == 'ELSE'):
            return None, None

        # Replace unary and assignment operator
        elif self.par.tk.tok == 'C_E_SYMB':
            operand_tok = self.par.tok_list_out[-1]
            operator_val = self.par.tk.val
            self.par.tok_list_out.extend(self.par.tok_str('='))
            self.par.tok_list_out.append(operand_tok)
            self.par.tok_list_out.extend(self.par.tok_str(operator_val[0]))
            if operator_val.count(operator_val[0]) == len(operator_val):
                self.par.tok_list_out.extend(self.par.tok_str('1'))
            return None, None

        # Replace true and false
        elif self.par.tk.tok == 'D_OPERAT':
            if self.par.tk.uval == 'FALSE':
                self.par.tok_list_out.extend(self.par.tok_str('0'))
                return None, None
            elif self.par.tk.uval == 'TRUE':
                self.par.tok_list_out.extend(self.par.tok_str('-1'))
                return None, None

        # Translate unicode characters to ASCII equivalent
        elif self.stg.translate \
                and self.par.tk.tok in self.des.c_lit_toks:
            self.par.tk.val = self.trans_char(self.par.tk.val)
            self.par.tok_list_out.append(self.par.tk)
            return None, None

        return '', None

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

        return '', None

    # Methods -----------------------------------------------------------------
    def get_short_var(self, tk):
        '''Transform long named variables into short, two characters, ones'''
        g = re.match(self.des.d_idnttp_grp, tk.lval)
        long_var = g.group(1)
        var_type = g.group(2)

        if long_var in self.des.c_reserved_kw:
            return ('log', [1, f'Reserved keyword: '
                               f'{long_var}', tk]), tk.val

        elif self.par.tok_list_out[-1].val == self.des.d_keepid:
            if len(long_var) <= 2:
                return ('log', [1, f'Can´t use {self.des.d_keepid} '
                                   f'on a short named variable: '
                                   f'{long_var}', tk]), tk.val

            self.par.tok_list_out.pop()
            return '', tk.val

        elif len(long_var) <= 2:
            if long_var in self.des.c_used_short_vars \
                    and long_var not in self.des.c_pure_short_vars:

                for key, value in self.des.d_declares.items():
                    if long_var == value:
                        break

                return ('log', [1, f'Short name already assigned: '
                                   f'{long_var} {key}', tk]), tk.val
            if len(long_var) == 2:
                self.des.c_used_short_vars.update({long_var})
                self.des.c_pure_short_vars.update({long_var})

            return None, tk.val

        short_var = '--'
        if long_var in self.des.d_declares:
            return None, self.des.d_declares[long_var] + var_type

        while self.var_index > 0:
            # get xx format by decomposing 676 in two base 26 digits (a-z)
            self.var_index -= 1
            idx_h = int(self.var_index / 26)
            idx_l = round(self.var_index % 26)
            short_var = self.des.c_var_chr[idx_h] + self.des.c_var_chr[idx_l]

            if short_var not in self.des.c_used_short_vars:
                self.des.d_declares[long_var] = short_var
                self.des.c_used_short_vars.update({short_var})
                return None, short_var + var_type

        return ('log', [1, f'Too many variable names used: '
                           f'{self.var_index}', self.par.tk]), None

    def trans_char(self, text):
        '''Convert unicode characters into ASCII equivalents'''
        # ☺☻♥♦♣♠·◘○◙♂♀♪♬☼┿┴┬┤├┼│─┌┐└┘╳╱╲╂
        replacements = {'☺': 'A', '☻': 'B', '♥': 'C', '♦': 'D', '♣': 'E', '♠': 'F',
                        '·': 'G', '◘': 'H', '○': 'I', '◙': 'J', '♂': 'K', '♀': 'L',
                        '♪': 'M', '♬': 'N', '☼': 'O', '┿': 'P', '┴': 'Q', '┬': 'R',
                        '┤': 'S', '├': 'T', '┼': 'U', '│': 'V', '─': 'W', '┌': 'X',
                        '┐': 'Y', '└': 'Z', '┘': '[', '╳': ']', '╱': '\\', '╲': '^',
                        '╂': '_'}

        text = ''.join([replacements.get(c, c) for c in text])

        original = 'ÇüéâäàåçêëèïîìÄÅÉæÆôöòûùÿÖÜ¢£¥₧ƒáíóúñÑªº¿⌐¬½¼¡«»ÃãĨĩÕõŨũĲĳ¾∽◇‰¶§▂▚▆▔◾▇▎▞▊▕▉▨▧▼▲▶◀⧗⧓▘▗▝▖▒Δǂω█▄▌▐▀αβΓπΣσμτΦθΩδ∞φ∈∩≡±≥≤⌠⌡÷≈°∙‐√ⁿ²❚■'
        translat = ('\u0080\u0081\u0082\u0083\u0084\u0085\u0086\u0087\u0088\u0089\u008A\u008B\u008C\u008D\u008E\u008F'
                    '\u0090\u0091\u0092\u0093\u0094\u0095\u0096\u0097\u0098\u0099\u009A\u009B\u009C\u009D\u009E\u009F'
                    '\u00A0\u00A1\u00A2\u00A3\u00A4\u00A5\u00A6\u00A7\u00A8\u00A9\u00AA\u00AB\u00AC\u00AD\u00AE\u00AF'
                    '\u00B0\u00B1\u00B2\u00B3\u00B4\u00B5\u00B6\u00B7\u00B8\u00B9\u00BA\u00BB\u00BC\u00BD\u00BE\u00BF'
                    '\u00C0\u00C1\u00C2\u00C3\u00C4\u00C5\u00C6\u00C7\u00C8\u00C9\u00CA\u00CB\u00CC\u00CD\u00CE\u00CF'
                    '\u00D0\u00D1\u00D2\u00D3\u00D4\u00D5\u00D6\u00D7\u00D8\u00D9\u00DA\u00DB\u00DC\u00DD\u00DE\u00DF'
                    '\u00E0\u00E1\u00E2\u00E3\u00E4\u00E5\u00E6\u00E7\u00E8\u00E9\u00EA\u00EB\u00EC\u00ED\u00EE\u00EF'
                    '\u00F0\u00F1\u00F2\u00F3\u00F4\u00F5\u00F6\u00F7\u00F8\u00F9\u00FA\u00FB\u00FC\u00FD\u00FE\u00FF')

        translation = text.maketrans(original, translat)
        text = text.translate(translation)

        return text


class Tokenize():
    def __init__(self, stg):
        self.stg = stg

    def tokenize(self):
        self.TOK_EXISTS = TOK_EXISTS
        if self.TOK_EXISTS:
            tok = Tokenizer.Main()
            tok.stg.binary_ext = self.stg.binary_ext
            tok.stg.list_ext = self.stg.list_ext
            tok.stg.export_list = self.stg.export_list
            if 'A' not in self.stg.output_format:
                tok.stg.delete_original = True
            tok.stg.init(external=[self.stg.file_save])
            tok.execute()
