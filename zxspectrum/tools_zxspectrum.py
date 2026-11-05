from . import emulator_interface, tokenizer_interface


class Interface:
    def __init__(self, stg):
        self.stg = stg

    def run(self):
        settings = emulator_interface.Settings(self.stg)
        tapes = tokenizer_interface.Run(self.stg).run(force=settings.run)
        if settings.run:
            emulator_interface.run(self.stg, settings, tapes[0])


class Expose:
    def __init__(self):
        self.exposed = [tokenizer_interface.Expose(), emulator_interface.Expose()]
