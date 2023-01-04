import os.path
import platform
import argparse
import configparser

# Custom modules
from Modules.Support import infolog
from Modules.Support import getsystem


# Settings class --------------------------------------------------------------
class SettingsBuild:

    def __init__(self):
        super(SettingsBuild, self).__init__()
        '''Initialize variables, .ini, arguments and process the user input information'''

        # Files
        self.SUBLIMEBUILD_INI = 'sublimebuild.ini'
        self.SYSTEMS_JSON = 'systems.json'
        self.LOCAL_PATH = os.path.split(os.path.abspath(__file__))[0]

        # Configs
        self.INI_MAIN = 'CONFIGS'
        self.INI_WIN = 'WINPATHS'
        self.INI_MAC = 'MACPATHS'

        # System
        self.system_id = 'msx'
        self.system_name = 'MSX'
        self.dignified_ext = '.dmx'
        self.ascii_ext = '.amx'
        self.binary_ext = '.bmx'
        self.list_ext = '.lmx'

        # User variables
        self.source_file = ''
        self.machine_name = ''          # Emulator machine to open, eg: 'Philips_NMS_8250' 'Sharp_HB-8000_1.2' 'Sharp_HB-8000_1.2_Disk'
        self.disk_ext_name = ''         # Emulator extension to open, eg: 'Microsol_Disk:SlotB'
        self.throttle = False           # Run the emulator with throttle enabled
        self.monitor_exec = True        # Monitor the code execution on the emulator
        self.tokenize = False           # Tokenize the ASCII code
        self.show_output = True         # Show the emulator stderr output
        self.verbose_level = 3          # Show processing status: 0-silent 1-+errors 2-+warnings 3-+steps 4-+details
        self.emulator_filepath = ''     # Path to the emulator to run the program ('' = local path)

        self.is_windows = platform.system() == "Windows"  # Get the operating system

    def init(self):
        '''Initialize the settings module'''

        self.get_ini()

        parser = self.get_arguments()
        args = parser.parse_args()

        self.properties(args)

    def get_arguments(self):
        '''Get the command line arguments using the defaults from the variables and the .ini'''

        parser = argparse.ArgumentParser(description='Convert Basic Dignified source and run on emulator',
                                         epilog='Fred Rique (farique) (c) 2018 - '
                                                'github.com/farique/basic-dignified\n')

        parser.add_argument('source_file',
                            nargs='?', default=self.source_file,
                            help='File to build')

        parser.add_argument('-id',
                            nargs='?', default=self.system_id,
                            help='Basic system to use (def %(default)s)')

        parser.add_argument('-classic',
                            action='store_true',
                            help='The flavor of Basic to process (def %(default)s)')

        parser.add_argument('-convert',
                            action='store_true',
                            help='Do not run the code after conversion (def %(default)s)')

        parser.add_argument('-monitor',
                            default=self.monitor_exec, action='store_true',
                            help='Monitor the execution on the emulator (def %(default)s)')

        parser.add_argument('-tokenize',
                            default=self.tokenize, action='store_true',
                            help='Tokenize the ASCII code (def %(default)s)')

        parser.add_argument('-list',
                            action='store_true',
                            help='Save a .mlt list file (def %(default)s)')

        return parser

    # def str_bool(self, string):
    #     boolean = True if string == 'True' else False
    #     return boolean

    def get_ini(self):
        '''Read the .ini file if present using the defaults from the variables'''

        ini_path = os.path.join(self.LOCAL_PATH, self.SUBLIMEBUILD_INI)
        if os.path.isfile(ini_path):
            ini_section = self.INI_WIN if self.is_windows else self.INI_MAC
            config = configparser.ConfigParser()
            config.sections()
            try:
                config.read(ini_path)
                config_sec = config[self.INI_MAIN]
                paths_sec = config[ini_section]
                self.system_id = config_sec.get('system_id') or self.system_id
                self.machine_name = config_sec.get('machine_name') or self.machine_name
                self.disk_ext_name = config_sec.get('disk_ext_name') or self.disk_ext_name
                self.throttle = config_sec.get('throttle') or self.throttle
                self.monitor_exec = config_sec.get('monitor_exec') or self.monitor_exec
                self.tokenize = config_sec.get('tokenize') or self.tokenize
                self.verbose_level = int(config_sec.get('verbose_level') or self.verbose_level)
                self.emulator_filepath = paths_sec.get('emulator_filepath') or self.emulator_filepath
            except (ValueError, configparser.NoOptionError) as e:
                infolog.log(1, f'Problem with:{self.SUBLIMEBUILD_INI}:' + str(e))

        # Check if emulator_filepath is only the name of the emulator
        # If so make the path local + emulator name
        if self.emulator_filepath == '':
            self.emulator_filepath = self.LOCAL_PATH

        return config

    def properties(self, args):

        self.system_id = args.id
        self.SYSTEMS_JSON = os.path.join(self.LOCAL_PATH, self.SYSTEMS_JSON)
        system = getsystem.read_system(self.SYSTEMS_JSON, self.system_id)

        self.system_name = system.name
        self.dignified_ext = system.dig_ext
        self.ascii_ext = system.asc_ext
        self.binary_ext = system.bin_ext
        self.list_ext = system.lst_ext

        self.classic_basic = args.classic
        self.convert_only = args.convert
        self.monitor_exec = args.monitor
        self.tokenize = args.tokenize
        self.save_list = args.list
        self.source_file = args.source_file
        self.file_path = os.path.dirname(args.source_file)
        self.file_name = os.path.basename(args.source_file)
