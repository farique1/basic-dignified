import os.path
import subprocess

from Modules.Support import infolog

TOK_EXISTS = True
try:
    from Modules.msx import msxbatoken as Tokenizer
except (ImportError, ModuleNotFoundError):
    TOK_EXISTS = False


class Build:
    def __init__(self, stg):
        self.stg = stg

    def build(self):
        if TOK_EXISTS:
            tok = Tokenizer.Main()
            args = [self.stg.source_file]
            if self.stg.save_list:
                args.append('-el')
            tok.stg.init(external=args)
            tok.execute()
        else:
            infolog.log(2, 'Tokenizer not found.')


class Run:
    def __init__(self, stg):
        self.stg = stg

    def output(self, has_input, step):
        if not self.stg.show_output:
            return

        log_out = self.proc.stdout.readline().rstrip() if has_input else ''
        log_out = log_out.replace('&quot;', '"')
        log_out = log_out.replace('&apos;', "'")

        if '"nok"' in log_out or ' error: ' in log_out:
            log_out = log_out.replace('<reply result="nok">', '')
            self.proc.stdin.write('<command>quit</command>')
            infolog.log(4, step)

            if 'invalid command name "ext' in log_out:
                infolog.log(2, 'Machine probably missing a slot')

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

    def run(self, line_list):
        disk_ext_slot = 'ext'
        using_machine = 'default machine'

        call_monitor_tcl = ''
        TCL_SCRIPT = 'openMSXoutput.tcl'

        if self.stg.is_windows:
            if not os.path.isfile(self.stg.emulator_filepath) \
                    and (not self.stg.convert_only or self.stg.monitor_exec):
                infolog.log(1, f'Emulator not found: {self.stg.emulator_filepath}')
        else:
            if not os.path.isdir(self.stg.emulator_filepath) \
                    and (not self.stg.convert_only or self.stg.monitor_exec):
                infolog.log(1, f'Emulator not found: {self.stg.emulator_filepath}')

        if self.stg.machine_name != '':
            using_machine = self.stg.machine_name
            self.stg.machine_name = ['-machine', self.stg.machine_name]

        disk_ext = self.stg.disk_ext_name.split(':')
        self.stg.disk_ext_name = disk_ext[0].strip()
        if len(disk_ext) > 1:
            disk_ext_slot = 'extb' if disk_ext[1].lower().strip() == 'slotb' else disk_ext_slot

        extension = f'{self.stg.disk_ext_name} extension at {disk_ext_slot}'
        infolog.log(3, 'openMSX', bullet='')
        infolog.log(3, f'Opening: {self.stg.file_name}', bullet='')
        infolog.log(3, f'As a {using_machine} with {extension if self.stg.disk_ext_name != "" else "no extension"}')
        infolog.log(3, f'Throttle {"enabled" if self.stg.throttle else "disabled"}')

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

        self.stg.file_path = self.stg.file_path.replace(' ', r'\ ')

        if self.stg.is_windows:
            self.stg.file_path = self.stg.file_path.replace('\\', '/')  # cmd apparently needs forward slashes even on Windows
            cmd = [self.stg.emulator_filepath, '-control', 'stdio']
        else:
            cmd = [os.path.join(self.stg.emulator_filepath, 'contents', 'macos', 'openmsx'), '-control', 'stdio']

        if self.stg.machine_name != '':
            cmd.extend(self.stg.machine_name)

        if self.stg.monitor_exec:
            TCL_path = os.path.split(os.path.abspath(__file__))[0]
            if os.path.isfile(os.path.join(TCL_path, TCL_SCRIPT)):
                call_monitor_tcl = ['-script', os.path.join(TCL_path, TCL_SCRIPT)]
            else:
                infolog.log(2, 'openMSXoutput.tcl script not found (monitoring_disabled)')
                self.stg.monitor_exec = False

        if self.stg.monitor_exec:
            cmd.extend(call_monitor_tcl)

        self.proc = subprocess.Popen(cmd, bufsize=1, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8', close_fds=True)

        endline = '\r\n'
        nl = '\\r'

        self.output(True, f'')  # needed to synchronize responses from the emulator

        self.proc.stdin.write(f'<command>set renderer SDL</command>{endline}')
        self.output(True, 'Showing screen')

        self.proc.stdin.write('<command>set throttle off</command>' + endline)
        self.output(True, 'Turning throttle off')

        # self.proc.stdin.write('<command>debug set_watchpoint write_mem 0xfffe {[debug read "memory" 0xfffe] == 0} {set renderer SDL}</command>' + endline)
        # self.output(True, 'Setting render SDL watch point')

        self.proc.stdin.write('<command>debug set_watchpoint write_mem 0xfffe {[debug read "memory" 0xfffe] == 1} {set throttle on}</command>' + endline)
        self.output(True, 'Setting throttle on watch point')

        if self.stg.disk_ext_name != '':
            self.proc.stdin.write(f'<command>{disk_ext_slot} {self.stg.disk_ext_name}</command>{endline}')
            self.output(True, f'Inserting disk drive extension: {self.stg.disk_ext_name} at {disk_ext_slot}')

        self.proc.stdin.write(f'<command>diska insert {self.stg.file_path}</command>{endline}')
        self.output(True, f'Inserting folder as disk: {self.stg.file_path}')

        self.proc.stdin.write(f'<command>set power on</command>{endline}')
        self.output(True, 'Powering on')

        self.proc.stdin.write(f'<command>type_via_keybuf {nl}{nl}</command>{endline}')  # Disk ROM ask for date, two enter to skip
        self.output(True, 'Pressing return twice')

        self.proc.stdin.write(f'<command>type_via_keybuf load"{crop_export}{nl}</command>{endline}')
        self.output(True, f'Typing load"{crop_export}')

        # self.proc.stdin.write(f'<command>type_via_keybuf poke-2,0{nl}</command>{endline}')
        # self.output(True, 'Typing poke to render SLD')

        if not self.stg.throttle:
            self.proc.stdin.write(f'<command>type_via_keybuf poke-2,1{nl}</command>{endline}')
            self.output(True, 'Typing poke to turn throttle on')

        self.proc.stdin.write(f'<command>type_via_keybuf cls:run{nl}</command>{endline}')
        self.output(True, 'Typing cls and run')

        if self.stg.monitor_exec and self.stg.is_windows:
            infolog.log(2, 'Execution monitoring not yet supported on Windows')

        elif self.stg.monitor_exec:
            infolog.log(1, 'Monitoring execution', bullet='--- ')
            for line in iter(self.proc.stdout.readline, b''):
                poll = self.proc.poll()
                if poll is not None:
                    raise SystemExit(0)
                if '\x07' in line and '\x0c' not in line:
                    line_out = line.replace('\x1b', '').replace('Y$ ', '').replace('\x07', '').rstrip()
                    current_line = line_out.split(' ')[len(line_out.split(' ')) - 1].rstrip()
                    if line_out[:5] == 'Parei' or line_out[:5] == 'Break':
                        infolog.log(1, line_out, bullet='  - ')
                    elif current_line in line_list:
                        line_exec = (f'{line_list[current_line][2]}: ({line_list[current_line][0]},0): {line_out}'
                                     f'\n    {line_list[current_line][1].strip()}'
                                     f'\n    ^')
                        infolog.log(1, line_exec, bullet='*** ')
                    else:
                        infolog.log(1, line_out, bullet='  * ')

            # proc.wait()
