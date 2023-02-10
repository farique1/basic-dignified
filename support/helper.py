import os.path
from collections import namedtuple


# Logger class ---------------------------------------------------------------
class Infolog:
    '''Format and display the log activity.
   lvl = The message importance level
   desc = Main message
   data = Detailed data: line = line number
                         column = column number
                         offset = column offset for pointer
                         line text = the current line text
                         filename = the current filename
   bullet = Message leading marker
   show_file = Show the file name'''

    def __init__(self):
        super(Infolog, self).__init__()
        self.level = 5
        self.position = '({lin},{col}): '
        self.message = '{bullet}{file}{pos}{desc}'
        self.bullets = ['',      # 0 none
                        '*** ',  # 1 error
                        '  * ',  # 2 warning
                        '--- ',  # 3 main
                        '  - ',  # 4 sub
                        '    ',  # 5 item
                        '    ',  # more item
                        '    ',  # more item
                        '    ']  # more item

    def log(self, lvl, desc, data=None, bullet=None, show_file=False):

        error = False
        if lvl == 1 and not bullet:
            error = True
            if data:
                col = data.col - data.offset - 1
                desc += f'\n    {data.text.strip()}'
                desc += '\n    ' + '-' * col + '^'
            desc += '\n    Conversion stopped.'

        if error and self.level == 0:
            raise SystemExit(0)

        if self.level < lvl:
            return

        if bullet is None:
            bullet = self.bullets[lvl]

        pos = ''
        file = ''
        if data:
            pos = self.position.format(lin=data.lin, col=data.col)
            if error or show_file:
                file = f'{os.path.basename(data.file)}: '

        print(self.message.format(bullet=bullet, file=file, pos=pos, desc=desc))

        if error:
            raise SystemExit(0)


infolog = Infolog()


class IO:
    '''Load the Dignified and save the classic code'''

    def load_file(tk, file_load, encoding='latin1', tab_lenght=4):
        '''Load the source code and the includes.
           tk = Token for error reporting on include
           file_load = Name of the file
           encoding = File encoding format
           tab_lenght = Spaces in each TAB'''

        Line = namedtuple('Line', 'nmbr text file')
        listing = [Line(0, 'PROGRAM', file_load)]

        if file_load:
            try:
                with open(file_load, 'r', encoding=encoding) as f:
                    for i, line in enumerate(f, 1):
                        line_prep = line.expandtabs(tab_lenght)
                        listing.append(Line(i, line_prep, file_load))
            except IOError:
                infolog.log(1, f'File not found: {file_load}', tk)
        else:
            infolog.log(1, 'File name not given.', tk)

        listing.append(Line(i + 1, 'EOF', ''))

        return listing

    # Save file -------------------------------------------------------------------
    def save_file(tk, code, file_save, encoding='latin1'):
        '''Save the converted code and auxiliary files
           tk = Token for error reporting
           code = Code to be saved
           file_save = File name
           encoding = Saving encoding'''

        try:
            with open(file_save, 'w', encoding=encoding) as f:
                for line in code:
                    try:
                        f.write(line)
                    except UnicodeEncodeError as e:
                        infolog.log(1, f'Saving encode error: {str(e)}\n'
                                    f'    {file_save}', tk)
        except IOError:
            infolog.log(1, f'Save folder not found: {file_save}', tk)
