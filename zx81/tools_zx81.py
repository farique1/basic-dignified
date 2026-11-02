import os.path

from . import emulator_interface as ei
from . import tokenizer_interface as ti


class Interface:
    def __init__(self, e_stg):
        self.stg = e_stg

    def run(self):
        tokenizer = ti.Run(self.stg)
        tokenizer.run()

        if tokenizer.stg.tokenize and os.path.isfile(tokenizer.stg.file_bin):
            self.stg.file_save = tokenizer.stg.file_bin

        emulator = ei.Run(self.stg)
        emulator.run()


class Expose:
    def __init__(self):
        self.exposed = [ei.Expose(), ti.Expose()]