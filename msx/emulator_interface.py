# This module is responsible for opening, sending information and controlling the Emulator

import re
import os.path
import argparse
import subprocess
import configparser
from collections import namedtuple

from support.helper import Infolog

infolog = Infolog()


class Run:
    def __init__(self, e_stg):
        self.e_stg = e_stg

    def run(self):
        self.stg = Settings(self.e_stg)
        self.stg.init()

        if self.stg.run:
            emu = Emulator(self.stg)
            emu.run()


class Expose():
    '''Expose values up the dignified chain'''

    def __init__(self):

        # remTAGs
        # Keep self.remtags as an empty dictionary if no remtag to pass
        remtag = namedtuple('remtag', 'name help metavar')
        self.remtags = {'openMSX': [remtag('EM_RUN', 'Open openMSX and run the code.', 'True or false'),
                                    remtag('EM_SETTING', 'Load openMSX with a setting config.', 'Setting_file'),
                                    remtag('EM_MACHINE', 'Load openMSX with a custom machine.', 'Machine_name'),
                                    remtag('EM_EXTENSION', 'Load openMSX with a custom disk extension.', 'Extension_name:slot'),
                                    remtag('EM_NOTHROTTLE', 'Load openMSX with throttle on or off.', 'True or false'),
                                    remtag('EM_MONITOR', 'Monitor the code execution on openMSX.', 'True or false'),
                                    remtag('EM_VERBOSE', 'Level of information given.', '0-4')]}

        # Command line arguments
        # Keep self.parser even if none argument added
        self.parser = argparse.ArgumentParser(add_help=False)
        arg_group = self.parser.add_argument_group('openMSX')
        arg_group.add_argument('--em_run', help='Open openMSX and run the code.', action='store_true', default=None),
        arg_group.add_argument('--em_setting', help='Load openMSX with a custom setting.', metavar='Setting_file'),
        arg_group.add_argument('--em_machine', help='Load openMSX with a custom machine.', metavar='Machine_name'),
        arg_group.add_argument('--em_extension', help='Load openMSX with a custom disk extension.', metavar='Extension_name:slot'),
        arg_group.add_argument('--em_nothrottle', help='Load openMSX without throttle.', action='store_true', default=None),
        arg_group.add_argument('--em_monitor', help='Monitor the code execution on openMSX.', action='store_true', default=None),
        arg_group.add_argument('--em_verbose', help='Level of information given.', type=int, metavar='0-4')


class Settings:
    def __init__(self, e_stg):
        super(Settings, self).__init__()
        self.e_stg = e_stg

        # Settings
        self.run = False            # Run the code on openMSX
        self.setting = ''            # Emulator settinguration file
        self.machine = ''           # Emulator machine to open, eg: 'Sharp_HB-8000_1.2'
        self.extension = ''         # Emulator extension to open, eg: 'Microsol_Disk:extb'
        self.nothrottle = False     # Run the emulator with throttle enabled
        self.monitor = True         # Monitor the code execution on the emulator
        self.verbose = 3            # Show the emulator output
        self.emulator_path = ''     # Path to the emulator to run the program ('' = local path)

        # Settings from Badig
        self.CURRENT_SYSTEM = self.e_stg.CURRENT_SYSTEM    # Current OS
        self.line_list = self.e_stg.line_list
        self.file_name = os.path.basename(self.e_stg.file_save)
        self.file_path = self.e_stg.file_path
        self.e_args = e_stg.args

        # Constants
        self.INI_FILE = 'emulator_interface.ini'
        self.LOCAL_PATH = os.path.split(os.path.abspath(__file__))[0]
        self.INI_WIN = 'WINDOWS'
        self.INI_LNX = 'LINUX'
        self.INI_MAC = 'DARWIN'

    def str2bol(self, string, same, name):
        '''String to Bool
        string = string to convert to boolean
        same = fallback value if string is empty
        name = name of the object for error reporting'''

        if string.upper() == 'TRUE':
            boolean = True
        elif string.upper() == 'FALSE':
            boolean = False
        elif string == '':
            boolean = same
        else:
            infolog.log(1, f'Remtag must be true or false: {name} = {string}')

        return boolean

    def init(self):
        '''Initialize settings'''

        self.get_ini()

        # Add local path if none is given
        if not os.path.dirname(self.emulator_path):
            self.emulator_path = os.path.join(self.LOCAL_PATH, self.emulator_path)

        # Get passed command line arguments
        self.run = self.run if self.e_args.em_run is None else self.e_args.em_run
        self.setting = self.setting if self.e_args.em_setting is None else self.e_args.em_setting
        self.machine = self.machine if self.e_args.em_machine is None else self.e_args.em_machine
        self.extension = self.extension if self.e_args.em_extension is None else self.e_args.em_extension
        self.nothrottle = self.nothrottle if self.e_args.em_nothrottle is None else self.e_args.em_nothrottle
        self.monitor = self.monitor if self.e_args.em_monitor is None else self.e_args.em_monitor
        self.verbose = self.verbose if self.e_args.em_verbose is None else self.e_args.em_verbose

        # Get passed remtags
        self.run = self.str2bol(self.e_stg.code_remtags.get('EM_RUN', str(self.run)), self.run, 'run')
        self.setting = self.e_stg.code_remtags.get('EM_SETTING', self.setting) or self.setting
        self.machine = self.e_stg.code_remtags.get('EM_MACHINE', self.machine) or self.machine
        self.extension = self.e_stg.code_remtags.get('EM_EXTENSION', self.extension) or self.extension
        self.nothrottle = self.str2bol(self.e_stg.code_remtags.get('EM_NOTHROTTLE', str(self.nothrottle)), self.nothrottle, 'throttle')
        self.monitor = self.str2bol(self.e_stg.code_remtags.get('EM_MONITOR', str(self.monitor)), self.monitor, 'monitor')
        try:
            self.verbose = int(self.e_stg.code_remtags.get('EM_VERBOSE', self.verbose) or self.verbose)
        except ValueError as e:
            infolog.log(1, f'Remtag "em_verbose" must be a number: {e}')

        infolog.level = self.verbose

    def get_ini(self):
        '''Read the .ini file if present using the defaults from the variables'''

        ini_path = os.path.join(self.LOCAL_PATH, self.INI_FILE)
        if os.path.isfile(ini_path):
            ini_section = self.CURRENT_SYSTEM
            config = configparser.ConfigParser()
            config.sections()
            try:
                config.read(ini_path)
                config_sec = config['CONFIGS']
                self.run = config_sec.get('run') or self.run
                self.setting = config_sec.get('setting') or self.setting
                self.machine = config_sec.get('machine') or self.machine
                self.extension = config_sec.get('extension') or self.extension
                self.monitor = config_sec.getboolean('monitor') if config_sec.get('monitor') != '' else self.monitor
                self.nothrottle = config_sec.getboolean('nothrottle') if config_sec.get('nothrottle') != '' else self.nothrottle
                self.verbose = int(config_sec.get('verbose') or self.verbose)
                paths_sec = config[ini_section]
                self.emulator_path = paths_sec.get('emulator_path') or self.emulator_path
            except (ValueError, configparser.NoOptionError) as e:
                infolog.log(1, f'Problem with: {self.INI_FILE}: {str(e)}')


class Emulator:
    def __init__(self, stg):
        self.stg = stg

    def output(self, has_input, step):
        '''Show openMSX output and monitor errors
        removing excess control text if necessary'''

        if self.stg.CURRENT_SYSTEM == self.stg.INI_WIN:
            return

        log_out = self.proc.stdout.readline().rstrip() if has_input else ''
        log_out = log_out.replace('&quot;', '"')
        log_out = log_out.replace('&apos;', "'")

        if '"nok"' in log_out or ' error: ' in log_out:
            log_out = log_out.replace('<reply result="nok">', '')
            self.proc.stdin.write('<command>quit</command>')
            infolog.log(4, step)

            if 'invalid command name "ext' in log_out:
                infolog.log(1, 'Machine probably missing a slot')

            if 'invalid command name "diska' in log_out:
                infolog.log(1, 'Machine probably missing a disk drive')

            infolog.log(1, log_out)

        elif '<log level="warning">' in log_out:
            log_warning = log_out.replace('<log level="warning">', '')
            log_warning = log_warning.replace('</log>', '')
            log_out = log_out.split('<log')[0]
            log_comma = '' if log_out == '' else ': '

            if step + log_comma + log_out != '':
                infolog.log(4, f'{step} {log_comma} {log_out}')

            infolog.log(2, log_warning)
            self.output(True, '')

        else:
            log_out = log_out.replace('<openmsx-output>', '')
            log_out = log_out.replace('</openmsx-output>', '')
            log_out = log_out.replace('<reply result="ok">', '')
            log_out = log_out.replace('</reply>', '')
            log_comma = '' if log_out == '' else ': '

            if step + log_comma + log_out != '':
                infolog.log(4, f'{step} {log_comma} {log_out}')

    def run(self):
        '''Run openMSX with the given arguments'''

        infolog.log(3, 'openMSX')

        call_monitor_tcl = ''
        TCL_SCRIPT = 'openmsx_output.tcl'

        # Check if the emulator exists on the given path
        if self.stg.CURRENT_SYSTEM == self.stg.INI_WIN or self.stg.CURRENT_SYSTEM == self.stg.INI_LNX:
            if not os.path.isfile(self.stg.emulator_path):
                infolog.log(1, f'Emulator not found: {self.stg.emulator_path}')
        elif self.stg.CURRENT_SYSTEM == self.stg.INI_MAC:
            if not os.path.isdir(self.stg.emulator_path):
                infolog.log(1, f'Emulator not found: {self.stg.emulator_path}')

        # Check file names and try to mitigate incompatibilities with MSX disk standards
        crop_export = os.path.splitext(self.stg.file_name)[0][0:8] + os.path.splitext(self.stg.file_name)[1]
        crop_export = crop_export.replace(' ', '_')
        list_dir = os.listdir(self.stg.file_path)
        list_export = [x for x in list_dir if
                       x.lower() != self.stg.file_name.lower()
                       and os.path.splitext(x)[0][0:8].replace(' ', '_').lower()
                       + os.path.splitext(x)[1].replace(' ', '_').lower()
                       == crop_export.lower()]
        if list_export:
            infolog.log(1, f'File name conflict: {list_export[0]} ({crop_export}) = {self.stg.file_name}')

        # Set the emulator execution command based on the machine
        self.stg.file_path = self.stg.file_path.replace(' ', r'\ ')  # Escaping spaces for cmd
        if self.stg.CURRENT_SYSTEM == self.stg.INI_WIN:
            self.stg.file_path = self.stg.file_path.replace('\\', '/')  # cmd apparently needs forward slashes even on Windows
            cmd = [self.stg.emulator_path, '-control', 'stdio']
        elif self.stg.CURRENT_SYSTEM == self.stg.INI_LNX:
            cmd = [self.stg.emulator_path, '-control', 'stdio']
        elif self.stg.CURRENT_SYSTEM == self.stg.INI_MAC:
            cmd = [os.path.join(self.stg.emulator_path, 'contents', 'macos', 'openmsx'), '-control', 'stdio']

        infolog.log(3, f'Opening: {self.stg.file_name}')

        # Set the machine to load
        using_setting = 'default settings'
        if self.stg.setting != '':
            using_setting = self.stg.setting
            self.stg.setting = ['-setting', self.stg.setting]
            cmd.extend(self.stg.setting)
        infolog.log(4, f'Using: {using_setting}')

        # Set the machine to load
        using_machine = 'default machine'
        if self.stg.machine != '':
            using_machine = self.stg.machine
            self.stg.machine = ['-machine', self.stg.machine]
            cmd.extend(self.stg.machine)
            infolog.log(4, f'As: {using_machine}')

        # Set the extension and slot to load
        extension = 'no extension'
        if self.stg.extension != '':
            disk_ext_slot = 'ext'
            disk_ext = self.stg.extension.split(':')
            self.stg.extension = disk_ext[0].strip()
            if len(disk_ext) > 1:
                if re.match(r'ext[a-z]?$', disk_ext[1].lower().strip()):
                    disk_ext_slot = disk_ext[1].lower().strip()
                else:
                    infolog.log(2, f'Slot name must be "ext[a-z]": {disk_ext_slot}\n  * Extension inserted in the first available slot.')
            cmd.extend([f'-{disk_ext_slot}', self.stg.extension])
            extension = f'{self.stg.extension} extension at {disk_ext_slot}'
            infolog.log(4, f'With: {extension}')

        if self.stg.nothrottle:
            infolog.log(4, f'Throttle disabled')

        # Set the TCL monitoring script
        if self.stg.monitor:
            TCL_path = os.path.split(os.path.abspath(__file__))[0]
            if os.path.isfile(os.path.join(TCL_path, TCL_SCRIPT)):
                call_monitor_tcl = ['-script', os.path.join(TCL_path, TCL_SCRIPT)]
            else:
                infolog.log(2, f'{TCL_SCRIPT} script not found (monitoring_disabled)')
                self.stg.monitor = False
            cmd.extend(call_monitor_tcl)

        # Set the folder to insert as a drive
        cmd.extend(['-diska', self.stg.file_path])

        # Run the emulator
        self.proc = subprocess.Popen(cmd, bufsize=1,
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT,
                                     encoding='utf-8',
                                     cwd=os.path.dirname(self.stg.emulator_path),
                                     close_fds=True)

        endline = '\r\n'
        newline = '\\r'

        # Send commands and get replies
        self.output(True, f'')  # needed to synchronize responses from the emulator

        self.proc.stdin.write(f'<command>set renderer SDL</command>{endline}')
        self.output(True, 'Showing screen')

        self.proc.stdin.write('<command>set throttle off</command>' + endline)
        self.output(True, 'Turning throttle off')

        self.proc.stdin.write('<command>debug set_watchpoint write_mem 0xfffe {[debug read "memory" 0xfffe] == 1} {set throttle on}</command>' + endline)
        self.output(True, 'Setting throttle on watch point')

        self.proc.stdin.write(f'<command>set power on</command>{endline}')
        self.output(True, 'Powering on')

        self.proc.stdin.write(f'<command>type_via_keybuf {newline}{newline}</command>{endline}')  # Disk ROM ask for date, two enter to skip
        self.output(True, 'Pressing return twice')

        self.proc.stdin.write(f'<command>type_via_keybuf load"{crop_export}{newline}</command>{endline}')
        self.output(True, f'Typing load"{crop_export}')

        # Throttle will turn on too soon if using the throttle on command
        if not self.stg.nothrottle:
            self.proc.stdin.write(f'<command>type_via_keybuf poke-2,1{newline}</command>{endline}')
            self.output(True, 'Typing poke to turn throttle on')

        self.proc.stdin.write(f'<command>type_via_keybuf cls:run{newline}</command>{endline}')
        self.output(True, 'Typing cls and run')

        if self.stg.monitor and self.stg.CURRENT_SYSTEM == self.stg.INI_WIN:
            infolog.log(2, 'Execution monitoring not yet supported on Windows')

        # Start the monitoring routine
        elif self.stg.monitor:
            infolog.log(4, 'Monitoring execution')
            for line in iter(self.proc.stdout.readline, b''):
                poll = self.proc.poll()
                if poll is not None:
                    raise SystemExit(0)
                if '\x07' in line and '\x0c' not in line:
                    line_out = line.replace('\x1b', '').replace('Y$ ', '').replace('\x07', '').rstrip()
                    current_line = line_out.split(' ')[len(line_out.split(' ')) - 1].rstrip()
                    if line_out[:5] == 'Parei' or line_out[:5] == 'Break':
                        infolog.log(2, line_out, bullet='  - ')
                    elif current_line in self.stg.line_list:
                        line_exec = (f'{self.stg.line_list[current_line][2]}: ({self.stg.line_list[current_line][0]},0): {line_out}'
                                     f'\n    {self.stg.line_list[current_line][1].strip()}'
                                     f'\n    ^')
                        infolog.log(1, line_exec, bullet='*** ')
                    else:
                        infolog.log(1, line_out, bullet='  * ')
