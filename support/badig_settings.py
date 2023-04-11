import re
import sys
import os.path
import platform
import argparse
import importlib
import configparser
from collections import namedtuple

# Custom modules
from .helper import IO
from .helper import Infolog
from . import badig_dignified as Dignified

# Classic modules imported in Settings.init()

# Initlalize Infolog
infolog = Infolog()


# Initialization --------------------------------------------------------------
class Settings:
    '''Initialize user variables and get values from
    the .ini file or command line arguments if available.'''

    def __init__(self):
        '''Initialize variables, .ini, arguments and process the user input information'''

        # Files
        self.BADIG_INI = 'badig.ini'
        self.LOCAL_PATH = os.path.split(os.path.abspath(__file__))[0]

        # Configs
        self.INI_MAIN = 'CONFIGS'
        self.CURRENT_SYSTEM = platform.system().upper()  # Get the operating system

        # System
        self.system_id = 'msx'

        # User variables
        self.file_load = ''              # Source file
        self.file_save = ''              # Destination file

        self.line_start = 10             # Start line number
        self.line_step = 10              # Line step amount
        self.rem_header = True           # Add product line
        self.strip_spaces = False        # Strip all spaces
        self.capitalise_all = False      # Capitalize all instructions
        self.translate = False           # Translate Unicode characters to native similar

        self.print_report = False        # Print the reports instead of saving
        self.label_report = False        # Show label names as rem on the converted code
        self.line_report = False         # Save or display a line correspondence report
        self.var_report = False          # Save a variable substitution report
        self.lexer_report = False        # Save or display the lexer output tokens
        self.parser_report = False       # Save or display the parser output tokens

        self.tab_lenght = 4              # The amount of spaces in each TAB, used to report columns.
        self.verbose_level = 3           # Level of information: 0=silent 1+=erros 2+=warnings 3+=headers 4+=subheaders 5+=itens

        # Arguments who take variables to check before applying remtags
        remtag = namedtuple('remtag', 'name help metavar')
        self.remtags = {'Badig': [remtag('EXPORT_FILE', 'Custom name to save the file', 'File_name'),
                                  remtag('ARGUMENTS', 'Pass command line arguments inside the code', 'arguments'),
                                  remtag('HELP', 'Show all available remtags', 'True or false')]}

        # Other
        self.header1 = 'Converted with Basic Dignified'
        self.header2 = 'https://github.com/farique1/basic-dignified'

    def init(self, external=None):
        '''Initialize the settings module
           external: 'None' will retain the original command line arguments.
                      However if Badig is running as a module, the original
                      arguments of the program calling the module will be passed,
                      so 'external' should contain the file to be called. This will
                      reset the arguments and also pass the file to be converted'''

        # Load the .ini file
        ini_response = self.get_ini()

        # Hackish way to load correct modules before properly processing the arguments
        if '-id' in sys.argv:
            self.system_id = sys.argv[sys.argv.index('-id') + 1]

        system_language_module = f'{self.system_id}.badig_{self.system_id}'
        system_tools_module = f'{self.system_id}.tools_{self.system_id}'
        system_package = f'{self.system_id}'

        # Import classic modules
        try:
            self.Classic = importlib.import_module(system_language_module, system_package)
            self.Tools = importlib.import_module(system_tools_module, system_package)
        except ModuleNotFoundError as e:
            infolog.log(1, f'Classic module not found: {e}')

        # Expose Dignified module
        self.Dignified = Dignified

        # Get exposed information from modules
        clc_exposed = self.Classic.Expose()
        tls_exposed = self.Tools.Expose()

        # Get remtags from the tools
        remtags_desc, remtags_list, max_remtag_len = self.get_exposed_remtags(tls_exposed, clc_exposed)

        # Get information about the system
        self.Classic.Description.sysinfo(self)

        # Process arguments including getting the filename to get the remtags
        parser = self.get_arguments(tls_exposed, clc_exposed)
        self.args = parser.parse_args(external)

        # Show remtag help by command line
        if self.args.rtg:
            self.show_remtag_help(remtags_desc, max_remtag_len)

        # Apply settings
        self.properties(self.args)

        # Write an .ini file if asked
        if self.write_ini_file:
            self.write_ini(ini_response)

        # Get remtags from the code, show help from remtag and get arguments
        code_remtags = self.read_remtags_from_code(self.args.input, remtags_list)
        rt_help = code_remtags.get('HELP')
        rt_help = self.str2bol(rt_help, False, 'Remtag help')
        if rt_help:
            self.show_remtag_help(remtags_desc, max_remtag_len)
        arguments = self.get_remtag_arguments(external, code_remtags)

        if arguments:
            # Process the arguments again including the remtags and apply
            self.args = parser.parse_args(arguments)
            self.properties(self.args)

        # Apply remtag save name and unify verbose
        self.process_other_remtags(code_remtags)

        # Expose remtag lists and dicts by adding them to self
        self.code_remtags = code_remtags
        self.remtags_desc = remtags_desc
        self.remtags_list = remtags_list

        # Process arguments on the classic module and apply them to c_stg
        c_stg = self.Classic.Settings()
        self.c_stg = c_stg.properties(self)

    def new_save_file(self, old_save_file):
        '''Build a save file path and name based on the contents os the output file
        old_save_file: output file path to process'''
        load_file = os.path.basename(self.file_load)
        load_file = os.path.splitext(load_file)[0]

        load_path = os.path.dirname(self.file_load)

        save_file = os.path.basename(old_save_file)
        save_path = os.path.dirname(old_save_file)
        save_path = save_path.lstrip('\\').lstrip('/')

        if not os.path.isabs(save_path):
            save_path = os.path.abspath(os.path.join(load_path, save_path))

        if old_save_file == '':
            save_filepathext = os.path.join(load_path, load_file)
        else:
            if save_path and save_file:
                save_filepathext = os.path.join(save_path, save_file)
            elif save_file:
                save_filepathext = os.path.join(load_path, save_file)
            elif save_path:
                save_filepathext = os.path.join(save_path, load_file)

        if not os.path.splitext(save_filepathext)[1]:
            save_filepathext += self.ascii_ext

        return save_filepathext

    def show_remtag_help(self, remtags_desc, max_remtag_len):
        '''Show a help message with all exposed remtags and its functions'''
        infolog.log(1, 'Available remtags.', bullet='-')
        infolog.log(1, 'Format for copying to the code:\n', bullet='--')
        for program in remtags_desc:
            for remtag in remtags_desc[program]:
                infolog.log(1, f'{remtag.name.lower()}=', bullet='##BB:')
            infolog.log(1, '', bullet='   ')

        infolog.log(1, 'By program:', bullet='--')
        for program in remtags_desc:
            infolog.log(1, program, bullet=' ')
            for remtag in remtags_desc[program]:
                spaces = ' ' * (max_remtag_len - len(remtag.name))
                infolog.log(1, f'{remtag.name} {spaces} {remtag.help} ({remtag.metavar}).', bullet='  - ')
            infolog.log(1, '', bullet='   ')
        raise SystemExit(0)

    def get_remtag_arguments(self, external, code_remtags):
        '''Get the ARGUMENTS remtag arguments from the code,
        make them into a list and add them to other arguments to be passed again
        - external = the variable to add to argparser (see init())'''
        arguments = False
        # If remtags has arguments, run properties() again with them + the original ones
        if arg_remtags := code_remtags.get('ARGUMENTS'):

            # Convert ARGUMENTS remtag argument in list
            if arg_remtags != '':
                split_args = arg_remtags.split()
                code_remtags['ARGUMENTS'] = split_args

            # If coming from the build (external = not None)
            # pass the file name + remtag args
            # else pass the command line arguments + remtag args
            if external:
                arguments = external
            else:
                arguments = sys.argv[1:]
            arguments.extend(split_args)

        return arguments

    def process_other_remtags(self, code_remtags):
        '''Apply functions of miscellaneous remtags'''

        # If remtags has export file, process it
        if save_file := code_remtags.get('EXPORT_FILE'):
            if save_file != '':
                self.file_save = self.new_save_file(save_file)

        # Unify verbose if value < 0
        if self.verbose_level < 0:
            self.verbose_level = abs(self.verbose_level)
            for arg in vars(self.args):
                if 'VERBOSE' in arg.upper():
                    setattr(self.args, arg, abs(self.verbose_level))

    def get_exposed_remtags(self, tls_exposed, clc_exposed):
        '''Get the remtags exposed by the tool interfaces
        - tls_exposed = The tls_exposed elements from the tools'''
        remtags_desc = self.remtags

        # Add remtags from classic module
        remtags_desc.update(clc_exposed.remtags)

        # Add remtags from program interfaces
        for exp in tls_exposed.exposed:
            if exp.remtags is not None:
                remtags_desc.update(exp.remtags)

        # Make the remtags list
        max_remtag_len = 0
        remtags_list = {}
        for program in remtags_desc:
            for item in remtags_desc[program]:
                if item.name in remtags_list:
                    raise AttributeError(f'Remtag duplicated: {item.name} in {program}')
                remtags_list[item.name] = ''
                if len(item.name) > max_remtag_len:
                    max_remtag_len = len(item.name)

        return remtags_desc, remtags_list, max_remtag_len

    def read_remtags_from_code(self, file_load, remtags_list):
        '''Get the remtags and their arguments from the Dignified file
        - file_load = the file to get the remtags from'''

        d_code = IO.load_file(None, file_load)

        desc = Dignified.Description()

        code_remtags = {}
        for line in d_code:
            if m := re.match(desc.d_match_remtags, line.text, re.I):
                rt_name = m.group(1).upper()
                rt_args = m.group(2).strip()
                if rt_name not in remtags_list:
                    infolog.log(2, f'Remtag not available: {rt_name}')
                code_remtags[rt_name] = rt_args

        return code_remtags

    def str2bol(self, string, same, name):
        '''String to Bool
        string = string to convert to boolean
        same = fallback value if string is empty
        name = name of the object for error reporting'''
        if string is None:
            string = False
            return

        if string.upper() == 'TRUE':
            boolean = True
        elif string.upper() == 'FALSE':
            boolean = False
        elif string == '':
            boolean = same
        else:
            infolog.log(1, f'Remtag must be true or false: {name} = {string}')

        return boolean

    def get_ini(self):
        '''Read the .ini file if present using the defaults from the variables'''

        ini_path = os.path.join(self.LOCAL_PATH, self.BADIG_INI)
        config = configparser.ConfigParser()
        config.sections()
        if os.path.isfile(ini_path):
            try:
                config.read(ini_path)
                configs_sec = config[self.INI_MAIN]
                use_ini_file = configs_sec.getboolean('use_ini_file') if configs_sec.get('use_ini_file') != '' else False
                if use_ini_file:
                    self.system_id = configs_sec.get('system_id') or self.system_id

                    self.file_load = configs_sec.get('source_file') or self.file_load
                    self.file_save = configs_sec.get('destin_file') or self.file_save

                    self.line_start = int(configs_sec.get('line_start') or self.line_start)
                    self.line_step = int(configs_sec.get('line_step') or self.line_step)
                    self.rem_header = configs_sec.getboolean('rem_header') if configs_sec.get('rem_header') != '' else self.rem_header
                    self.strip_spaces = configs_sec.getboolean('strip_spaces') if configs_sec.get('strip_spaces') != '' else self.strip_spaces
                    self.capitalise_all = configs_sec.getboolean('capitalize_all') if configs_sec.get('capitalize_all') != '' else self.capitalise_all
                    self.translate = configs_sec.getboolean('translate') if configs_sec.get('translate') != '' else self.translate

                    self.print_report = configs_sec.getboolean('print_report') if configs_sec.get('print_report') != '' else self.print_report
                    self.label_report = configs_sec.getboolean('label_report') if configs_sec.get('label_report') != '' else self.label_report
                    self.line_report = configs_sec.getboolean('line_report') if configs_sec.get('line_report') != '' else self.line_report
                    self.var_report = configs_sec.getboolean('var_report') if configs_sec.get('var_report') != '' else self.var_report
                    self.lexer_report = configs_sec.getboolean('lexer_report') if configs_sec.get('lexer_report') != '' else self.lexer_report
                    self.parser_report = configs_sec.getboolean('parser_report') if configs_sec.get('parser_report') != '' else self.parser_report

                    self.tab_lenght = int(configs_sec.get('tab_lenght') or self.tab_lenght)
                    self.verbose_level = int(configs_sec.get('verbose_level') or self.verbose_level)

            except (ValueError, configparser.NoOptionError) as e:
                infolog.log(1, f'Problem with: {self.BADIG_INI}: {str(e)}')
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
                                 'translate': str(self.translate),
                                 'print_report': str(self.print_report),
                                 'label_report': str(self.label_report),
                                 'var_report': str(self.var_report),
                                 'line_report': str(self.line_report),
                                 'lexer_report': str(self.lexer_report),
                                 'parser_report': str(self.parser_report),
                                 'verbose_level': str(self.verbose_level)}

        with open(os.path.join(self.LOCAL_PATH, self.BADIG_INI), 'w') as configfile:
            config.write(configfile)
            infolog.log(1, f'.ini file written with current settings: {self.BADIG_INI}', '', '--- ')
            raise SystemExit(0)

    def get_arguments(self, tls_exposed, clc_exposed):
        '''Get the command line arguments using the defaults from the variables and the .ini'''

        # Check for arguments on the program interfaces and add them
        parent_parsers = []
        parent_parsers.append(clc_exposed.parser)
        for exp in tls_exposed.exposed:
            parent_parsers.append(exp.parser)

        parser = argparse.ArgumentParser(description='Basic Dignified Suite: Write classic 8 bit Basic the modern way.',
                                         epilog='Fred Rique (farique) (c) 2018 - '
                                                'github.com/farique/basic-dignified\n',
                                         parents=parent_parsers)

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

        parser.add_argument('-tr',
                            default=self.translate, action='store_true',
                            help='Translate Unicode characters to native similar (def %(default)s)')

        parser.add_argument('-vb', metavar='#',
                            default=self.verbose_level, type=int,
                            help='Verbosity level: 0=silent, 1=errors, 2=1+warnings, '
                                 '3=2+steps, 4=3+details (def %(default)s)')

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

        parser.add_argument('-asc',
                            action='store_true',
                            help='Tells Badig the file is classic ASCII Basic (def %(default)s)')

        parser.add_argument('-ini',
                            action='store_true',
                            help='Create msxbadig.ini (def %(default)s)')

        parser.add_argument('-rtg',
                            action='store_true',
                            help='Show all available remtags (def %(default)s)')

        return parser

    def properties(self, args):
        '''Prepare and expand the settings information'''

        # System information
        self.system_id = args.id

        # Type of code
        self.code_is_ascii = args.asc

        # Process properties
        # Files
        self.file_load = args.input
        self.file_save = args.output
        self.file_path = os.path.dirname(self.file_load)
        if self.code_is_ascii:
            self.file_save = self.file_load
        else:
            self.file_save = self.new_save_file(self.file_save)

        self.load_path = os.path.dirname(self.file_load)

        # Dignified
        self.tab_lenght = abs(args.tl)
        self.line_start = abs(args.ls)
        self.line_step = abs(args.lp)
        self.rem_header = args.rh
        self.general_spaces = '' if args.ss else ' '
        self.capitalise_all = args.ca
        self.translate = args.tr
        self.load_format = 'utf-8' if self.translate else 'latin1'
        self.verbose_level = args.vb
        self.write_ini_file = args.ini

        # Reports
        self.print_report = args.prr
        self.label_report = args.lbr
        self.line_report = args.lnr
        self.var_report = args.var
        self.lexer_report = args.lex
        self.parser_report = args.par
