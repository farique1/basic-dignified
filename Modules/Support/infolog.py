import os.path

# Logger module ---------------------------------------------------------------
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

level = 5
position = '({lin},{col}): '
message = '{bullet}{file}{pos}{desc}'
bullets = ['',      # 0 none
           '*** ',  # 1 error
           '  * ',  # 2 warning
           '--- ',  # 3 main
           '  - ',  # 4 sub
           '    ']  # 5 item


def log(lvl, desc, data=None, bullet=None, show_file=False):

    error = False
    if lvl == 1 and not bullet:
        error = True
        if data:
            col = data.col - data.offset - 1
            desc += f'\n    {data.text.strip()}'
            desc += '\n    ' + '-' * col + '^'
        desc += '\n    Conversion stopped.'

    if error and level == 0:
        raise SystemExit(0)

    if level < lvl:
        return

    if bullet is None:
        bullet = bullets[lvl]

    pos = ''
    file = ''
    if data:
        pos = position.format(lin=data.lin, col=data.col)
        if error or show_file:
            file = f'{os.path.basename(data.file)}: '

    print(message.format(bullet=bullet, file=file, pos=pos, desc=desc))

    if error:
        raise SystemExit(0)
