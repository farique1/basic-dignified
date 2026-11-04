from . import tokenizer_interface


class Interface:
    def __init__(self, stg):
        self.stg = stg

    def run(self):
        tokenizer_interface.Run(self.stg).run()


class Expose:
    def __init__(self):
        self.exposed = [tokenizer_interface.Expose()]
