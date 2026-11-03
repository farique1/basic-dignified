#!/usr/bin/env python3
'''
ZX81 Basic DignifieR
v1.0
Convert numbered classic ZX-81 BASIC to the Basic Dignified format.

Part of the Basic Dignified Suite
https://github.com/farique1/basic-dignified

Based on MSX Basic DignifieR by Fred Rique (farique).
'''

import re
import os.path
import argparse

# Keyword lists
instr = ['COPY', 'RETURN', 'CLEAR', 'UNPLOT', 'CLS', 'IF', 'RANDOMIZE', 'RAND',
         'SAVE', 'RUN', 'PLOT', 'PRINT', 'POKE', 'NEXT', 'PAUSE', 'LET', 'LIST',
         'LOAD', 'INPUT', 'GOSUB', 'GOTO', 'FOR', 'REM', 'DIM', 'CONTINUE',
         'CONT', 'SCROLL', 'NEW', 'FAST', 'SLOW', 'STOP', 'LLIST', 'LPRINT',
         'STEP', 'TO', 'THEN', 'AND', 'OR', 'NOT']

funct = ['CHR$', 'STR$', 'INKEY$', 'USR', 'PEEK', 'ABS', 'SGN', 'SQR', 'INT',
         'EXP', 'LN', 'ATN', 'ACS', 'ASN', 'TAN', 'COS', 'SIN', 'LEN', 'VAL',
         'CODE', 'TAB', 'AT', 'PI', 'RND']

branc = ['GOTO', 'GOSUB', 'RUN', 'LIST', 'LLIST']

# Words with a special meaning in Basic Dignified
dignified_kw = ['DEFINE', 'DECLARE', 'INCLUDE', 'KEEP', 'ENDIF', 'FUNC', 'RET',
                'EXIT', 'TRUE', 'FALSE']

# User variables
file_load = ''         # Source file
file_save = ''         # Destination file
conv_lower = True      # Convert non literals to lowercase
keep_spcs = False      # Keep original spacing
conv_printat = True    # Convert PRINT AT r,c; to [?](r,c)
format_label = 'is'    # Format labels: i=indent lines, s=blank line before
format_rems = ''       # Process REMs: l=remove REM lines, b=empty REMs become blank lines
unravel_if = ''        # Break IF lines: t=after THEN, n=before THEN
rename_vars = ''       # Rename variables: old:new,old$:new$
verbose_level = 3      # Show processing status: 0-silent 1-+errors 2-+warnings 3-+steps 4-+details

ELEMENTS = re.compile(r'(?P<hex>\\\{[0-9A-Fa-f]{2}\})'
                      r'|(?P<str>"(?:""|\\.|[^"\\])*(?:"|$))'
                      r'|(?P<num>(?:\d+\.?\d*|\.\d+)(?:E[+-]?\d+)?)'
                      r'|(?P<word>GO\s*TO(?![A-Z0-9$])|GO\s*SUB(?![A-Z0-9$])'
                      r'|[A-Z][A-Z0-9]*\$?)'
                      r'|(?P<spc>\s+)'
                      r'|(?P<op>\*\*|<>|<=|>=|\\..|.)', re.I)
LINE = re.compile(r'^\s*(\d+)\s?(.*)$')
NAME = re.compile(r'^[a-z][a-z0-9_]*\$?$', re.I)
ALNUM = ('num', 'word', 'kw', 'fn', 'str', 'label', 'define')


def get_settings(argv=None):
    '''Read the command line arguments, using the user variables as defaults'''
    parser = argparse.ArgumentParser(description='Convert classic ZX-81 BASIC to '
                                                 'the Basic Dignified format.')

    parser.add_argument('input', nargs='?', default=file_load,
                        help='Source file (.AZX or a numbered .DZX)')

    parser.add_argument('output', nargs='?', default=file_save,
                        help='Destination file ([source].DZX) if missing')

    parser.add_argument('-tl', default=conv_lower, action='store_false',
                        help=f'Do not make lower case all non literal text. def: {conv_lower}')

    parser.add_argument('-ks', default=keep_spcs, action='store_true',
                        help=f'Keep original spacing. def: {keep_spcs}')

    parser.add_argument('-cp', default=conv_printat, action='store_false',
                        help=f'Do not convert PRINT AT r,c; to [?](r,c). def: {conv_printat}')

    parser.add_argument('-fl', default=format_label, type=str.lower,
                        help='Format labels: i=indent non label lines, s=blank line '
                        f'before label. (Can mix letters together) def: {format_label}')

    parser.add_argument('-fr', default=format_rems, type=str.lower,
                        help='Format REMs: l=remove REM lines, b=empty REMs become '
                        f'blank lines. (Can mix letters together) def: {format_rems}')

    parser.add_argument('-ut', default=unravel_if, type=str.lower,
                        help='Break IF lines: t=after THEN, n=before THEN. '
                        f'(Can mix letters together) def: {unravel_if}')

    parser.add_argument('-rv', default=rename_vars, type=str,
                        help='Rename variables: old:new,old$:new$. '
                        f'def: {rename_vars}')

    parser.add_argument('-vb', default=verbose_level, type=int,
                        help='Verbosity level: 0=silent, 1=errors, 2=1+warnings, '
                        f'3=2+steps, 4=3+details. def: {verbose_level}')

    args = parser.parse_args(argv)

    for option, letters in (('-fl', 'is'), ('-fr', 'lb'), ('-ut', 'tn')):
        value = getattr(args, option[1:])
        if set(value) - set(letters):
            parser.error(f'{option} accepts only the letters: {letters}')

    if not args.output:
        base = os.path.splitext(args.input)[0]
        args.output = base + '.DZX'
        if os.path.normcase(os.path.abspath(args.output)) \
                == os.path.normcase(os.path.abspath(args.input)):
            args.output = base + '_dig.DZX'

    return args


def show_log(line_number, text, level, **kwargs):
    '''Display log output'''
    bullets = ['', '*** ', '  * ', '--- ', '  - ', '    ']
    bullet = kwargs.get('bullet', level)
    line_number = f'({line_number}): ' if line_number != '' else ''

    if stg.vb >= level:
        print(bullets[bullet] + line_number + text)

    if bullet == 1:
        print('    Execution_stopped')
        print()
        raise SystemExit(1)


def load_file(file_load):
    '''Load a text file into a list'''
    show_log('', 'Loading file', 3)
    if not file_load:
        show_log('', 'Source_not_given', 1)
    try:
        with open(file_load, 'r', encoding='latin1') as f:
            return [line.rstrip() for line in f]
    except IOError:
        show_log('', f'Source_not_found {file_load}', 1)


def save_file(dignified_code, file_save):
    '''Save a text file from a list'''
    show_log('', 'File saving', 3)
    try:
        with open(file_save, 'w', encoding='latin1', newline='\n') as f:
            for line in dignified_code:
                f.write(line + '\n')
    except IOError as e:
        show_log('', str(e), 1)


def get_renames(lnumber=''):
    '''Parse the old:new variable rename list'''
    renames = {}
    for pair in filter(None, (p.strip() for p in stg.rv.split(','))):
        old, _, new = pair.partition(':')
        old, new = old.strip().lower(), new.strip().lower()
        if not NAME.match(old) or not NAME.match(new) or old.endswith('$') != new.endswith('$'):
            show_log(lnumber, f'Invalid_rename: {pair}', 1)
        if new.rstrip('$').upper() in instr + funct + dignified_kw \
                or new.upper() in funct:
            show_log(lnumber, f'Rename_is_a_keyword: {pair}', 1)
        renames[old] = new
    return renames


def tokenize(lnumber, body):
    '''Split a line body into (kind, text) elements'''
    tokens = []
    p = 0
    while p < len(body):
        g = ELEMENTS.match(body, p)
        kind, text = g.lastgroup, g.group()
        p = g.end()

        if kind == 'word':
            upper = re.sub(r'\s+', '', text.upper())
            if upper == 'REM':
                tokens.append(('rem', ('rem' if stg.tl else 'REM') + body[p:]))
                break
            if upper in instr:
                kind, text = 'kw', upper
            elif upper in funct:
                kind, text = 'fn', upper
            elif upper in dignified_kw:
                show_log(lnumber, f'Variable_is_a_Dignified_keyword: {text} (use -rv)', 2)
            if stg.tl and kind != 'str':
                text = text.lower()

        tokens.append((kind, text))
    return tokens


def code_after(tokens, i):
    '''Index of the next non space element'''
    i += 1
    while i < len(tokens) and tokens[i][0] == 'spc':
        i += 1
    return i


def needs_space(prev, cur):
    '''Spaces required by the Dignified syntax and readability'''
    pk, pt = prev
    ck, ct = cur
    if pk == 'define':
        return True
    if pk == 'kw':
        return ct not in (',', ';', ')')
    if ck in ('kw', 'rem'):
        return pk in ALNUM or pt == ')'
    if pk == 'fn':
        return ck in ('num', 'word', 'fn', 'str', 'label')
    if ck == 'fn':
        return pk in ALNUM or pt == ')'
    return pk in ('num', 'word') and ck in ('num', 'word')


def render(tokens):
    '''Join elements with the appropriate spacing'''
    out = ''
    prev = None
    pending = ''
    for kind, text in tokens:
        if kind == 'spc':
            pending = text
            continue
        if prev is not None:
            if prev[0] == 'hex' or kind == 'hex':
                # A space before \{7E} changes how the tokenizer stores a number.
                out += ' ' if pending else ''
            elif needs_space(prev, (kind, text)):
                out += pending if stg.ks and pending else ' '
            elif stg.ks:
                out += pending
        out += text
        prev = (kind, text)
        pending = ''
    return out


def convert_print_at(tokens):
    '''Replace PRINT AT r,c; with [?](r,c)'''
    result = []
    i = 0
    while i < len(tokens):
        kind, text = tokens[i]
        j = code_after(tokens, i)
        if kind == 'kw' and text.upper() == 'PRINT' and j < len(tokens) \
                and tokens[j][0] == 'fn' and tokens[j][1].upper() == 'AT':
            parts = [[]]
            depth = 0
            j += 1
            while j < len(tokens):
                part_text = tokens[j][1]
                if part_text == '(':
                    depth += 1
                elif part_text == ')':
                    depth -= 1
                elif depth == 0 and part_text == ',' and len(parts) == 1:
                    parts.append([])
                    j += 1
                    continue
                elif depth == 0 and part_text in (',', ';'):
                    break
                parts[-1].append(tokens[j])
                j += 1
            if j < len(tokens) and tokens[j][1] == ';' and len(parts) == 2 \
                    and all(render(part).strip() for part in parts):
                row, column = (render(part).strip() for part in parts)
                result.append(('define', f'[?]({row},{column})'))
                i = j + 1
                continue
        result.append(tokens[i])
        i += 1
    return result


def unravel(tokens):
    '''Split a line around THEN, returning (indent, text) segments'''
    then = next((i for i, t in enumerate(tokens)
                 if t[0] == 'kw' and t[1].upper() == 'THEN'), None)
    if then is None or not stg.ut or code_after(tokens, then) >= len(tokens):
        return [(0, render(tokens))]

    pieces = [tokens]
    if 'n' in stg.ut and 't' in stg.ut:
        pieces = [tokens[:then], tokens[then:then + 1], tokens[then + 1:]]
    elif 'n' in stg.ut:
        pieces = [tokens[:then], tokens[then:]]
    elif 't' in stg.ut:
        pieces = [tokens[:then + 1], tokens[then + 1:]]

    texts = [render(piece).strip() for piece in pieces]
    return [(min(n, 1), text + (' _' if n < len(texts) - 1 else ''))
            for n, text in enumerate(texts)]


def dignify(classic_code):
    '''Process each line of the classic code'''
    show_log('', 'Converting lines', 3)
    renames = get_renames()
    lines = []
    prev_line = -1

    for line in classic_code:
        if not line.strip():
            continue
        if line.lstrip().startswith('#'):
            lines.append((None, [('comment', '##' + line.lstrip()[1:])]))
            continue
        g = LINE.match(line)
        if not g:
            show_log(prev_line if prev_line >= 0 else '', 'No_line_number_(after)', 1)
        lnumber = int(g.group(1))
        if lnumber <= prev_line:
            show_log(lnumber, 'Line_number_out_of_order', 1)
        prev_line = lnumber
        lines.append((lnumber, tokenize(lnumber, g.group(2).rstrip())))

    numbers = [n for n, _ in lines if n is not None]
    variables = {t[1].lower() for _, tokens in lines for t in tokens if t[0] == 'word'}
    for old, new in renames.items():
        if old not in variables:
            show_log('', f'Rename_not_found: {old}', 2)
        if new in variables - set(renames):
            show_log('', f'Rename_clashes_with_variable: {new}', 1)

    labels = set()
    output = []
    for lnumber, tokens in lines:
        if lnumber is None:
            output.append((None, tokens[0][1], False))
            continue

        for i, (kind, text) in enumerate(tokens):
            if kind == 'word' and text.lower() in renames:
                tokens[i] = ('word', renames[text.lower()])
            if kind != 'kw' or text.upper() not in branc:
                continue
            j = code_after(tokens, i)
            if j >= len(tokens):
                continue
            if tokens[j][0] == 'num' and tokens[j][1].isdigit() \
                    and code_after(tokens, j) >= len(tokens):
                wanted = int(tokens[j][1])
                target = next((n for n in numbers if n >= wanted), None)
                if target is None:
                    show_log(lnumber, f'Line_does_not_exist: {wanted}', 2)
                    target = wanted
                elif target != wanted:
                    show_log(lnumber, f'Line_does_not_exist: {wanted} (using {target})', 4)
                if target == lnumber:
                    tokens[j] = ('label', '{@}')
                else:
                    labels.add(target)
                    tokens[j] = ('label', f'{{l_{target}}}')
            else:
                show_log(lnumber, f'Computed_jump_kept: {render(tokens[j:]).strip()}', 2)

        is_rem = tokens and tokens[0][0] == 'rem'
        if is_rem and 'l' in stg.fr:
            output.append((lnumber, '', True))
            continue
        if is_rem and 'b' in stg.fr and not tokens[0][1][3:].strip():
            output.append((lnumber, [(0, '')], False))
            continue

        if stg.cp:
            tokens = convert_print_at(tokens)
        output.append((lnumber, unravel(tokens), False))

    return assemble_dignified(output, labels)


def assemble_dignified(output, labels):
    '''Create the final list with the Dignified code'''
    show_log('', 'Assembling Dignified code', 3)
    label_indent = ''
    dignified_code = []

    for lnumber, segments, removed in output:
        if lnumber is None:
            dignified_code.append(segments)
            continue

        if lnumber in labels:
            if 's' in stg.fl and dignified_code:
                dignified_code.append('')
            if 'i' in stg.fl:
                label_indent = '\t'
            dignified_code.append(f'{{l_{lnumber}}}')

        if removed:
            continue

        for indent, text in segments:
            dignified_code.append(label_indent + '\t' * indent + text if text else '')

    missing = labels - {n for n, _, _ in output}
    for target in sorted(missing):
        show_log('', f'Label_without_line: {{l_{target}}}', 2)

    return dignified_code


def main(argv=None):
    global stg
    stg = get_settings(argv)
    classic_code = load_file(stg.input)
    dignified_code = dignify(classic_code)
    save_file(dignified_code, stg.output)
    show_log('', f'Saved: {stg.output}', 3)


if __name__ == '__main__':
    main()
