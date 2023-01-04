import os.path
import argparse
import configparser

# Wether part of Badig or standalone
try:
    from Modules.Support import infolog
except (ImportError, ModuleNotFoundError):
    import infolog


# Settings class --------------------------------------------------------------
class Settings:

    def __init__(self):
        super(Settings, self).__init__()
        '''Initialize variables, .ini, arguments and process the user input information'''

        # Files
        self.BATOKEN_INI = 'msxbatoken.ini'

        # System
        self.binary_ext = '.bmx'
        self.list_ext = '.lmx'

        # Variables
        self.file_load = ''
        self.file_load = ''              # Source file
        self.file_save = ''              # Destination file
        self.export_list = 0             # Save a .mlt list file detailing the tokenization: [#] number of bytes per line (def 16) (max 32) (0 no)
        self.delete_original = False     # Delete the original ASCII file
        self.verbose_level = 3           # Verbosity level: 0 silent, 1 errors, 2 +warnings, 3 +steps(def), 4 +details, 5 +conversion dump
        # self.is_from_build = False       # Tell if it is being called from a build system (show file name on error messages and other stuff)

    def init(self, external=None):
        '''Initialize the settings module
           external = 'None' will retain the original command line arguments.
                      However if this program is running as a module, the original
                      arguments of the program calling the module will be passed,
                      so 'external' should contain the file to be called. This will
                      reset the arguments and also pass the file to be converted'''

        self.get_ini()

        parser = self.get_arguments()
        args = parser.parse_args(external)

        self.properties(args)

    # def str_bool(self, string):
    #     boolean = True if string == 'True' else False
    #     return boolean

    def get_ini(self):
        '''Read the .ini file if present using the defaults from the variables'''

        local_path = os.path.split(os.path.abspath(__file__))[0]
        ini_path = os.path.join(local_path, self.BATOKEN_INI)
        if os.path.isfile(ini_path):
            config = configparser.ConfigParser()
            config.sections()
            try:
                config.read(ini_path)
                configs_sec = config['CONFIGS']
                self.file_load = configs_sec.get('file_load') or self.file_load
                self.file_save = configs_sec.get('file_save') or self.file_save
                self.export_list = int(configs_sec.get('export_list') or self.export_list)
                self.delete_original = configs_sec.get('delete_original') or self.delete_original
                self.verbose_level = int(configs_sec.get('verbose_level') or self.verbose_level)
            except (ValueError, configparser.NoOptionError) as e:
                # pass
                infolog.log(1, f'Problem with:{self.BATOKEN_INI}:{str(e)}')

        return config

    def get_arguments(self):
        '''Get the command line arguments using the defaults from the variables and the .ini'''

        parser = argparse.ArgumentParser(description='MSX Basic Tokenizer: Tokenize MSX Basic (rly!).',
                                         epilog='Fred Rique (farique) (c) 2018 - '
                                                'github.com/farique/basic-dignified\n')

        parser.add_argument('input',
                            nargs='?', default=self.file_load,
                            help='Source file (preferable .asc)')

        parser.add_argument('output',
                            nargs='?', default=self.file_save,
                            help='Destination file ([source].bas) if missing')

        parser.add_argument('-el',
                            default=self.export_list, const=16, type=int, nargs='?',
                            help='Save a .mlt list file detailing the tokenization: '
                            '[#] number of bytes per line (def 16) (max 32)')

        parser.add_argument('-do',
                            default=self.delete_original, action='store_true',
                            help='Delete original file after conversion')

        parser.add_argument('-vb',
                            default=self.verbose_level, type=int,
                            help='Verbosity level: 0 silent, 1 errors, 2 +warnings, '
                            '3 +steps, 4 +details, 5 +conversion dump (def %(default)s)')

        return parser

    def properties(self, args):
        '''Apply the initialization information'''

        self.file_load = args.input
        self.file_save = args.output
        base_file = os.path.basename(self.file_load)
        save_path = os.path.dirname(self.file_load)
        if args.output == '':
            save_file = os.path.splitext(base_file)[0] + self.binary_ext
            self.file_save = os.path.join(save_path, save_file)
        list_file = os.path.splitext(base_file)[0] + self.list_ext
        self.file_list = os.path.join(save_path, list_file)
        self.export_list = True if args.el > 0 else False
        bytes_width = min(abs(args.el), 32)
        self.width_byte = bytes_width * 2
        self.width_line = bytes_width * 3 + 7
        self.delete_original = args.do
        self.verbose_level = args.vb
