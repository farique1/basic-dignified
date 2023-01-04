import os
import json
from collections import namedtuple

from Modules.Support import infolog


def read_system(SYSTEMS_JSON, system_id):

    # Get information about the current classic system
    if os.path.isfile(SYSTEMS_JSON):
        with open(SYSTEMS_JSON, 'r') as json_file:
            sys_desc = json_file.read()
    else:
        infolog.log(1, f'{SYSTEMS_JSON} not found.')

    try:
        sys_desc = json.loads(sys_desc)[0]

        curr_sys = sys_desc[system_id]

        system = namedtuple('system', 'name '
                                      'dig_ext '
                                      'asc_ext '
                                      'bin_ext '
                                      'lst_ext')

        system = system(curr_sys['name'],
                        curr_sys['dig_ext'],
                        curr_sys['asc_ext'],
                        curr_sys['bin_ext'],
                        curr_sys['lst_ext'])

    except json.decoder.JSONDecodeError:
        infolog.log(1, f'Problem decoding: {SYSTEMS_JSON}')
    except KeyError as e:
        infolog.log(1, f'Missing key on: {SYSTEMS_JSON}: {e}')

    return system
