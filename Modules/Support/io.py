from collections import namedtuple

from Modules.Support import infolog


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
