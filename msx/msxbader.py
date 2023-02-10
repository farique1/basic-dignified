#!/usr/bin/env python3
'''
MSX Basic DignifiER
v1.3
Convert traditional MSX Basic to modern MSX Basic Dignified format.

Copyright (C) 2020- Fred Rique (farique)
Part of the Basic Dignified Suite
https://github.com/farique1/basic-dignified

New: 1.3v 09/12/2021
    WINDOWS COMPATIBILITY YEY!
        os.path() operations to improve compatibility across systems

TODO (and ideas):
    Make an .ini file
    Force together character pairs without capturing a group
    Unravel only FORs (with indentation option)
    Indentation option for IFs
    Option to remove colons when unraveling
    Remove option to keep original spacing
    Centralize all unravel/indent options on a single variable:
        ie. 'adidfdtbec' a=all f=for i=if n=bef_then t=aft_then b=bef_else e=aft_else
                        d=indentation, modify the item before, id=indent_if
                        c=colon below, put the : on the line below
'''

import re
import os.path
import argparse

# Keyword lists
instr = ['AND', 'BASE', 'BEEP', 'BLOAD', 'BSAVE', 'CALL', 'CIRCLE', 'CLEAR',
         'CLOAD', 'CLOSE', 'CLS', 'CMD', 'COLOR', 'CONT', 'COPY', 'CSAVE',
         'CSRLIN', 'DATA', 'DEF', 'DEFDBL', 'DEFINT', 'DEFSNG', 'DEFSTR', 'DIM',
         'DRAW', 'DSKI', 'END', 'EQV', 'ERASE', 'ERR', 'ERROR', 'FIELD', 'FILES',
         'FN', 'FOR', 'GET', 'IF', 'INPUT', 'INTERVAL', 'IMP', 'IPL', 'KILL',
         'LET', 'LFILES', 'LINE', 'LOAD', 'LOCATE', 'LPRINT', 'LSET', 'MAX',
         'MERGE', 'MOD', 'MOTOR', 'NAME', 'NEW', 'NEXT', 'NOT', 'OFF', 'ON',
         'OPEN', 'OR', 'OUT', 'OUTPUT', 'PAINT', 'POINT', 'POKE', 'PRESET',
         'PRINT', 'PSET', 'PUT', 'READ', 'REM', 'RSET', 'SAVE', 'SCREEN', 'SET',
         'SOUND', 'STEP', 'STOP', 'SWAP', 'TIME', 'TO', 'TROFF', 'TRON', 'USING',
         'VPOKE', 'WAIT', 'WIDTH', 'XOR', r'\?', "'"]  # 'AS',

funct = ['ABS', 'ASC', 'ATN', r'ATTR\$', r'BIN\$', 'CDBL', r'CHR\$', 'CINT',
         'COS', 'CSNG', 'CVD', 'CVI', 'CVS', 'DSKF', r'DSKO\$', 'EOF', 'EXP',
         'FIX', 'FPOS', 'FRE', r'HEX\$', r'INKEY\$', 'INP', r'INPUT\$', 'INSTR',
         'INT', 'KEY', r'LEFT\$', 'LEN', 'LOC', 'LOF', 'LOG', 'LPOS', r'MID\$',
         r'MKD\$', r'MKI\$', r'MKS\$', r'OCT\$', 'PAD', 'PDL', 'PEEK', 'PLAY',
         'POS', r'RIGHT\$', 'RND', 'SGN', 'SIN', r'SPACE\$', 'SPC', r'SPRITE\$',
         'SPRITE', 'SQR', 'STICK', r'STR\$', 'STRIG', r'STRING\$', 'TAB',
         'TAN', 'USR', 'VAL', 'VARPTR', 'VDP', 'VPEEK']

branc = ['AUTO', 'DELETE', 'ELSE', 'ERL', 'GOSUB', 'GOTO', 'LIST', 'LLIST',
         'RENUM', 'RESTORE', 'RESUME', 'RETURN', 'RUN', 'THEN']

# User variables
file_load = ''         # Source file
file_save = ''         # Destination file
conv_lower = True      # Convert non literals to lowercase
keep_spcs = False      # Keep original spacing
conv_locprt = True     # Convert locate:print to [?]
format_label = 'is'    # Format labels: i=indent lines, s=blank line before
format_rems = ''       # Process REMs. l=line, i=inline, b=keep blank, m=move before k=keep label
unravel_if = ''        # Break IF/THEN/ELSE lines: f=colons, t=bef THEN, n=aft THEN, e=bef ELSE, s=aft ELSE
unravel_for = 'f'
unravel_colons = 'c'  # Break lines at ':': i=with indent, w=without indent, c=colon on line below
verbose_level = 3      # Show processing status: 0-silent 1-+errors 2-+warnings 3-+steps 4-+details
# Put a space before and/or after a keyword if preceded/followed by this matches
repelcbef = r'[a-z0-9{}")$]'
repelcaft = r'[a-z0-9{}"(]'
# Force the removal of spaces before and/or after these matches
stripsbef = r'^(,|:)$'
stripsaft = r'^(,|:)$'
# Force a space before and/or after these matches
spacesbef = r'^(#|\+|-|\*|/|\^|\\)$'
spacesaft = r'^(\+|-|\*|/|\^|\\)$'
# Force this matches to be together
forcetogt = r'(<=|>=|=<|=>|\)-\()'

# Command line arguments
parser = argparse.ArgumentParser(description='Convert traditional MSX Basic to '
                                             'modern MSX Basic Dignified format.')

parser.add_argument('input', nargs='?', default=file_load,
                    help='Source file (.asc)')

parser.add_argument('output', nargs='?', default=file_save,
                    help='Destination file ([source].bad) if missing')

parser.add_argument('-tl', default=conv_lower, action='store_false',
                    help='Make lower case all non literal text. '
                    f'def: {conv_lower}')

parser.add_argument('-ks', default=keep_spcs, action='store_true',
                    help='Keep original spacing if greater than 1. '
                    f'def: {keep_spcs}')

parser.add_argument('-cp', default=conv_locprt, action='store_true',
                    help='Convert locatex,y:print to [?]x,y. '
                    f'def: {conv_locprt}')

parser.add_argument("-fl", default=format_label, choices=['i', 's'],
                    type=str.lower, help='Format labels: i=indent non label '
                    'lines, s=blank line before label. '
                    '(Can mix letters together) '
                    f'def: {format_label}')

parser.add_argument("-fr", default=format_rems, choices=['l', 'i', 'b', 'm', 'k'],
                    type=str.lower, help='Format REMs: l=remove line, i=remove '
                    'inline, b=keep blank as blank lines, m=move inline to line '
                    'before, k=add labels to removed REMs. '
                    '(Can mix letters together) '
                    f'def: {format_rems}')

parser.add_argument("-ut", default=unravel_if, choices=['t', 'n', 'e', 'b'],
                    type=str.lower, help='Break after THEN/ELSE: t=after THEN, '
                    'n=before THEN, t=after THEN, b=before ELSE, e=after ELSE. '
                    '(Can mix letters together) '
                    f'def: {unravel_if}')

parser.add_argument("-uc", default=unravel_colons, choices=['i', 'w', 'c'],
                    type=str.lower, help='Break lines at ":": i=with indent, '
                    'w=without indent, c=colon on line below. '
                    '(Can mix letters together) '
                    f'def: {unravel_colons}')

parser.add_argument("-rb", default=repelcbef, type=str,
                    help='Regex matches to add a space before a keyword and this. '
                    f'def {repelcbef}')

parser.add_argument("-ra", default=repelcaft, type=str,
                    help='Regex matches to add a space after a keyword and this. '
                    f'def {repelcaft}')

parser.add_argument("-jb", default=stripsbef, type=str,
                    help='Regex to force the removal of spaces before matches. '
                    f'def {stripsbef}')

parser.add_argument("-ja", default=stripsaft, type=str,
                    help='Regex to force the removal of spaces after matches. '
                    f'def {stripsaft}')

parser.add_argument("-sb", default=spacesbef, type=str,
                    help='Regex matches to force a space before this. '
                    f'def {spacesbef}')

parser.add_argument("-sa", default=spacesaft, type=str,
                    help='Regex matches to force a space after this. '
                    f'def {spacesaft}')

parser.add_argument("-ft", default=forcetogt, type=str,
                    help='Regex matches forcing this to stick together. '
                    f'def {forcetogt}')

parser.add_argument('-vb', default=verbose_level, type=int,
                    help='Verbosity level: 0=silent, 1=errors, '
                    '2=1+warnings, 3=2+steps(def), 4=3+details. '
                    f'def {verbose_level}')

args = parser.parse_args()

# Apply chosen settings
file_load = args.input
file_save = args.output
if args.output == '':
    save_path = os.path.dirname(file_load)
    # save_path = '' if save_path == '' else save_path
    save_temp = os.path.basename(file_load)
    save_temp = os.path.splitext(save_temp)[0] + '.bad'
    file_save = os.path.join(save_path, save_temp)
conv_lower = args.tl
keep_spcs = args.ks
conv_locprt = args.cp
format_label = args.fl
format_rems = args.fr
unravel_colons = args.uc
unravel_if = args.ut
repelcbef = args.rb
repelcaft = args.ra
stripsbef = args.jb
stripsaft = args.ja
spacesbef = args.sb
spacesaft = args.sa
forcetogt = args.ft
verbose_level = args.vb

keywords = instr + funct + branc
keywords.sort(key=len, reverse=True)

# Regexes
keyw_list = '|'.join(keywords)
rejkwnum = fr'((?={keyw_list})|[EDed])'
rejkwvar = fr'(?={keyw_list}|[^a-z0-9])'
elements = (r'(?:'
            r'%s'
            fr'|(?P<flo>\d*\.\d+{rejkwnum}?[+-]?\d*)'
            fr'|(?P<int>\d+{rejkwnum}?)'
            fr'|(?P<key>{keyw_list})'
            fr'|(?P<var>[a-z]({rejkwvar}|[a-z0-9]*?{rejkwvar})[!#$%%]?)'
            fr'|(?P<glu>{forcetogt})'
            r'|(?P<col>:)'
            r'|(?P<ret>\r)'
            r'|(?P<spc>\s+)'
            r'|(?P<msc>.)'
            r')'
            )

match_int = re.compile(r'\s*\d+')
has_print = re.compile(r'([^:]+?)(?::\s*print)', re.I)
get_fornv = re.compile(r'(\s*\w*\s*,?\s*)*?(?=then|else|:|\r)', re.I)

getstrings = r'(?P<lit>"(?:[^"]*)((?:")|(?=\r)))'
to_endline = r'(?P<lit>.*(?=\r))'
to_endsect = r'(?P<lit>(("(?:[^"]*)((?:")|(?=\r)))?.*?)*?(?=\:|\r))'
# to_endsect = r'(?P<lit>.*?(?=\:|\r))'

match_elements = re.compile(elements % getstrings, re.I)
match_tendline = re.compile(elements % to_endline, re.I)
match_tendsect = re.compile(elements % to_endsect, re.I)


def show_log(line_number, text, level, **kwargs):
    '''Display log output
    '''
    bullets = ['', '*** ', '  * ', '--- ', '  - ', '    ']
    try:
        bullet = kwargs['bullet']
    except KeyError:
        bullet = level

    display_file_name = ''
    line_number = '(' + str(line_number) + '): ' if line_number != '' else ''

    if verbose_level >= level:
        print(bullets[bullet] + display_file_name + line_number + text)

    if bullet == 1:
        print('    Execution_stoped')
        print()
        raise SystemExit(0)


def load_file(file_load):
    '''Load a text file into a list
    '''
    show_log('', 'Loading file', 3)
    classic_code = []
    if file_load:
        try:
            with open(file_load, 'r', encoding='latin1') as f:
                for line in f:
                    classic_code.append(line.strip())
            return classic_code
        except IOError:
            show_log('', f'Source_not_found {file_load}', 1)  # Exit
    else:
        show_log('', 'Source_not_given', 1)  # Exit


def save_file(dignified_code, file_save):
    '''Save a text file from a list
    '''
    show_log('', 'File saving', 3)
    try:
        with open(file_save, 'w') as f:
            for line in dignified_code:
                f.write(line)
    except IOError as e:
        show_log('', str(e), 1)  # Exit


def force_space(match, p_match, n_match):
    '''Force a space berore or after a regex match
    '''
    if re.match(spacesbef, match.strip(), re.I) and p_match != ' ':
        match = ' ' + match
    if re.match(spacesaft, match.strip(), re.I) and n_match != ' ':
        match = match + ' '
    return match


def check_space(char, pattern, g):
    '''Add space before or after keywords depending on regex matches
    Do not add space before '(' if keyword is a function
    '''
    match = g.group().upper().replace('$', r'\$')
    if g.lastgroup == 'key' and match in funct:
        pattern = pattern.replace('(', '')
    space = ''
    if re.match(pattern, char, re.I):
        space = ' '
    return space


def check_labels(dignified_dict, labels, rem_lines):
    '''Check for branching labels without line labels
    '''
    show_log('', 'Checking for branching errors', 3)
    for line in sorted(labels.keys()):
        if line not in dignified_dict:
            if line in rem_lines and 'k' in format_rems:
                show_log(line, f'Added_labels_for_removed_REMs: {labels[line]}', 4)
                dignified_dict[line] = ('', 0)
            else:
                for line_i in labels[line]:
                    show_log(line_i, f'Line_does_not_exist: {line}', 2)


def assemble_dignified(dignified_dict, labels, rem_lines):
    '''Create the final list with the Dignified code
    making some final formatting
    '''
    show_log('', 'Assembling Dignified code', 3)
    label_indent = ''
    dignified_code = []

    for line in sorted(dignified_dict.keys()):
        if line in labels:
            if 's' in format_label:
                dignified_code.append('\n')

            if 'i' in format_label:
                label_indent = '\t'

            dignified_code.append(f'{{l_{str(int(line))}}}\n')

        line_indent = dignified_dict[line][1] * '\t'
        all_indent = label_indent + line_indent

        if line not in rem_lines:
            dignified_code.append(all_indent + dignified_dict[line][0] + '\n')

    return dignified_code


def do_lines(lnumber, line):
    '''Process a line of the classic code
    '''
    p = 0
    g = re.match(r'', '')
    indent = 0
    indent_acc = 0
    match = ' '
    dig_line = ''
    rem_line = ''
    carry_match = False
    temp_for = 0
    unravel = ('i' in unravel_colons or 'w' in unravel_colons)
    dig_list = []
    branch_l = []
    keep_caps = False
    is_branching = False
    match_current = match_elements
    while p < len(line):
        split = False
        carry_match = False
        lone_match = False

        p_match = ''
        prev_spc = ''
        if match:
            p_match = match[-1].upper()
            prev_spc = check_space(p_match, repelcbef, g)

        g = match_current.match(line, p)
        p = g.end()
        match = g.group()
        match_current = match_elements
        next_int = match_int.match(line, p)

        n_match = line[p:p + 1].upper()
        next_spc = check_space(n_match, repelcaft, g)

        if g.lastgroup == 'spc' and not keep_spcs:
            match = ' '
            if (re.match(stripsaft, n_match)
                    or re.match(stripsbef, p_match)):
                match = ''

        if is_branching and (match != ','
                             and g.lastgroup != 'int'
                             and g.lastgroup != 'spc'):
            is_branching = False

        if g.group('key'):
            match = match.upper()

            if p < len(line):
                if match == 'REM' or match == "'":
                    match_current = match_tendline

                    if (('l' in format_rems or 'b' in format_rems)
                            and not dig_list and not dig_line):
                        if 'b' not in format_rems or line[p:].strip():
                            p = len(line)
                            rem_line = lnumber

                        match = ''

                    if (('i' in format_rems or 'm' in format_rems)
                            and (dig_list or dig_line)):

                        if 'm' in format_rems:
                            match = match.lower() if conv_lower else match
                            dig_list.insert(0, (match + line[p:], 0))

                        p = len(line) - 1
                        if dig_line == ':':
                            p = len(line)

                        if not dig_line.strip():
                            p = len(line)
                            dig_list[-1][0] = dig_list[-1][0][:-1]
                        else:
                            dig_line = dig_line.strip().strip(':')

                        match = ''

                elif match == 'DATA':
                    match_current = match_tendsect

                # elif match == 'LOCATE' and conv_locprt:
                #     if haslp_g := has_print.match(line, p):
                #         locparg = haslp_g.group(1) + '\r'
                #         locpinf = do_lines(-1, locparg)[0]
                #         locpinf = locpinf[0][0]
                #         locpinf = locpinf.replace(' ', '')
                #         # locpinf = locpinf.rstrip()
                #         match = f'[?]{locpinf}'
                #         p = haslp_g.end()
                #         next_spc = ''
                #         if line[p] != ' ':
                #             next_spc = ' '

                elif match == 'IF' and 'f' in unravel_if:
                    unravel = True

                    if dig_line.strip() and dig_line.strip() != ':':
                        split = True
                        carry_match = True

                        if not dig_line.rstrip().endswith(':'):
                            dig_line = dig_line.rstrip() + ' _'
                        elif 'c' in unravel_colons:
                            dig_line = dig_line[:-1]
                            match = ':' + match

                elif match == 'THEN' or match == 'ELSE':
                    a, b = 't', 'n'
                    if match == 'ELSE':
                        a, b = 'e', 's'

                    c = 0
                    if a in unravel_if and dig_line.strip():
                        c += 1
                        carry_match = True

                        if not dig_line.rstrip().endswith(':'):
                            split = True
                            dig_line = dig_line.rstrip() + ' _'
                        elif 'c' in unravel_colons:
                            dig_line = dig_line[:-1]
                            match = ':' + match

                    if b in unravel_if and not next_int:
                        split = True
                        c += 1

                        if line[p:].strip().startswith(':'):
                            if 'c' not in unravel_colons:
                                line = line[p:].lstrip().lstrip(':')
                                match += ':'
                                p = 0
                        else:
                            match = match.rstrip() + ' _'

                    if c == 2:
                        lone_match = True

                elif match == 'FOR' and 'f' in unravel_for:
                    temp_for += 1
                    unravel = bool(temp_for)

                    if dig_line.strip() and dig_line.strip() != ':':
                        split = True
                        carry_match = True

                        if not dig_line.rstrip().endswith(':'):
                            dig_line = dig_line.rstrip() + ' _'
                        elif 'c' in unravel_colons:
                            dig_line = dig_line[:-1]
                            match = ':' + match

                elif match == 'NEXT' and 'f' in unravel_for:
                    temp_for -= 1
                    unravel = bool(temp_for)

                    fn_varg = get_fornv.match(line, p)
                    fn_vars = fn_varg.group()
                    match = match.rstrip() + ' ' + fn_vars.strip()
                    p = fn_varg.end()

                    c = 0
                    if dig_line.strip():
                        c += 1
                        carry_match = True

                        if not dig_line.rstrip().endswith(':'):
                            split = True
                            dig_line = dig_line.rstrip() + ' _'
                        elif 'c' in unravel_colons:
                            dig_line = dig_line[:-1]
                            match = ':' + match

                        split = True
                        c += 1

                        if line[p:].strip().startswith(':'):
                            if 'c' not in unravel_colons:
                                line = line[p:].lstrip().lstrip(':')
                                match += ':'
                                p = 0
                        else:
                            match = match.rstrip() + ' _'

                    if c == 2:
                        lone_match = True

                    # if line[p:p + 1].strip() != ':':
                    #     match = match.rstrip() + ' _'
                    #     nx_count += 1

            if match in branc:
                is_branching = True

            match = prev_spc + match + next_spc

        elif g.group('int') and is_branching:
            if int(match) == lnumber:
                match = '{@}'
            else:
                branch_l.append(int(match))
                match = f'{{l_{match.strip()}}}'

        elif g.group('lit'):
            keep_caps = True

        if (unravel and (g.group('col')) or g.group('ret')):
            split = True
            if 'c' in unravel_colons:
                carry_match = True

        if not keep_caps and conv_lower:
            match = match.lower()

        match = force_space(match, p_match, n_match)

        if not carry_match:
            dig_line += match

        # if lnumber >= 0:
        #     show_log(lnumber, f'{g.lastgroup} {match} {split}', 3)
        #     if g.lastgroup == 'ret':
        #         show_log('', '', 3)

        if split:
            dig_list.append([dig_line.lstrip(), indent])
            line = line[p:]
            p = 0
            if 'i' in unravel_colons and len(dig_list) == 1:
                indent_acc += 1

            dig_line = ''

            indent = indent_acc

            if lone_match:
                dig_list.append([match.lstrip(), indent])
                match = ''
            if carry_match:
                dig_line += match

        keep_caps = False

    return dig_list, branch_l, rem_line


def dignify(classic_code):
    '''Process each line of the classic code
    '''
    show_log('', 'Converting lines', 3)
    lnumber = 0
    prev_line = 0
    rem_lines = []
    labels = {}
    dignified_dict = {}
    for line in classic_code:
        line = line.strip()

        if line == '':
            continue

        if line == '':
            show_log(prev_line, f'Blank_line_(after)', 2)
            continue

        if line.isdigit():
            show_log(line, 'Line_number_alone', 2)
            continue

        if not line[0].isdigit():
            show_log(lnumber, 'No_line_number_(after)', 1)  # Exit

        g = match_elements.match(line)
        p = g.end()

        line = line[p:].strip() + '\r'

        lnumber = int(g.group())
        if lnumber <= prev_line:
            show_log(lnumber, 'Line_number_out_of_order', 1)  # Exit

        prev_line = lnumber

        dig_list, branch_l, rem_line = do_lines(lnumber, line)

        if rem_line:
            rem_lines.append(rem_line)

        for label_line in branch_l:
            if label_line not in labels:
                labels[label_line] = [lnumber]
            else:
                labels[label_line].append(lnumber)

        for n, dig_line in enumerate(dig_list):
            clean_lnum = lnumber + (n / 100)
            dignified_dict[clean_lnum] = dig_line

    check_labels(dignified_dict, labels, rem_lines)

    return assemble_dignified(dignified_dict, labels, rem_lines)


def main():

    classic_code = load_file(file_load)
    dignified_code = dignify(classic_code)
    save_file(dignified_code, file_save)


if __name__ == '__main__':
    main()
