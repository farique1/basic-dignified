import os.path

from . import emulator_interface as ei
from . import tokenizer_interface as ti


class Interface:
    '''Run the code on the interfaces and manage the interaction between them'''

    def __init__(self, e_stg):
        self.stg = e_stg

    def run(self):
        runt = ti.Run(self.stg)
        runt.run()

        if runt.stg.tokenize and os.path.isfile(runt.stg.file_bin):
            self.stg.file_save = runt.stg.file_bin

        rune = ei.Run(self.stg)
        rune.run()


class Expose:
    '''Provide the consolidated exposed classes of the interfaces as a list'''

    def __init__(self):
        ex = ei.Expose()
        tx = ti.Expose()
        self.exposed = [ex, tx]
