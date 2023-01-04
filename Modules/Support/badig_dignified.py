# Description class -----------------------------------------------------------
class Description:
    '''A description of the Dignified basic'''

    def __init__(self):
        super(Description, self).__init__()

        # Dignified commands
        d_instrc = ['DEFINE', 'DECLARE', 'INCLUDE',
                    'KEEP', 'ENDIF', 'FUNC', 'RET',
                    'EXIT']

        # Dignified operators
        d_operat = ['TRUE', 'FALSE']

        # Dignified symbols
        d_symbol = [r'\[', r'\]', '{', '}', '@', '~']

        # General identifiers description for inclusion with caps
        d_idcaps = r'[a-zA-Z][a-zA-Z_0-9]*'
        # General identifiers description for inclusion without caps
        d_idnocaps = r'[a-z][a-z_0-9]*'
        # General identifiers legal names standalone
        self.d_identf = r'^[a-zA-Z][a-zA-Z_0-9]*$'

        # Identifier with type and groups for match
        self.d_idnttp_grp = r'^([a-zA-Z][a-zA-Z_0-9]*)([%!#$]?)$'

        # Defines dictionary
        self.d_defines = {}
        # Defines delimiter open
        self.d_defdop = '['
        # Defines delimiter close
        self.d_defdcl = ']'
        # Defines separator
        self.d_defsep = ','
        # Defines variable delimiter open
        self.d_defvop = '('
        # Defines variable delimiter close
        self.d_defvcl = ')'

        # Declares dictionary
        self.d_declares = {}
        # Declares assign
        self.d_decass = ':'
        # Declares separator
        self.d_decsep = ','
        # Keep long name vars as is
        self.d_keepid = '~'

        # Labels delimiter open
        self.d_labdop = '{'
        # Labels delimiter close
        self.d_labdcl = '}'
        # Labels same line
        self.d_labsml = '@'

        # Functions dictionary
        self.d_functions = {}
        # Functions delimiter open
        self.d_funcop = '('
        # Functions delimiter close
        self.d_funccl = ')'
        # Functions separator
        self.d_funcsep = ','
        # Functions equal
        self.d_funcequal = '='
        # Function names
        d_funcnm = fr'^\.{d_idnocaps}$'

        # Toggle rems list
        self.d_keeps = []
        # Toggle rem keep all
        self.d_keep_all = '#ALL'
        # Toggle rem keep none
        self.d_keep_none = '#NONE'
        # Toggle rem character
        self.d_togremchar = '#'
        # Toggle rem compiler
        d_togrem = fr'^#{d_idnocaps}$'
        # Toggle rem checker
        self.d_togremchk = fr'^(#)({d_idcaps})$'

        # Remtags dictionary
        self.d_remtags = {}
        # Remtag equal
        self.d_remtequal = '='
        # Remtag arg indicator
        self.d_remtindic = '-'
        # Remtags match regex
        self.d_match_remtags = r'^\s*##BB:([a-zA-Z_0-9]+)=(.*)$'
        # Remtags commands
        self.d_remtcm = ['EXPORT_FILE', 'OVERRIDE_MACHINE', 'OVERRIDE_EXTENSION',
                         'MONITOR_EXEC', 'THROTTLE', 'CONVERT_ONLY', 'ARGUMENTS']

        # block rems (open)
        d_o_rems = r'^###$'

        # Line rem
        d_linrem = r'^##$'

        # Command separator (shared with classic call instruction)
        # Decide in parser based on position relative to end of line
        d_instsp = r'^_$'
        self.d_instsp_str = '_'

        # Hack so the regex match partially until it get to the correct match
        d_partls = [r'\.']

        # Additional tokens
        # (These tokens are not used for match, they are entered directly on the code
        # and are here only for reference)
        # Label line position placeholder
        r'(?P<d_lbllin>)'
        # Label jump position placeholder token
        r'(?P<d_lbljmp>)'
        # Function definition position placeholder
        r'(?P<d_funcdf>)'
        # Function call position placeholder
        r'(?P<d_funcal>)'

        # Identifier with type and named group for compile
        self.d_idnttp = r'^(?P<d_idnttp>[a-z][a-z_0-9]*[%!#$]?$)'

        # Regex groups
        dig_inst = fr"(?P<d_instrc>{self.join_commands(d_instrc)})"
        dig_oper = fr"(?P<d_operat>{self.join_commands(d_operat)})"
        dig_symb = fr"(?P<d_symbol>{self.join_commands(d_symbol)})"
        dig_part = fr"(?P<d_partls>{self.join_commands(d_partls)})"
        dig_trem = fr'(?P<d_tglrem>{d_togrem})'
        dig_lems = fr"(?P<d_linrem>{d_linrem})"
        dig_brem = fr"(?P<d_o_erem>{d_o_rems})"
        dig_insp = fr'(?P<d_instsp>{d_instsp})'
        dig_func = fr'(?P<d_funcnm>{d_funcnm})'

        # Groups assembled for compiling (Order is important)
        self.dignified_groups = (''
                                 fr'{dig_inst}|'
                                 fr'{dig_func}|'
                                 fr'{dig_oper}|'
                                 fr'{dig_symb}|'
                                 fr'{dig_lems}|'
                                 rf'{dig_insp}|'
                                 fr'{dig_trem}|'
                                 fr'{dig_brem}|'
                                 fr'{dig_part}')

    def join_commands(self, *args):
        '''Join list items with individual regex terminators'''
        l = []
        [l.extend(a) for a in args]
        l = r'$|^'.join(l)
        return fr'(^{l}$)'
