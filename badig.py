#!/usr/bin/env python3

'''
Basic Dignified
v2.0
A modern take on 8 bit classic Basics
Support for any classic Basic though description modules

Copyright (C) 2018-2022 - Fred Rique (farique)
https://github.com/farique1/basic-dignified

The complete suite includes:
Syntax Highlight, Theme, Build System, Comment Preference and Auto Completion
    for Sublime Text 3 and 4
Tokenizers for some systems.
Basic DignifieR
    Convert classic Basic to Dignified format

badig.py <source> <destination> [args...]
badig.py -h for help.
'''

# Standard libraries
import re
import sys
import time
import os.path
from collections import namedtuple, defaultdict

# Custom modules
from support.helper import IO
from support.helper import Infolog
from support.badig_settings import Settings

# if coming from a module
# pass the file name as argument to the init() method
# Badig is not being called by a module anymore
# But it is left here in case it's needed
external = None
if __name__ != '__main__':
    external = [os.path.basename(sys.argv[1])]

# Initialize settings
stg = Settings()
stg.init(external)

# Classic modules
Classic = stg.Classic
Tools = stg.Tools

# Dignified module
Dignified = stg.Dignified

# Initlalize Infolog
infolog = Infolog()

# Apply verbose
infolog.level = stg.verbose_level


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


# Language descriptions -------------------------------------------------------
class Description(Dignified.Description, Classic.Description):
    '''Describes the classic and dignified versions of Basic
    Mix Dignified and Classic modules and adds global descriptions'''

    def __init__(self):
        super(Description, self).__init__()

        # General
        self.tab = r'\t'
        self.space = r'\s'
        self.newline = r'\r'
        self.newline_str = '\r'
        self.newline_classic = '\r\n'

        if stg.CURRENT_SYSTEM == 'WINDOWS':
            self.newline_str_n = '\n'
        else:
            self.newline_str_n = '\r'

        # General groups
        m_eof = r'^EOF$'
        m_newline = r'^\r+$'
        m_spaces = r'^[^\S\r\n]$'

        # Regex groups
        main_eof = fr'(?P<eof>{m_eof})'
        main_new = fr'(?P<newline>{m_newline})'
        main_spc = fr'(?P<spaces>{m_spaces})'

        # Groups assembled for compiling (Order is important)
        self.main_groups = (''
                            fr'{main_eof}|'
                            fr'{main_new}|'
                            fr'{main_spc}')

        # Compiling all groups (Order is important)
        self.commands = re.compile(''
                                   fr'{self.main_groups}|'
                                   fr'{self.dignified_groups}|'
                                   fr'{self.classic_groups}|'
                                   fr'{self.d_idnttp}',
                                   re.I)

    def join_commands(self, *args):
        '''Join list items with individual regex terminators'''
        l = []
        [l.extend(a) for a in args]
        l = r'$|^'.join(l)
        return fr'(^{l}$)'


# Token -----------------------------------------------------------------------
class Token:
    '''Define and creates the token object
       tok = Token type
       val = Token value
       pos = Position object'''

    def __init__(self, tok='', val=None, pos=None):
        self.tok = tok
        self.val = val
        self.pos = pos

        self.c_idnttp_grp = Description().c_idnttp_grp

        if self.tok:
            self.tok = self.tok.upper()

    @property
    def uval(self):
        '''Create an uppercase value'''
        return str(self.val).upper()

    @property
    def lval(self):
        '''Create a lowercase value'''
        return str(self.val).lower()

    @property
    def var_name(self):
        '''Give variable identifier'''
        g = re.match(self.c_idnttp_grp, self.val)
        var_name = g.group(1)
        return str(var_name).lower()

    @property
    def val_w_file(self):
        '''Give variable + file name'''
        val_w_file = self.var_name
        val_w_file += f'@{self.pos.file}'
        return str(val_w_file).lower()

    @property
    def var_type(self):
        '''Give variable type'''
        g = re.match(self.c_idnttp_grp, self.val)
        var_type = g.group(2)
        return str(var_type).lower()

    def copy(self):
        '''Make a copy of the object'''
        return Token(self.tok, val=self.val, pos=self.pos.copy())

    def __repr__(self):
        '''Nicer way of representing the object information'''
        # 1 show the file, 0 hide it
        file = '' if 1 else f' --------- {os.path.basename(self.pos.file)}'
        return (''
                f'{self.pos.lin:02} | '
                f'{self.pos.col:02} | '
                f'{self.tok} | '
                f'{repr(str(self.val))[1:-1]}'
                f'{file}')


# Position --------------------------------------------------------------------
class Position:
    '''Define and create the positional information object for the token
       d_code = The code listing
       lin = Line position
       col = Column position
       offset = Amount to compensate for leading spaces
                when displaying the position glyph on error messages'''

    def __init__(self, d_code, lin=0, col=0, offset=0):
        self.lin = lin
        self.col = col + 1  # Columns start with 1, not 0
        self.d_code = d_code
        self.offset = offset

        self.text = d_code[self.lin].text
        self.file = d_code[self.lin].file
        self.code_len = len(d_code)

    def __repr__(self):
        '''Nicer way for representing the object information'''

        return (f'{self.lin:02} | '
                f'{self.col:02} | '
                f'{self.text.rstrip()} | '
                f'{self.file} | '
                f'{self.code_len}')

    def copy(self, d_code=None, lin=None, col=None, offset=None):
        '''Makes a copy of the object'''

        lin = self.lin if lin is None else lin
        col = self.col if col is None else col
        lead_spc = (len(self.text) - len(self.text.lstrip()))
        offset = lead_spc if offset is None else offset
        d_code = self.d_code if d_code is None else d_code

        return Position(d_code=d_code, lin=lin, col=col, offset=offset)


# Lexer -----------------------------------------------------------------------
class Lexer:
    '''Scanner to read the text file and create the tokens
       stg = Settings object
       d_code = File to process'''

    def __init__(self, stg, d_code):
        self.d_code = d_code
        self.stg = stg
        self.des = Description()
        self.pos = Position(d_code, lin=0, col=-1)

        # Run classic module lexer initialization
        self.clc = Classic.Lexer(self, self.stg, Token)
        self.clc.initialization()

    # General -----------------------------------------------------------------
    def advance(self):
        '''Read the current character and advance the cursor'''

        current_char = self.pos.text[self.pos.col]
        self.pos.col += 1
        if self.pos.col >= len(self.pos.text):
            self.advance_line()
        return current_char

    def advance_line(self):
        '''Advance one line and prepare it for processing'''

        self.pos.lin += 1
        self.pos.col = 0
        nl = self.des.newline_str

        if self.pos.lin <= self.pos.code_len - 1:
            self.pos.text = self.d_code[self.pos.lin].text.rstrip() + nl
            return self.pos.text

    def lookahead(self):
        '''Look at the current character without advancing'''

        return self.pos.text[self.pos.col]

    def get_token(self):
        '''Makes a token based on the word or character matched.
        Get characters until no match is found
        then uses the last positive match'''

        partial = ''
        match_group = ''
        last_pos = self.pos.copy()

        while True:
            next_char = self.lookahead()
            g = self.des.commands.match(partial + next_char)

            if not g:
                if not partial:
                    match_group = None
                    partial = next_char
                return Token(tok=match_group,
                             val=partial.strip(' '),
                             pos=last_pos)

            partial += self.advance()
            match_group = g.lastgroup

    # Literals ----------------------------------------------------------------
    def get_lit_block(self, tk):
        '''Get a classic comment block
           tk = Initial token'''

        partial = ''
        rem_block = [tk]
        val_len = len(tk.val)
        nl = self.des.newline
        nls = self.des.newline_str

        if not self.pos.text[self.pos.col + 1:]:
            self.advance_line()
            self.pos.col -= 1

        last_pos_lit = self.pos.copy(col=max(self.pos.col, 0))

        while True:
            partial += self.advance()
            next_char = self.lookahead()
            last_pos_close = self.pos.copy(col=self.pos.col - (val_len))

            if re.match(nl, next_char):

                g = re.match(tk.val, partial[-val_len:])
                if g:
                    partial = partial[:-val_len]
                partial = partial.strip(nls)

                # if not alone in a line with a comment block indicator
                if not (not partial[:-val_len].strip() and g):
                    rem_block.append(Token(tok='C_LIBREM',
                                           val=partial,
                                           pos=last_pos_lit))

                if g:
                    rem_block.append(Token(tok='C_C_BREM',
                                           val=tk.val,
                                           pos=last_pos_close))
                    break

                if self.pos.lin + 1 >= self.pos.code_len:
                    return None

                last_pos_lit = self.pos.copy(lin=self.pos.lin + 1, col=0)
                partial = ''

        if tk.tok == 'D_O_EREM':
            rem_block = []

        return rem_block

    def get_lit_line(self, tok, end, part, l_pos):
        '''Get a literal line of type depending on passed arguments
           tok = Token of the matched literal
           end = A character to end the capture
           part = First part of the literal string
           l_pos = Start position of the string'''

        nl = self.des.newline
        nls = self.des.newline_str

        if self.lookahead() == nls:
            return None

        while True:
            last_chr = self.advance()
            part += last_chr
            next_chr = self.lookahead()

            g = re.match(fr'{end}|{nl}', next_chr)
            if g:
                if g.group() != nls:
                    part = part + self.advance()
                break

        return Token(tok=tok,
                     val=part,
                     pos=l_pos)

    # Process -----------------------------------------------------------------
    def lex(self):
        '''Go through the code, get the tokens, adjust them and outputs a list'''

        # Create the token list header
        self.tk = Token('NEWLINE', self.des.newline_str, self.pos.copy())
        self.lexer = [Token('PROGRAM', 'PROGRAM', self.pos.copy()), self.tk]
        self.last_tok = self.tk

        self.advance_line()
        while True:

            self.last_tok = self.lexer[-1]
            self.tk = self.get_token()

            if not self.tk.val:
                continue

            # Errors ----------------------------------------------------------
            # Character not recognized at that location
            if not self.tk.tok:
                Info.log(1, f'Character not recognized in this context: '
                            f'{self.tk.val}', self.tk)

            # Unfinished part of potential matches
            elif self.tk.tok == 'C_PARTLS' or self.tk.tok == 'D_PARTLS':
                Info.log(1, f'Token incomplete: {self.tk.val}', self.tk)

            # Fix toggle rems not at the start of a line
            # convert to correct tokens of # and ident/number
            if self.tk.tok == 'D_TGLREM' \
                    and self.lexer[-1].tok != 'NEWLINE' \
                    and self.lexer[-1].tok != 'D_TGLREM' \
                    and self.lexer[-1].tok != 'D_INSTRC':

                g = re.match(self.des.d_togremchk, self.tk.val)

                tok = self.des.commands.match(g.group(1))
                self.lexer.append(Token(tok=tok.lastgroup,
                                        val=g.group(1),
                                        pos=self.pos.copy()))

                tok = self.des.commands.match(g.group(2))
                self.tk = (Token(tok=tok.lastgroup,
                                 val=g.group(2),
                                 pos=self.pos.copy()))

            # Literal blocks --------------------------------------------------
            elif (self.tk.tok == 'C_O_BREM' or self.tk.tok == 'D_O_EREM') \
                    and self.last_tok.tok == 'NEWLINE':
                last_tok = self.tk.copy()
                rem_block = self.get_lit_block(self.tk)

                if rem_block is None:
                    Info.log(1, f'Block not closed from: {self.tk.val}', last_tok)

                self.lexer.extend(rem_block)

                continue

            # Literal lines ---------------------------------------------------
            # Dignified exclusive rems
            elif self.tk.tok == 'D_LINREM':
                self.pos.col = len(self.pos.text) - 1
                continue

            # Classic line rems (comment block indicator not at the start of a line)
            elif self.tk.tok == 'C_O_BREM' and self.last_tok.tok != 'NEWLINE':

                self.lexer.append(Token(tok='C_LINREM',
                                        val=self.des.c_altrem,
                                        pos=self.pos.copy(col=self.pos.col - 2)))

                self.tk = self.get_lit_line(tok='C_LITREM',
                                            end=self.des.newline,
                                            part=self.des.c_altrem,
                                            l_pos=self.pos.copy(col=self.pos.col - 1))

            # Classic line rems
            elif self.tk.tok == 'C_LINREM':
                self.lexer.append(self.tk)
                lit_rem = self.get_lit_line(tok='C_LITREM',
                                            end=self.des.newline,
                                            part='',
                                            l_pos=self.pos.copy(col=self.pos.col))

                if not lit_rem:
                    continue

                self.tk = lit_rem

            # Quotes
            elif self.tk.tok == 'C_QUOTES':
                self.pos.col -= 1
                self.tk = self.get_lit_line(tok='C_LITQUO',
                                            end=self.des.c_quotes,
                                            part='',
                                            l_pos=self.pos.copy(col=self.pos.col))

            # Classic module functions ----------------------------------------
            # Lex functions on the classic module
            # and deal with their response
            else:
                ctk = self.clc.lexing()
                if ctk is None:
                    continue
                elif ctk:
                    self.tk = ctk

            # Create list -----------------------------------------------------
            self.lexer.append(self.tk)

            # EOF -------------------------------------------------------------
            if self.tk.tok == 'EOF':
                break

        return self.lexer


# Parser ----------------------------------------------------------------------
class Parser:
    '''Process the list of tokens sent by the lexer
       stg = Setings object
       lexed = List of tokens
       des = Language description object
       short_vars = List of short named vars used
                    (prevent conflict on included files)'''

    def __init__(self, stg, lexed, des, include_vars):
        self.tok_list_in = lexed
        self.stg = stg
        self.reset_pass()
        self.des = des
        self.des.c_hard_short_vars.update(include_vars[0])
        self.des.c_hard_long_vars.update(include_vars[1])
        self.des.d_declares.update(include_vars[2])

        # Run initialization on the classic module
        self.clc = Classic.Parser(self, stg, Token)
        self.clc.initialization()

    def reset_pass(self):
        '''Reset the variables to prepare for another pass at the token list'''

        self.len = len(self.tok_list_in)
        self.index = 0
        self.tk = self.tok_list_in[0]
        self.tk.pos.lin = 0
        self.tk.pos.col = 1
        self.tok_list_out = [self.tk]

    def next_tok(self):
        '''Advance and get the next token on the token list'''

        if self.index + 1 <= self.len:
            self.index += 1

        self.tk = self.tok_list_in[self.index]

        return self.tk

    def prev_tok(self):
        '''Recede and get the previous token on the token list'''

        if self.index - 1 > 0:
            self.index -= 1

        self.tk = self.tok_list_in[self.index]

        return self.tk

    def peek_ahead(self, offset=1):
        '''Get the next token in the input list without advancing'''

        return self.tok_list_in[self.index + offset]

    def last_tok(self, offset=-1):
        '''Get the last token on the output list'''

        return self.tok_list_out[offset]

    # Defines -----------------------------------------------------------------
    def get_defines(self):
        '''Get the defines definitions'''

        do = self.des.d_defdop
        dc = self.des.d_defdcl
        se = self.des.d_defsep
        def_grp = namedtuple('def_grp', 'repl varv')

        while True:
            self.next_tok()
            def_def = self.get_in_bracket(f'{do}{dc}')

            if not def_def:
                self.prev_tok()
                Info.log(1, f'Define definition blank.', self.tk)

            if not re.match(self.des.d_identf, def_def.val):
                Info.log(1, f'Invalid define name: {def_def.val}', def_def)

            def_var = None
            def_rep = self.get_defined_content(f'{do}{dc}', 2)
            if def_rep[1]:
                def_var = def_rep[1][0][0]

            def_rep = def_rep[0]
            if def_def.lval in self.des.d_defines:
                Info.log(1, f'Define name duplicated: {def_def.val}', def_def)

            self.des.d_defines[def_def.lval] = (def_grp(def_rep, def_var))

            tk = self.next_tok()
            if tk.val != se:
                if tk.tok != 'NEWLINE':
                    Info.log(1, f'Expecting: {se}', self.tk)
                break

    def get_defined_content(self, delim, recur=1):
        '''Get the content of the defined define and its variable if any
           delim = Open and closing characters delimiting the content
           recur = Recursions before delimiter character balance error'''

        assert len(delim) == 2
        do = delim[0]
        dc = delim[1]

        if self.tk.val != do:
            Info.log(1, f'Expecting: {do}', self.tk)

        var = []
        part = []
        balance = [do]

        while True:

            tk = self.next_tok()
            if tk.tok == 'NEWLINE' and balance:
                Info.log(1, f'Unbalanced {do}{dc}', self.tk)

            elif tk.val == do:
                if len(balance) >= recur:
                    Info.log(1, f'Too many opened "{do}"', self.tk)

                balance.append(do)
                pos = self.tk.pos
                var.append(self.get_defined_content(f'{do}{dc}'))
                part.append(Token(tok='D_DEFVAR',
                                  val='VAR',
                                  pos=pos))
                self.prev_tok()

                continue

            elif tk.val == dc:
                if not balance:
                    Info.log(1, f'Too many closed "{dc}"', self.tk)

                balance.pop()

                if not balance:
                    return part, var

                continue

            part.append(tk)

    def replace_define(self):
        '''Replace the defines for their content throughout the code'''

        do = self.des.d_defdop
        dc = self.des.d_defdcl
        vo = self.des.d_defvop
        vc = self.des.d_defvcl
        define = []
        def_var = []
        balance = [vo]

        def_def = self.get_in_bracket(f'{do}{dc}')
        if not def_def:
            Info.log(1, f'Define blank.', self.tk)

        if not def_def.lval.replace(self.des.d_idsnake, '').isalnum() \
                and def_def.lval != self.des.c_print_alt:
            Info.log(1, f'{def_def.val} invalid define name.', def_def)

        if def_def.lval not in self.des.d_defines:
            Info.log(1, f'{def_def.val} define not defined.', def_def)

        if self.tk.tok == 'C_SYMBOL' and self.tk.val == vo:
            while True:

                tk = self.next_tok()
                if tk.tok == 'NEWLINE' and balance:
                    Info.log(1, f'Missing {vc}', tk)

                # If define has variable, recurse it
                elif tk.val == do:
                    def_var.extend(self.replace_define())
                    continue

                elif tk.val == vo:
                    balance.append(tk.val)

                elif tk.val == vc:
                    balance.pop()
                    if not balance:
                        break

                def_var.append(tk)

            self.next_tok()

        insert_var = self.des.d_defines[def_def.lval].varv
        if def_var:
            insert_var = def_var

        for d in self.des.d_defines[def_def.lval].repl:
            if d.tok == 'D_DEFVAR':
                for v in insert_var:
                    define.append(v.copy())

                continue

            d.pos.lin = def_def.pos.lin
            d.pos.col = def_def.pos.col
            define.append(d.copy())

        self.prev_tok()

        return define

    # Declares ----------------------------------------------------------------
    def get_declares(self):
        '''Get the declares definitions'''

        vc = self.des.c_var_valid_chars

        while True:

            # Get long variable
            dec_long = self.next_tok()

            if not re.match(self.des.d_identf, dec_long.lval):
                Info.log(1, f'Invalid declared variable: {dec_long.val}', dec_long)

            if len(dec_long.lval) == 1:
                Info.log(1, f'Declared variable too short: {dec_long.lval}', dec_long)

            if dec_long.uval in self.des.c_reserved_kw:
                Info.log(1, f'Variable is a reserved keyword: {dec_long.lval}', dec_long)

            # If there is no assignment (:)
            if self.peek_ahead().val == self.des.d_decsep \
                    or self.peek_ahead().tok == 'NEWLINE':

                for var in self.des.d_declares:
                    val_n_file = var.split('@')[0]
                    if dec_long.lval[:vc] == self.des.d_declares[var]:
                        Info.log(2, f'Declared variable conflict: '
                                    f'{dec_long.lval} '
                                    f'{val_n_file}:{self.des.d_declares[var]}', dec_long)
                    if dec_long.val_w_file == var:
                        Info.log(1, f'Long variable already reserved: '
                                    f'{dec_long.lval} '
                                    f'{val_n_file}:{self.des.d_declares[var]}', dec_long)

                for var in self.des.c_hard_long_vars:
                    if dec_long.lval[:vc] == var.var_name[:vc]:
                        Info.log(2, f'Reserved long variable conflict: '
                                    f'{dec_long.lval} {var.var_name}', dec_long)

                for var in self.des.c_hard_short_vars:
                    if dec_long.lval[:vc] == var:
                        Info.log(2, f'Reserved short variable conflict: '
                                    f'{dec_long.lval} {var}', dec_long)

                if len(dec_long.lval) == vc:
                    self.des.c_hard_short_vars.update({dec_long.lval})
                else:
                    self.des.c_hard_long_vars.update({dec_long})

                if self.peek_ahead().tok == 'NEWLINE':
                    break

                if self.peek_ahead().val == self.des.d_decsep:
                    self.next_tok()
                    continue

            self.next_tok()

            # Get short variable
            dec_short = self.next_tok()

            if not re.match(self.des.c_varsna, dec_short.lval):
                Info.log(1, f'Invalid declared short variable: {dec_short.lval}', dec_short)

            for var in self.des.d_declares:
                val_n_file = var.split('@')[0]
                if dec_long.val_w_file == var:
                    Info.log(1, f'Long variable already declared: '
                                f'{dec_long.lval}:{dec_short.lval} '
                                f'{val_n_file}:{self.des.d_declares[var]}', dec_short)
                if dec_short.lval == self.des.d_declares[var]:
                    Info.log(1, f'Short variable already declared: '
                                f'{dec_long.lval}:{dec_short.lval} '
                                f'{val_n_file}:{self.des.d_declares[var]}', dec_short)

            for var in self.des.c_hard_long_vars:
                if dec_long.val_w_file == var.val_w_file:
                    Info.log(1, f'Long variable already reserved: '
                                f'{dec_long.lval}:{dec_short.lval} '
                                f'{var.lval}', dec_long)

            for var in self.des.c_hard_long_vars:
                if dec_short.lval == var.var_name[:vc]:
                    Info.log(2, f'Reserved long variable conflict: '
                                f'{dec_long.lval}:{dec_short.lval} '
                                f'{var.var_name}', dec_short)

            for var in self.des.c_hard_short_vars:
                if dec_short.lval == var:
                    Info.log(2, f'Reserved short variable conflict: '
                                f'{dec_long.lval}:{dec_short.lval} '
                                f'{var}', dec_short)

            self.des.d_declares[dec_long.val_w_file] = dec_short.lval

            tk = self.next_tok()
            if tk.val != self.des.d_decsep:
                if tk.tok != 'NEWLINE':
                    Info.log(1, f'Expecting: {self.des.d_decsep}', self.tk)
                break

    # Labels ------------------------------------------------------------------
    def get_label_lines(self):
        '''Get line and loop labels'''

        label = None
        lo = self.des.d_labdop
        lc = self.des.d_labdcl

        # line labels
        if self.last_tok().tok == 'NEWLINE':
            label = self.get_in_bracket(f'{lo}{lc}')
            self.prev_tok()

        # Loop labels
        elif self.last_tok(-2).tok == 'NEWLINE':
            label = self.last_tok()
            self.loop_labels.append(label)
            self.tok_list_out.pop()

        if label is None:
            Info.log(1, f'Label error.', self.tk)

        if not label:
            Info.log(1, f'Label blank.', self.tk)

        if not re.match(self.des.d_identf, label.val):
            Info.log(1, f'Invalid label name: {label.val}', label)

        self.tk = Token(tok='D_LBLLIN',
                        val=label.lval,
                        pos=self.tk.pos)

    def get_jump_labels(self):
        '''Get labels on jump instructions'''

        lo = self.des.d_labdop
        lc = self.des.d_labdcl
        goto = self.get_in_bracket(f'{lo}{lc}')

        self.prev_tok()

        tk_pos = self.peek_ahead(-1).pos
        self.tk = Token(tok='D_LBLJMP',
                        val=goto.lval,
                        pos=tk_pos)

    def get_loop_label_return(self):
        '''Get loop labels return'''

        if not self.loop_labels:
            Info.log(1, f'Loop label close without open.', self.tk)

        label = self.loop_labels.pop()

        # Add : if } not at the start of a line
        if self.last_tok().tok != 'NEWLINE' \
                and self.last_tok().tok != 'C_INSTSP':
            self.tok_list_out.extend(self.tok_str(self.des.c_instsp_str))

        self.tok_list_out.extend(self.tok_str(self.des.c_loop_back))

        self.tk = Token(tok='D_LBLRET',
                        val=label.lval,
                        pos=self.tk.pos)

    def get_labels_exit(self):
        '''Get loop labels exit'''

        self.tok_list_out.extend(self.tok_str(self.des.c_loop_back))

        self.tk = Token(tok='D_LBLEXT',
                        val=self.loop_labels[-1].lval,
                        pos=self.tk.pos)

    # Helper function ---------------------------------------------------------
    def get_in_bracket(self, delim):
        '''Get content inside delimiters.
           delim: Opening and closing delimiter characters'''

        assert len(delim) == 2
        do = delim[0]
        dc = delim[1]

        if self.tk.val != do:
            Info.log(1, f'Expecting: {do}', self.tk)

        content = self.next_tok()
        if content.val == dc:
            return ''

        if self.next_tok().val != dc:
            Info.log(1, f'Closing "{dc}" not found.', self.tk)

        self.next_tok()

        return content

    # Functions ---------------------------------------------------------------
    def get_func_def(self):
        '''Get function definitions and its arguments'''

        fe = self.des.d_funcequal

        func = self.next_tok()
        if self.in_func:
            Info.log(1, f'Already inside a function.', self.in_func)

        if func.lval in self.des.d_functions:
            Info.log(1, f'Function name duplicated: {func.val}', func)

        func_def_args_tmp = self.get_func_args(func)
        self.func_def_args = []  # this is the a in: func(a=b)
        self.func_def_equl = []  # this is the b in: func(a=b)

        for args in func_def_args_tmp:
            new_equ = []
            new_arg = args

            if not args:
                Info.log(1, f'Function definition missing  argument: '
                            f'{func.val}', func)

            if args[0].tok != 'D_IDNTTP':
                Info.log(1, f'Function definition only takes variables: '
                            f'{args[0].val}', args[0])

            if len(args) > 1:
                if args[1].val != fe:
                    Info.log(1, f'Function definition only takes one variable: '
                                f'{args[1].val}', args[1])

                new_arg = [args[0]]
                new_equ = args[2:]

            self.func_def_args.append(new_arg)
            self.func_def_equl.append(new_equ)

        if not all(i for i in self.func_def_args):
            Info.log(1, f'Empty argument in function definition.', func)

        self.tk.pos.col = 1
        self.tk = Token(tok='D_FUNCDF',
                        val=func.lval,
                        pos=self.tk.pos.copy())

        self.in_func = func

    def get_func_ret(self):
        '''Get function return and its variables'''

        ret_tok = []
        ret_list = []
        last_ret_tok = self.tk
        fs = self.des.d_funcsep
        ar = self.des.c_altrem
        func_def = namedtuple('func_def', 'args rets equl')

        if not self.in_func:
            Info.log(1, f'Ret without function.', self.tk)

        tk = self.peek_ahead()
        if tk.val != ar and tk.tok != 'C_INSTSP' and tk.tok != 'NEWLINE':
            while True:
                tk = self.next_tok()

                if tk.val == fs:
                    ret_list.append(ret_tok)
                    ret_tok = []
                    continue

                if tk.val == ar or tk.tok == 'C_INSTSP' or tk.tok == 'NEWLINE':
                    ret_list.append(ret_tok)
                    self.prev_tok()
                    break

                ret_tok.append(tk)

        if not all(i for i in ret_list):
            Info.log(1, f'Function return missing variable.', last_ret_tok)

        self.tk = self.tok_str(self.des.c_func_ret)[0]
        self.des.d_functions[self.in_func.lval] = func_def(self.func_def_args, ret_list, self.func_def_equl)
        self.in_func = None

    def replace_func_calls(self):
        '''Replace the dignified function calls for the classic format'''

        se = self.des.c_instsp_str
        dw = self.des.c_func_stop_kw
        fs = self.des.d_funcsep
        fe = self.des.d_funcequal
        func = self.tk
        equ_tok = self.tok_str(self.des.c_equal)[0]
        ins_tok = self.tok_str(self.des.c_instsp_str)[0]
        fcl_tok = self.tok_str(self.des.c_func_call)[0]
        fun_tok = Token(tok='D_FUNCAL',
                        val=func.lval,
                        pos=func.pos)

        if func.lval not in self.des.d_functions:
            Info.log(1, f'Function not defined: {func.val}', func)

        cal_vars = []
        var_tok = []

        # If function call has variables
        if self.last_tok().val == fe:
            last_index = self.index
            self.prev_tok()

            # Scan back looking for variables then invert the list
            while True:
                tk = self.prev_tok()
                self.tok_list_out.pop()

                if tk.val == fs:
                    cal_vars.append(var_tok[::-1])
                    var_tok = []
                    continue

                if self.tk.tok == 'NEWLINE' or self.tk.val == se \
                        or self.tk.uval in dw:
                    cal_vars.append(var_tok[::-1])
                    self.prev_tok()
                    break

                var_tok.append(tk)

            self.index = last_index
            cal_vars = cal_vars[::-1]

        for var in cal_vars:

            if not var:
                continue

            if var[0].tok != 'D_IDNTTP':
                Info.log(1, f'Function definition only takes variables: '
                            f'{var[0].val}', var[0])

            if len(var) > 1:
                Info.log(1, f'Function definition only takes one variable: '
                            f'{var[1].val}', var[1])

        cal_args = self.get_func_args(func)
        # cal_equl = self.func_def_equl
        def_args = self.des.d_functions[func.lval].args
        def_rets = self.des.d_functions[func.lval].rets
        cal_equl = self.des.d_functions[func.lval].equl

        if len(cal_args) > len(def_args):
            Info.log(1, f'Function arguments mismatch.', func)

        if len(cal_vars) > len(def_rets):
            Info.log(1, f'Function variable mismatch.', func)

        func_call = []

        cal_args = [[]] if not cal_args else cal_args

        for d, c, e, in zip(def_args, cal_args, cal_equl):
            if not self.compare_func_args(d, c):
                if c:
                    func_call.append(d[0].copy())
                    func_call.append(equ_tok)
                    for ca in c:
                        func_call.append(ca.copy())
                    func_call.append(ins_tok)

                elif e:
                    func_call.append(d[0].copy())
                    func_call.append(equ_tok)
                    for eq in e:
                        func_call.append(eq)
                    func_call.append(ins_tok)

        func_call.append(fcl_tok)
        func_call.append(fun_tok)

        for c, d in zip(cal_vars, def_rets):
            if not self.compare_func_args(d, c):
                if c:
                    func_call.append(ins_tok)
                    func_call.append(c[0].copy())
                    func_call.append(equ_tok)
                    for de in d:
                        func_call.append(de.copy())

        return func_call

    def compare_func_args(self, args1, args2):
        '''Compare function arguments and variables
           (to remove them if they are the same)
           args1, args2 = The arguments to compare'''

        argstr1 = ' '.join([d.val for d in args1])
        argstr2 = ' '.join([d.val for d in args2])

        return argstr1 == argstr2

    def get_func_args(self, func):
        '''Get function arguments inside parenthesis
           func = The function name token'''

        fo = self.des.d_funcop
        fc = self.des.d_funccl
        fs = self.des.d_funcsep
        arg_tok = []
        balance = [fo]
        func_args = []

        if func.tok != 'D_FUNCNM':
            Info.log(1, f'Invalid function name: {func.val}', func)

        tk = self.next_tok()
        if tk.val != fo:
            Info.log(1, f'Missing {fo}', self.tk)

        if self.peek_ahead().val == fc:
            self.next_tok()
            return []

        while True:
            tk = self.next_tok()

            if tk.tok == 'NEWLINE' and balance:
                Info.log(1, f'Unbalanced {fo}{fc}', tk)

            elif tk.val == fo:
                balance.append(tk.val)

            elif tk.val == fs and len(balance) == 1:
                func_args.append(arg_tok)
                arg_tok = []
                continue

            elif tk.val == fc:
                balance.pop()
                if not balance:
                    func_args.append(arg_tok)
                    break

            arg_tok.append(tk)

        return func_args

    # Toggle rems -------------------------------------------------------------
    def get_keeps(self):
        '''Get the toggle rems definitions'''

        while True:
            keep = self.next_tok()

            if keep.tok == 'NEWLINE':
                break

            if keep.tok != 'D_TGLREM':
                Info.log(1, f'Invalid keep tag: {keep.val}', keep)

            if keep.val in self.des.d_keeps:
                Info.log(1, f'Keep tag duplicated: {keep.val}', keep)

            self.des.d_keeps.append(keep.uval)

    def toggle_lines(self):
        '''Remove toggled lines'''

        if (self.tk.uval in self.des.d_keeps
                or self.des.d_keep_all in self.des.d_keeps) \
                and self.des.d_keep_none not in self.des.d_keeps:
            return None

        tog_block = False
        toggle = self.tk

        if self.peek_ahead().tok == 'NEWLINE':
            tog_block = True

        while True:
            last_tok = self.tk
            tk = self.next_tok()

            if tk.tok == 'EOF':
                Info.log(1, f'Toggle rem not closed from {toggle.val}', toggle)

            elif tk.tok == 'NEWLINE' and not tog_block:
                break

            elif tk.tok == 'D_TGLREM' and tk.val == toggle.val \
                    and last_tok.tok == 'NEWLINE' \
                    and self.peek_ahead().tok == 'NEWLINE':
                break

    # Include -----------------------------------------------------------------
    def include_file(self):
        '''Include another file inside the code
        Go through the same process of the main file until this point'''

        qs = self.des.c_quotes
        include = self.next_tok()
        include_file = include.val.strip(qs).strip()

        if include.tok != 'C_LITQUO' or not include_file:
            Info.log(1, f'Include error: {include.val}', self.tk)

        if not os.path.isabs(include_file):
            include_file = os.path.join(self.stg.file_path, include_file)

        data_pack = namedtuple('data_pack', 'lin col offset text file')
        include = data_pack(include.pos.lin,
                            include.pos.col,
                            include.pos.offset,
                            include.pos.text,
                            include.pos.file)
        include_code = IO.load_file(include, include_file,
                                    self.stg.load_format, self.stg.tab_lenght)

        verbose = self.stg.verbose_level
        self.stg.verbose_level = 1

        lex = Lexer(self.stg, include_code)
        lexed = lex.lex()

        include_vars = (self.des.c_hard_short_vars,
                        self.des.c_hard_long_vars,
                        self.des.d_declares)

        par = Parser(self.stg, lexed, lex.des, include_vars)
        parsed, include_vars = par.par()

        self.des.c_hard_short_vars = include_vars[0]
        self.des.c_hard_long_vars = include_vars[1]
        self.des.d_declares = include_vars[2]

        if self.is_main_file():
            self.stg.verbose_level = verbose

        self.tok_list_out.extend(parsed[2:-2])

    # Rem header --------------------------------------------------------------
    def insert_rem_header(self, idx, lin, text):
        '''Add an information rem header on the final code
           idx: Token list index to insert the line
           lin: Line number for the position object
           text: Text to insert'''

        tok_rem = self.tok_str(self.des.c_altrem, pos=self.tk.pos.copy(col=0))[0]
        tok_lit = Token(tok='C_LINREM', val=text, pos=self.tk.pos.copy(col=1))
        tok_nl = self.tok_str(self.des.newline_str, pos=self.tk.pos.copy(col=len(text)))[0]

        self.tok_list_in.insert(idx, tok_rem)
        self.tok_list_in.insert(idx + 1, tok_lit)
        self.tok_list_in.insert(idx + 2, tok_nl)

        self.len = len(self.tok_list_in)

    # Helper ------------------------------------------------------------------
    def tok_str(self, text, pos=None):
        '''Makes tokens from a standalone string.
           text = The string to convert into tokens
           pos = The position object for the tokens'''

        tokens = []

        while True:
            if not pos:
                pos = self.tk.pos.copy()
                pos.col -= 1
            partial = ''
            match_group = ''
            text_in = text + ' '

            while True:
                next_char = text_in[0]

                g = self.des.commands.match(partial + next_char)
                if not g:
                    if not partial:
                        match_group = None
                        partial = next_char
                    token = Token(tok=match_group,
                                  val=partial.strip(' '),
                                  pos=pos)
                    break

                partial += next_char
                text_in = text_in[1:]
                match_group = g.lastgroup

            tokens.append(token)

            text = text[len(token.val):].strip()
            if not text:
                return tokens

    def is_main_file(self):
        '''Check if the main file is being processed.
        (avoid processing too much when including a file)'''

        return self.tok_list_out[0].pos.file == self.stg.file_load

    def par(self):
        '''Consolidate all the parser passes, limiting the access of the includes'''

        self.pass_1()
        self.pass_2()
        self.pass_3()

        # Included files do not go through the next passes
        if self.is_main_file():
            self.pass_4()
            self.pass_5()

        include_vars = (self.des.c_hard_short_vars,
                        self.des.c_hard_long_vars,
                        self.des.d_declares)

        return self.tok_list_out, include_vars

    # Pass 1 ------------------------------------------------------------------
    def pass_1(self):
        '''First parser pass
        Preparations, rem toggles, dignified instructions and replace defines'''

        Info.log(5, f'Pass 1.')

        self.in_func = None
        self.tok_list_out.append(self.next_tok())

        do = self.des.d_defdop

        while True:

            self.next_tok()

            # Rems ------------------------------------------------------------
            # Remove lines with rem toggle
            if self.tk.tok == 'D_TGLREM' \
                    and self.last_tok().tok == 'NEWLINE':
                self.toggle_lines()
                continue

            # Dignified instructions ------------------------------------------
            elif self.tk.tok == 'D_INSTRC':
                first = self.last_tok().tok == 'NEWLINE'

                d_instr = self.tk.uval
                if d_instr == 'EXIT':
                    pass

                elif d_instr == 'INCLUDE':
                    pass

                elif d_instr == 'ENDIF':
                    continue

                elif d_instr == 'DEFINE' and first:
                    self.get_defines()
                    continue

                elif d_instr == 'DECLARE' and first:
                    self.get_declares()
                    continue

                elif d_instr == 'KEEP' and first:
                    self.get_keeps()
                    continue

                elif d_instr == 'FUNC' and first:
                    self.get_func_def()

                elif d_instr == 'RET' and first:
                    self.get_func_ret()

                else:
                    Info.log(1, f'{self.tk.val} must be at the start of a line.', self.tk)

            # Define replacement
            elif self.tk.tok == 'D_SYMBOL' and self.tk.val == do:
                self.tok_list_out.extend(self.replace_define())
                continue

            # Classic module functions ----------------------------------------
            else:
                ctk = self.clc.pass_1()
                if ctk is None:
                    continue
                elif ctk:
                    self.tk = ctk

            # Create list -----------------------------------------------------
            self.tok_list_out.append(self.tk)

            # EOF -------------------------------------------------------------
            if self.tk.tok == 'EOF':
                break

    # Pass 2 ------------------------------------------------------------------
    def pass_2(self):
        '''Second parser pass, record code flow
        Function calls and labels'''

        Info.log(5, f'Pass 2.')

        self.tok_list_in = self.tok_list_out
        self.reset_pass()

        self.loop_labels = []

        while True:

            self.next_tok()

            # Function calls --------------------------------------------------
            if self.tk.tok == "D_FUNCNM":
                func_calls = self.replace_func_calls()
                self.tok_list_out.extend(func_calls)
                continue

            # Labels ----------------------------------------------------------
            elif self.tk.tok == 'D_SYMBOL':
                if self.last_tok().tok != 'NEWLINE' \
                        and self.peek_ahead(2).val == self.des.d_labdcl:
                    self.get_jump_labels()

                elif self.tk.val == self.des.d_labdop:
                    self.get_label_lines()

                elif self.tk.val == self.des.d_labdcl:
                    self.get_loop_label_return()

            elif self.tk.tok == 'D_INSTRC' and self.tk.uval == 'EXIT':
                self.get_labels_exit()

            # Classic module functions ----------------------------------------
            else:
                ctk = self.clc.pass_2()
                if ctk is None:
                    continue
                elif ctk:
                    self.tk = ctk

            # Create list -----------------------------------------------------
            self.tok_list_out.append(self.tk)

            # EOF -------------------------------------------------------------
            if self.tk.tok == 'EOF':
                break

        # Post pass -----------------------------------------------------------
        if self.loop_labels:
            Info.log(1, f'Loop label not closed from: '
                        f'{self.loop_labels[-1].val}', self.loop_labels[-1])
        if self.in_func:
            Info.log(1, f'Func without ret: {self.in_func.val}', self.in_func)

    # Pass 3 ------------------------------------------------------------------
    def pass_3(self):
        '''Third parser pass, add and remove
        Includes, rem blocks, remove excess newlines, join lines and strings'''

        Info.log(5, f'Pass 3.')

        self.tok_list_in = self.tok_list_out
        self.reset_pass()

        qs = self.des.c_quotes
        nl = self.des.newline_str

        while True:

            self.next_tok()

            # Include ---------------------------------------------------------
            if self.tk.tok == 'D_INSTRC' \
                    and self.tk.uval == 'INCLUDE':
                self.include_file()
                continue

            # Classic module functions ----------------------------------------
            else:
                ctk = self.clc.pass_3()
                if ctk is None:
                    continue
                elif ctk:
                    self.tk = ctk

            # Adjust lines ----------------------------------------------------
            # Rem blocks
            if self.tk.tok == 'C_O_BREM':
                self.next_tok()

                while self.tk.tok != 'C_C_BREM':
                    pos = self.tk.pos.copy(col=len(self.tk.val))
                    self.tok_list_out.extend(self.tok_str(self.des.c_altrem))
                    self.tok_list_out.append(self.tk)
                    self.tok_list_out.extend(self.tok_str(nl, pos=pos))
                    self.next_tok()

                continue

            # Remove excess newlines
            if self.tk.tok == 'NEWLINE':
                self.tk.val = self.des.newline_str
                if self.last_tok().tok == 'NEWLINE':
                    continue

            # Remove excess :
            if self.tk.tok == 'C_INSTSP' \
                    and self.last_tok().tok == 'C_INSTSP':
                continue

            # Remove newline after line separator
            elif self.tk.tok == 'NEWLINE' \
                    and self.last_tok().tok == 'D_INSTSP':
                self.tok_list_out.pop()
                if self.index < self.len - 3:
                    continue

            # Remove newline after instruction separator
            elif self.tk.tok == 'NEWLINE' \
                    and self.last_tok().tok == 'C_INSTSP':
                if self.index < self.len - 3:
                    continue

            # Remove newline before instruction separator
            elif self.tk.tok == 'C_INSTSP' \
                    and self.last_tok().tok == 'NEWLINE' \
                    and self.index > 3:
                self.tok_list_out.pop()

            # Remove newline after label lines
            elif self.tk.tok == 'NEWLINE' \
                    and self.last_tok().tok == 'D_LBLLIN':
                continue

            # Remove newline after function definitions
            elif self.tk.tok == 'NEWLINE' \
                    and self.last_tok().tok == 'D_FUNCDF':
                continue

            # Join adjacent strings
            # Same line
            elif self.tk.tok == 'C_LITQUO' \
                    and self.last_tok().tok == 'C_LITQUO':
                self.tk.val = self.last_tok().val.rstrip(qs) \
                    + self.tk.val.lstrip(qs)
                self.tok_list_out.pop()

            # Previous line
            elif self.tk.tok == 'C_LITQUO' \
                    and (self.last_tok().tok == 'NEWLINE'
                         and self.last_tok(-2).tok == 'C_LITQUO'):
                self.tk.val = \
                    self.last_tok(-2).val.rstrip(qs) + self.tk.val.lstrip(qs)
                self.tok_list_out.pop()
                self.tok_list_out.pop()

            # Create list -----------------------------------------------------
            self.tok_list_out.append(self.tk)

            # EOF -------------------------------------------------------------
            if self.tk.tok == 'EOF':
                break

    # Pass 4 ------------------------------------------------------------------
    def pass_4(self):
        '''Fourth parser pass, apply code flow and line numbers
        Replace labels with lines and apply line numbers and header'''

        Info.log(5, f'Pass 4.')

        self.tok_list_in = self.tok_list_out
        self.reset_pass()

        line_number = self.stg.line_start - self.stg.line_step

        self.line_report = []

        self.label_report = defaultdict(list)
        self.label_lines = {}
        self.label_jumps = []

        llabels_ret = {}
        llabels_exit = []
        label_info = namedtuple('label_info', 'label index line')

        func_defs = {}
        func_call = []
        func_info = namedtuple('func_info', 'func index line')

        # nl = self.des.newline_str

        # apply header
        if self.stg.rem_header:
            self.insert_rem_header(2, 1, self.stg.header1)
            self.insert_rem_header(5, 2, self.stg.header2)

        while True:

            self.next_tok()

            name_w_file = self.tk.val + self.tk.pos.file

            # (Label and functions names added with
            # file name to differentiate from includes)

            # Labels ----------------------------------------------------------
            # Get labels line information
            # Get name and line numbers of line labels
            if self.tk.tok == 'D_LBLLIN':
                self.label_lines[name_w_file] = line_number
                self.label_report[line_number].append(f'<{self.tk.val}')
                continue

            # Get name, index and line numbers of jump labels
            # Including loop labels returns
            elif self.tk.tok == 'D_LBLJMP' or self.tk.tok == 'D_LBLRET':
                self.label_report[line_number].append(f'>{self.tk.val}')

                # Get names and line numbers of loop labels return
                # for using with the exit command
                if self.tk.tok == 'D_LBLRET':
                    llabels_ret[name_w_file] = line_number + self.stg.line_step

                # If special label that points to the same line
                if self.tk.val == self.des.d_labsml:
                    self.tk.val = line_number

                else:
                    self.label_jumps.append(label_info(name_w_file,
                                                       len(self.tok_list_out),
                                                       line_number))

            # Get name, index and line numbers of loop label exit command
            elif self.tk.tok == 'D_LBLEXT':
                self.label_report[line_number].append(f'*{self.tk.val}')
                llabels_exit.append(label_info(name_w_file,
                                               len(self.tok_list_out),
                                               line_number))

            # Functions -------------------------------------------------------
            # Get functions line information
            if self.tk.tok == 'D_FUNCDF':
                func_defs[name_w_file] = line_number
                self.label_report[line_number].append(f'<{self.tk.val}')
                continue

            elif self.tk.tok == 'D_FUNCAL':
                func_call.append(func_info(name_w_file,
                                           len(self.tok_list_out),
                                           line_number))
                self.label_report[line_number].append(f'>{self.tk.val}')

            # Add line number
            elif self.tk.tok == 'NEWLINE' and self.index < self.len - 1:
                self.line_report.append((line_number,
                                         self.tk.pos.lin,
                                         self.tk.pos.text,
                                         self.tk.pos.file))
                line_number += self.stg.line_step
                start_tok = self.peek_ahead()
                line = start_tok.pos.lin

                # Line cannot start with number
                if start_tok.val.isdigit():
                    Info.log(1, f'Line starting with number: {start_tok.val}', tok=start_tok)

                self.tok_list_out.append(self.tk)
                self.tok_list_out.append(Token(tok='C_LINENB',
                                               val=line_number,
                                               pos=self.tk.pos.copy(lin=line,
                                                                    col=0)))
                continue

            # Classic module functions ----------------------------------------
            else:
                ctk = self.clc.pass_4()
                if ctk is None:
                    continue
                elif ctk:
                    self.tk = ctk

            # Create list -----------------------------------------------------
            self.tok_list_out.append(self.tk)

            # EOF -------------------------------------------------------------
            if self.tk.tok == 'EOF':
                break

        # Post pass -----------------------------------------------------------
        # Replace jumps placeholders for line numbers
        for l in self.label_jumps:
            if l.label not in self.label_lines:
                error_tok = self.tok_list_out[l.index]
                Info.log(1, f'Label does not exist: {error_tok.val}', error_tok)
            self.tok_list_out[l.index].val = self.label_lines[l.label]

        # Replace loop labels exit placeholders for line numbers
        for l in llabels_exit:
            if llabels_ret[l.label] > line_number - self.stg.line_step:
                error_tok = self.tok_list_out[l.index]
                Info.log(1, f'Loop exit past end of program.', error_tok)
            self.tok_list_out[l.index].val = llabels_ret[l.label]

        # Replace function calls placeholders for line numbers
        for l in func_call:
            self.tok_list_out[l.index].val = func_defs[l.func]

    # Pass 5 ------------------------------------------------------------------
    def pass_5(self):
        '''Fifth parser pass, classic alterations
        Mostly on the classic module, capitalize'''

        Info.log(5, f'Pass 5.')

        self.tok_list_in = self.tok_list_out
        self.reset_pass()

        while True:

            self.next_tok()

            if False:
                pass

            # Classic module functions ----------------------------------------
            else:
                ctk = self.clc.pass_5()
                if ctk is None:
                    continue
                elif ctk:
                    self.tk = ctk

            # Capitalize
            if self.stg.capitalise_all and isinstance(self.tk.val, str) \
                    and self.tk.tok not in self.des.c_lit_toks:
                self.tk.val = self.tk.uval

            # Create list -----------------------------------------------------
            self.tok_list_out.append(self.tk)

            # EOF -------------------------------------------------------------
            if self.tk.tok == 'EOF':
                break

    # Code generation ---------------------------------------------------------
    def generate(self):
        '''Generate the output code'''

        Info.log(5, f'Generating.')

        self.tok_list_in = self.tok_list_out
        self.reset_pass()

        self.next_tok()

        self.line = []
        self.c_line = ''
        self.c_code = []

        lr = self.des.c_lab_rep_rem
        nn = self.des.newline_str_n

        while True:

            self.next_tok()

            if self.stg.translate:
                for c in str(self.tk.val):
                    if ord(c) > 256:
                        Info.log(1, f'Translate cannot encode '
                                    f'character: {c} ({ord(c)})', self.tk)

            if self.tk.val:
                self.line.append(self.tk)

            # Process and add the line when a newline is reached
            if self.tk.tok == 'NEWLINE':

                line_number = self.line[0].val
                for self.n, self.token in enumerate(self.line):

                    # Classic module functions ----------------------------------------
                    ctk = self.clc.generate()
                    if ctk is None:
                        continue
                    elif ctk:
                        self.tk = ctk

                    # Add spaces before token
                    if self.token.uval in self.des.c_reserved_kw \
                            and self.c_line[-1] != ' ' \
                            and self.line[self.n - 1].val not in self.des.c_symb_comp:
                        self.c_line += self.stg.general_spaces

                    self.c_line += str(self.token.val)

                    # Add spaces after token
                    if self.token.tok != 'NEWLINE' \
                        and self.token.tok == 'C_LINENB' \
                        or (self.token.uval in self.des.c_reserved_kw
                            and self.line[self.n + 1].val not in self.des.c_symb_comp):
                        self.c_line += self.stg.general_spaces

                # Add label report to the end of the line
                if self.stg.label_report:
                    if line_number in self.label_report:
                        labels = ' '.join(self.label_report[line_number])
                        self.c_line = f'{self.c_line.rstrip()}{lr}{labels}'

                # Add a linefeed to the end of the line
                self.c_line = self.c_line.rstrip() + nn

                # Check line size
                line_len = len(self.c_line) - 1
                if line_len > 256:
                    Info.log(1, f'Line too long: {line_len} characters', self.tk)

                # Add line ----------------------------------------------------
                self.c_code.append(self.c_line)

                self.c_line = ''
                self.line = []

            # EOF -------------------------------------------------------------
            if self.tk.tok == 'EOF':
                break

        return self.c_code, self.des.d_declares, self.line_report


def report_output(report_list, header, list_type, file_save, print_report):
    '''Print or save a report list adding the type to the file name
       report_list = The output list
       header = A header to the list
       list_type = The type of the list'''
    report_list = header + report_list
    file_save = f'{os.path.splitext(file_save)[0]}_{list_type}.txt'

    if print_report:
        [print(t.rstrip()) for t in report_list]

    else:
        IO.save_file(None, report_list, file_save, 'UTF-8')
        Info.log(4, f'{file_save} saved.')


# Main class ------------------------------------------------------------------
class Main:
    def __init__(self):
        # settings defined earlier to get the system info and import modules dynamically
        self.stg = stg

        if self.stg.code_is_ascii:
            self.classic()
        else:
            self.dignified()

    # Runs expecting a classic Basic code -------------------------------------
    def classic(self):
        Info.log(3, f'Basic Dignified: {self.stg.system_name}')
        Info.log(3, f'  Processing: {os.path.basename(self.stg.file_load)}')

        # Load classic code -------------------------------------------------
        Info.log(4, f'Loading file: {self.stg.file_load}')
        d_code = IO.load_file(None, self.stg.file_load,
                              self.stg.load_format, self.stg.tab_lenght)

        # Relationship between line numbers to use on the monitoring error report
        self.line_list = {}
        for line in d_code[1:-1]:
            line_number = re.match(r'^\d+', line.text)
            if not line_number:
                err_pos = Position(d_code, lin=line.nmbr, col=-1)
                err_pos.text = line.text
                err_pos.file = os.path.basename(line.file)
                err_tok = Token(pos=err_pos)
                Info.log(1, f'Line not starting with number:', tok=err_tok)

            self.line_list[line_number.group(0)] \
                = (str(line.nmbr), line.text, os.path.basename(line.file))

        self.stg.line_list = self.line_list

        # Run tools -----------------------------------------------------------
        run = Tools.Interface(self.stg)
        run.run()

    # Runs expecting a Dignified Basic code -----------------------------------
    def dignified(self):
        Info.log(3, f'Basic Dignified: {self.stg.system_name}')
        Info.log(3, f'Converting: {os.path.basename(self.stg.file_load)}')

        # Load dignified code -------------------------------------------------
        Info.log(4, f'Loading file: {self.stg.file_load}')
        d_code = IO.load_file(None, self.stg.file_load,
                              self.stg.load_format, self.stg.tab_lenght)

        # Lex it --------------------------------------------------------------
        Info.log(5, 'Lexing.')
        t0 = time.time()

        lex = Lexer(self.stg, d_code)
        lexed = lex.lex()

        tl = time.time() - t0
        Info.log(5, f'{len(lexed)} tokens created in {tl:.4f}s.')

        # Save lexer token list
        if self.stg.lexer_report:
            header = [f'{os.path.split(self.stg.file_load)[1]} lexer output\r',
                      f'{len(lexed)} tokens\r\r']
            report_list = [repr(l) + '\r' for l in lexed]
            report_output(report_list, header, 'lexer',
                          self.stg.file_save, self.stg.print_report)

        # Parse it ------------------------------------------------------------
        Info.log(5, 'Parsing.')
        t0 = time.time()

        include_vars = (lex.des.c_hard_short_vars,
                        lex.des.c_hard_long_vars,
                        lex.des.d_declares)

        par = Parser(self.stg, lexed, lex.des, include_vars)
        parsed, _ = par.par()

        tp = time.time() - t0
        Info.log(5, f'{len(parsed)} tokens created in {tp:.4f}s.')

        # Save parser token list
        if self.stg.parser_report:
            header = [f'{os.path.split(self.stg.file_load)[1]} parser output\r',
                      f'{len(parsed)} tokens\r\r']
            report_list = [repr(l) + '\r' for l in parsed]
            report_output(report_list, header, 'parser',
                          self.stg.file_save, self.stg.print_report)

        # Generate classic code -----------------------------------------------
        Info.log(5, 'Generating Classic code.')
        t0 = time.time()

        c_code, var_r, line_r = par.generate()

        tg = time.time() - t0
        Info.log(5, f'{len(c_code)} lines created in {tg:.4f}s.')
        Info.log(5, f'Total: {tl+tp+tg:.4f}s.')

        # Relationship between line numbers to use on the monitoring error report
        self.line_list = {}
        for line in line_r:
            self.line_list[str(line[0])] \
                = (str(line[1]), line[2], os.path.basename(line[3]))
        self.stg.line_list = self.line_list

        # Save variables report
        if self.stg.var_report:
            report_list = [f'{v[1]}:{v[0].split("@")[0]}\n'
                           for v in sorted(var_r.items(),
                                           key=lambda kv: (kv[1], kv[0]),
                                           reverse=True)]
            header = [f'{len(report_list)} variables assigned\r\r']
            report_output(report_list, header, 'variables',
                          self.stg.file_save, self.stg.print_report)

        # Save lines report
        if self.stg.line_report:
            report_list = []
            for line in line_r:
                line_classic = line[1]
                if line_classic == 0:
                    line_classic = 'Auto generated'
                report_list.append(f'{line[0]} - {line_classic}\n')
            report_list.pop(0)
            header = [f'{len(report_list)} lines generated.\r(Classic - Dignified)\r\r']
            report_output(report_list, header, 'lines',
                          self.stg.file_save, self.stg.print_report)

        # Save classic code ---------------------------------------------------
        Info.log(4, f'Saving file: {self.stg.file_save}')
        IO.save_file(None, c_code, self.stg.file_save)

        # Run tools -----------------------------------------------------------
        run = Tools.Interface(self.stg)
        run.run()


# Main function ---------------------------------------------------------------
def main():
    '''Do the thing'''

    Main()


if __name__ == '__main__':
    main()
