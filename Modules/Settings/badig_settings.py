import re
import sys
import os.path
import argparse
import configparser

# Custom modules
from Modules.Support import io
from Modules.Support import infolog
from Modules.Support import getsystem
from Modules.Support import badig_dignified as Dignified


# Initialization --------------------------------------------------------------
class Initialize:
    '''Initialize user variables and get values from
    the .ini file or command line arguments if available.'''

    def __init__(self):
        super(Initialize, self).__init__()
        '''Initialize variables, .ini, arguments and process the user input information'''

        # Files
        self.SYSTEMS_JSON = 'systems.json'
        self.BADIG_INI = 'badig.ini'
        self.LOCAL_PATH = os.path.split(os.path.abspath(__file__))[0]

        # Configs
        self.INI_MAIN = 'CONFIGS'

        # System
        self.system_id = 'msx'
        self.system_name = 'MSX'
        self.dignified_ext = '.dmx'
        self.ascii_ext = '.amx'
        self.binary_ext = '.bmx'
        self.list_ext = '.lmx'

        # User variables
        self.file_load = ''              # Source file
        self.file_save = ''              # Destination file

        self.line_start = 10             # Start line number
        self.line_step = 10              # Line step amount
        self.rem_header = True           # Add product line
        self.strip_spaces = False        # Strip all spaces
        self.capitalise_all = False      # Capitalize all instructions
        self.translate = False           # Translate Unicode characters to native similar

        self.convert_print = ''          # Convert ? to PRINT or vice-versa: ?=? p=PRINT
        self.strip_then_goto = ''        # Strip adjacent THEN/ELSE or GOTO: t=THEN/ELSE g=GOTO

        self.print_report = False        # Print the reports instead of saving
        self.label_report = False        # Show label names as rem on the converted code
        self.line_report = False         # Save or display a line correspondence report
        self.var_report = False          # Save a variable substitution report
        self.lexer_report = False        # Save or display the lexer output tokens
        self.parser_report = False       # Save or display the parser output tokens

        self.tab_lenght = 4              # The amount of spaces in each TAB, used to report columns.
        self.verbose_level = 3           # Level of information: 0=silent 1+=erros 2+=warnings 3+=headers 4+=subheaders 5+=itens
        self.output_format = 'a'         # Tokenized or ASCII output: t=tokenized a=ASCII
        self.export_list = 0             # Save a .mlt list file detailing the tokenization: [#] number of bytes per line (def 16) (max 32) (0 no)

        self.monitor_exec = False        # Monitor the execution on the emulator and catch errors (only works with From Build)

        # Arguments who take variables to check before applying remtags
        self.args_with_vars = ['-id', '-tl', '-ls', '-lp', '-cp', '-tg', '-vb', '-of', '-el']
        self.remtags = {}

    def init(self, external=None):
        '''Initialize the settings module
           external = 'None' will retain the original command line arguments.
                      However if Badig is running as a module, the original
                      arguments of the program calling the module will be passed,
                      so 'external' should contain the file to be called. This will
                      reset the arguments and also pass the file to be converted'''

        # Load the .ini file
        ini_response = self.get_ini()

        # Process arguments including getting the filename to get the remtags
        parser = self.get_arguments()
        args1 = parser.parse_args(external)

        # Apply settings
        self.properties(args1)

        # Process remtags from Dignified file
        remtags = self.process_remtags(args1.input)

        # If remtags has arguments, run properties() again with them + the original ones
        if remtags.get('ARGUMENTS'):
            arg_remtags = remtags['ARGUMENTS']
            # If coming from the build, pass the file name + remtag args
            # else pass the command line arguments + remtag args
            if external:
                arguments = external
            else:
                arguments = sys.argv[1:]
            arguments.extend(arg_remtags)

            # Process the arguments again including the remtags
            args2 = parser.parse_args(arguments)

            # Apply settings again
            self.properties(args2)

        # If remtags has export file, process it
        if remtags.get('EXPORT_FILE'):
            save_file = remtags.get('EXPORT_FILE')

            if os.path.dirname(save_file):
                self.file_save = save_file
            else:
                self.file_path = os.path.dirname(self.file_load)
                self.file_save = os.path.join(self.file_path, save_file)

            if not os.path.splitext(self.file_save)[1]:
                self.file_save += self.ascii_ext

        # Write an .ini file if asked
        if self.write_ini_file:
            self.write_ini(ini_response)
            return

    def process_remtags(self, file_load):
        '''Process the remtags from the Dignified file
        - file_load = the file to get the remtags from'''

        d_code = io.load_file(None, file_load)

        desc = Dignified.Description()

        for line in d_code:
            if m := re.match(desc.d_match_remtags, line.text, re.I):
                rt_name = m.group(1).upper()
                rt_args = m.group(2)
                if rt_name not in desc.d_remtcm:
                    infolog.log(1, f'Invalid remtag: {m.group(1)}')
                self.remtags[rt_name] = rt_args

                if rt_name == 'ARGUMENTS' and rt_args != '':
                    rtargs = rt_args.split()
                    for n, a in enumerate(rtargs):
                        if a[0] != '-' and rtargs[n - 1] not in self.args_with_vars:
                            infolog.log(1, f'Invalid remtag argument: {a}')
                    self.remtags[rt_name] = rtargs
        return self.remtags

    # def str_bool(self, string):
    #     boolean = True if string == 'True' else False
    #     return boolean

    def get_ini(self):
        '''Read the .ini file if present using the defaults from the variables'''

        ini_path = os.path.join(self.LOCAL_PATH, self.BADIG_INI)
        config = configparser.ConfigParser()
        config.sections()
        if os.path.isfile(ini_path):
            try:
                config.read(ini_path)
                configs_sec = config[self.INI_MAIN]
                use_ini_file = bool(configs_sec.get('use_ini_file')) or False
                if use_ini_file:
                    self.file_load = configs_sec.get('source_file') or self.file_load
                    self.file_save = configs_sec.get('destin_file') or self.file_save

                    self.system_id = configs_sec.get('system_id') or self.system_id

                    self.tab_lenght = int(configs_sec.get('tab_lenght') or self.tab_lenght)
                    self.line_start = int(configs_sec.get('line_start') or self.line_start)
                    self.line_step = int(configs_sec.get('line_step') or self.line_step)
                    self.rem_header = configs_sec.get('rem_header') or self.rem_header
                    self.strip_spaces = configs_sec.get('strip_spaces') or self.strip_spaces
                    self.capitalise_all = configs_sec.get('capitalize_all') or self.capitalise_all
                    self.convert_print = configs_sec.get('convert_print') or self.convert_print
                    self.strip_then_goto = configs_sec.get('strip_then_goto') or self.strip_then_goto
                    self.translate = configs_sec.get('translate') or self.translate
                    self.verbose_level = int(configs_sec.get('verbose_level') or self.verbose_level)

                    self.print_report = configs_sec.get('print_report') or self.print_report
                    self.label_report = configs_sec.get('label_report') or self.label_report
                    self.line_report = configs_sec.get('line_report') or self.line_report
                    self.var_report = configs_sec.get('var_report') or self.var_report
                    self.lexer_report = configs_sec.get('lexer_report') or self.lexer_report
                    self.parser_report = configs_sec.get('parser_report') or self.parser_report

                    self.output_format = configs_sec.get('output_format') or self.output_format
                    self.export_list = int(configs_sec.get('export_list') or self.export_list)
            except (ValueError, configparser.NoOptionError) as e:
                infolog.log(1, f'Problem with: {self.BADIG_INI}:{str(e)}')
        else:
            infolog.log(2, f'.ini not found: {ini_path}\n'
                           '    A new one will be created with the current settings.')
            self.write_ini(config)

        return config

    def write_ini(self, config):
        '''Write an new .ini file with the user variables values'''
        config[self.INI_MAIN] = {'use_ini_file': 'True',
                                 'source_file': '',
                                 'destin_file': '',
                                 'system_id': str(self.system_id),
                                 'tab_lenght': str(self.tab_lenght),
                                 'line_start': str(self.line_start),
                                 'line_step': str(self.line_step),
                                 'rem_header': str(self.rem_header),
                                 'strip_spaces': str(self.strip_spaces),
                                 'capitalize_all': str(self.capitalise_all),
                                 'convert_print': str(self.convert_print),
                                 'strip_then_goto': str(self.strip_then_goto),
                                 'translate': str(self.translate),
                                 'print_report': str(self.print_report),
                                 'label_report': str(self.label_report),
                                 'var_report': str(self.var_report),
                                 'line_report': str(self.line_report),
                                 'lexer_report': str(self.lexer_report),
                                 'parser_report': str(self.parser_report),
                                 'verbose_level': str(self.verbose_level),
                                 'output_format': str(self.output_format),
                                 'export_list': str(self.export_list)}

        with open(os.path.join(self.LOCAL_PATH, self.BADIG_INI), 'w') as configfile:
            config.write(configfile)
            infolog.log(1, f'.ini file written with current settings: {self.BADIG_INI}', '', '--- ')

    def get_arguments(self):
        '''Get the command line arguments using the defaults from the variables and the .ini'''

        parser = argparse.ArgumentParser(description='Basic Dignified Suite: Write classic 8 bit Basic the modern way.',
                                         epilog='Fred Rique (farique) (c) 2018 - '
                                                'github.com/farique/basic-dignified\n')

        parser.add_argument('input',
                            nargs='?', default=self.file_load,
                            help='Source file (.bad or system specific extension)')

        parser.add_argument('output',
                            nargs='?', default=self.file_save,
                            help=f'Destination file (<SOURCE>{self.ascii_ext}) if missing')

        parser.add_argument('-id',
                            nargs='?', default=self.system_id,
                            help='Basic system to use (def %(default)s)')

        parser.add_argument('-tl', metavar='#',
                            default=self.tab_lenght, type=int,
                            help='Amount of spaces per TAB (def %(default)s)')

        parser.add_argument('-ls', metavar='#',
                            default=self.line_start, type=int,
                            help='Starting line (def %(default)s)')

        parser.add_argument('-lp', metavar='#',
                            default=self.line_step, type=int,
                            help='Line steps (def %(default)s)')

        parser.add_argument('-rh',
                            default=self.rem_header, action='store_false',
                            help='Show the info REM header (def %(default)s)')

        parser.add_argument('-ss',
                            default=self.strip_spaces, action='store_true',
                            help='Strip all spaces: (def %(default)s)')

        parser.add_argument('-ca',
                            default=self.capitalise_all, action='store_true',
                            help='Capitalize (def %(default)s)')

        parser.add_argument('-cp',
                            default=self.convert_print, choices=['?', 'p', 'P'],
                            help='Convert ? to PRINT or vice-versa (def %(default)s)')

        parser.add_argument('-tg', metavar='t|g',
                            default=self.strip_then_goto, choices=['t', 'T', 'g', 'G'],
                            help='Remove adjacent THEN/ELSE or GOTO: '
                                 't=THEN/ELSE, g=GOTO (def %(default)s)')  # REMOVED KEEP ALL (IS REALLY NEEDED?)

        parser.add_argument('-tr',
                            default=self.translate, action='store_true',
                            help='Translate Unicode characters to native similar (def %(default)s)')

        parser.add_argument('-vb', metavar='#',
                            default=self.verbose_level, type=int,
                            help='Verbosity level: 0=silent, 1=errors, 2=1+warnings, '
                                 '3=2+steps, 4=3+details (def %(default)s)')

        parser.add_argument('-of', metavar='ta',
                            default=self.output_format, choices=['ta', 'TA', 'tA', 'Ta', 't', 'T', 'a', 'A'],
                            help='Tokenized or ASCII output: t=tokenized, a=ASCII (def %(default)s)')  # REMOVED BOTH. CHANGE CODE ACCORDINLGY

        parser.add_argument('-el', metavar='#',
                            default=self.export_list, const=16, type=int, nargs='?',
                            help='Save a .mlt list file detailing the tokenization: '
                                 '[#]=number of bytes per line (max 32) (def %(default)s)')  # REMOVE 0, LOOK CODE

        parser.add_argument('-prr',
                            default=self.print_report, action='store_true',
                            help='Print the reports instead of saving (def %(default)s)')

        parser.add_argument('-lbr',
                            default=self.label_report, action='store_true',
                            help='Show label names as rem on the converted code (def %(default)s)')

        parser.add_argument('-lnr',
                            default=self.line_report, action='store_true',
                            help='Save or display a line correspondence report (def %(default)s)')

        parser.add_argument('-var',
                            default=self.var_report, action='store_true',
                            help='Save or display a variable substitution report (def %(default)s)')

        parser.add_argument('-lex',
                            default=self.lexer_report, action='store_true',
                            help='Save or display the lexer output tokens (def %(default)s)')

        parser.add_argument('-par',
                            default=self.parser_report, action='store_true',
                            help='Save or display the parser output tokens (def %(default)s)')

        parser.add_argument('-exe',
                            default=self.monitor_exec, action='store_true',
                            help='Send line numbers to build system to catch errors during execution '
                                 '(only works with From Build) (def %(default)s)')

        parser.add_argument('-ini',
                            action='store_true',
                            help='Create msxbadig.ini (def %(default)s)')
        return parser


# Settings --------------------------------------------------------------------
class Settings(Initialize):
    '''Apply the initialization information'''

    def properties(self, args):
        '''Prepare and expand the settings information'''

        self.system_id = args.id
        self.SYSTEMS_JSON = os.path.join(self.LOCAL_PATH, self.SYSTEMS_JSON)
        system = getsystem.read_system(self.SYSTEMS_JSON, self.system_id)

        self.system_name = system.name
        self.dignified_ext = system.dig_ext
        self.ascii_ext = system.asc_ext
        self.binary_ext = system.bin_ext
        self.list_ext = system.lst_ext

        # Process properties
        self.file_load = args.input
        self.file_save = args.output
        self.file_path = os.path.dirname(self.file_load)
        if self.file_save == '':
            save_file = os.path.basename(self.file_load)
            save_file = os.path.splitext(save_file)[0] + self.ascii_ext
            self.file_save = os.path.join(self.file_path, save_file)
        else:
            if not os.path.dirname(self.file_save):
                self.file_save = os.path.join(self.file_path, self.file_save)
            if not os.path.splitext(self.file_save)[1]:
                self.file_save += self.ascii_ext

        self.tab_lenght = abs(args.tl)
        self.line_start = abs(args.ls)
        self.line_step = abs(args.lp)
        self.rem_header = args.rh
        self.general_spaces = '' if args.ss else ' '
        self.capitalise_all = args.ca
        self.convert_print = args.cp.upper() if args.cp else None
        self.strip_then_goto = args.tg.upper()
        self.translate = args.tr
        self.verbose_level = args.vb
        self.output_format = args.of.upper()
        self.export_list = min(abs(args.el), 32)
        self.monitor_exec = args.exe
        self.write_ini_file = args.ini

        self.print_report = args.prr
        self.label_report = args.lbr
        self.line_report = args.lnr
        self.var_report = args.var
        self.lexer_report = args.lex
        self.parser_report = args.par

        self.header1 = 'Converted with Basic Dignified'
        self.header2 = 'https://github.com/farique1/basic-dignified'

        self.load_format = 'utf-8' if self.translate else 'latin1'
        self.load_path = os.path.dirname(self.file_load)

        return
