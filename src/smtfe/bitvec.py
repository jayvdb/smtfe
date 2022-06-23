from .variable import Variable


class BitVec(Variable):
    def __init__(self, name=None, bits=1):
        self.bits = bits
        super().__init__(name)
