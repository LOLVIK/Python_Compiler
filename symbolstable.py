import errors

class Symbols(object):
    def __init__(self):
        self._declarations = {}
        self.memory_counter = 0

    def add_array(self, name, length):
        self._check_name_not_declared_yet(name)
        address = self.memory_counter

        self.memory_counter += length
        self._declarations[name] = [address, length, False, "array", False]

    def add_variable(self, name, readonly=False):
        self._check_name_not_declared_yet(name)
        address = self.memory_counter

        self.memory_counter += 1
        self._declarations[name] = (address, 1, readonly, "variable")

    def delete_variable(self, name):
        # TODO: check if it is array, if not raise (?)
        self.memory_counter -= self.get_length(name)
        del self._declarations[name]

    def is_readonly(self, name):
        self._check_known_symbol(name)
        return self._declarations[name][2]

    def is_array(self, name):
        self._check_known_symbol(name)
        return self._declarations[name][3] == "array"

    def get_length(self, name):
        self._check_known_symbol(name)
        return self._declarations[name][1]

    def get_address(self, name):
        self._check_known_symbol(name)
        return self._declarations[name][0]

    def is_initialized(self, name):
        self._check_known_symbol(name)
        return self._declarations[name][4]

    def mark_initialized(self, name):
        self._check_known_symbol(name)
        self._declarations[name][4] = True

    def _check_name_not_declared_yet(self, name):
        if name in self._declarations:
            errors.variable_already_declared(name)

    def _check_known_symbol(self, name):
        if name not in self._declarations:
            errors.unknown_variable(name)


