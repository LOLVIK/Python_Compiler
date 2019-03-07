class Mnemo(object):
    def __init__(self, pos, arg=None):
        self.pos = pos
        self.arg = arg

class GET(Mnemo):
    def __str__(self):
        return "GET\n"

class PUT(Mnemo):
    def __str__(self):
        return "PUT\n"

class LOAD(Mnemo):
    def __str__(self):
        return "LOAD {}\n".format(self.arg)

class LOADI(Mnemo):
    def __str__(self):
        return "LOADI {}\n".format(self.arg)

class STORE(Mnemo):
    def __str__(self):
        return "STORE {}\n".format(self.arg)

class STOREI(Mnemo):
    def __str__(self):
        return "STOREI {}\n".format(self.arg)

class ADD(Mnemo):
    def __str__(self):
        return "ADD {}\n".format(self.arg)

class ADDI(Mnemo):
    def __str__(self):
        return "ADDI {}\n".format(self.arg)

class SUB(Mnemo):
    def __str__(self):
        return "SUB {}\n".format(self.arg)

class SUBI(Mnemo):
    def __str__(self):
        return "SUBI {}\n".format(self.arg)

class SHR(Mnemo):
    def __str__(self):
        return "SHR\n"

class SHL(Mnemo):
    def __str__(self):
        return "SHL\n"

class INC(Mnemo):
    def __str__(self):
        return "INC\n"

class DEC(Mnemo):
    def __str__(self):
        return "DEC\n"

class ZERO(Mnemo):
    def __str__(self):
        return "ZERO\n"

class JUMP(Mnemo):
    def __str__(self):
        return "JUMP {}\n".format(self.pos + self.arg)

class JZERO(Mnemo):
    def __str__(self):
        return "JZERO {}\n".format(self.pos + self.arg)

class JODD(Mnemo):
    def __str__(self):
        return "JODD {}\n".format(self.pos + self.arg)

class HALT(Mnemo):
    def __str__(self):
        return "HALT\n"


class MnemoList(object):
    def __init__(self, current_pos=0):
        self._current_pos = current_pos
        self._list = []
        self.lineno = False

    def add(self, mnemo_type, arg=None):
        pos = len(self._list) + self._current_pos
        mnemo = mnemo_type(pos, arg=arg)
        self._list.append(mnemo)
        return mnemo

    def __str__(self):
        if self.lineno:
            mnemo_format = '{lineno}:\t{mnemo}'
        else:
            mnemo_format = '{mnemo}'
        code = ''
        for lineno, mnemonic in enumerate(self._list):
            code += mnemo_format.format(lineno=lineno, mnemo=str(mnemonic))
        return code
