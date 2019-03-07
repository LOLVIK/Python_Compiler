from mnemonics import *
import errors
from symbolstable import Symbols

def unwrap_commands(commands):
    """ OUTPUT:
        deco - decompressed commands to tuple's array
    """
    deco = []
    while len(commands) > 1 and commands[0] == 'commands':
        if len(commands) == 2:
            deco.append(commands[1])
        else:
            deco.append(commands[2])
        commands = commands[1]
    return deco

def generate_commands(commands_tree):
    commands = unwrap_commands(commands_tree)
    command_types = {'asgn': AssignmentCmd,
                     'ifelse': IfElseCmd,
                     'if': IfCmd,
                     'while': WhileCmd,
                     'forto': ForToCmd,
                     'fordownto': ForDowntoCmd,
                     'read': ReadCmd,
                     'write':WriteCmd}
    objects_list = []
    for cmd in commands:
        instance = command_types[cmd[1]](cmd)
        objects_list.append(instance)
    return Commands(objects_list[::-1])


class Program(object):
    """Program """
    def __init__(self, tuple):
        self.declarations = Symbols()
        self._get_declarations(tuple[1])
        self.commands = generate_commands(tuple[2])

    def _get_declarations(self, vdecl):
        try:
            while len(vdecl) > 1:
                if len(vdecl) == 4:
                    self.declarations.add_array(vdecl[2], vdecl[3])
                else:
                    self.declarations.add_variable(vdecl[2])
                vdecl = vdecl[1]
        except RuntimeError as exc:
            # TODO: exc.message = exc.message.format(position)
            raise exc

    def translate(self):
        mnemonic_list = MnemoList()
        added_mnemos = self.commands.translate(mnemonic_list, self.declarations)
        if added_mnemos != len(mnemonic_list._list):
            raise RuntimeError("Something went very wrong with instruction counting...")
        mnemonic_list.add(HALT)
        return mnemonic_list


class Commands(object):
    def __init__(self, command_list):
        self.commands = command_list

    def translate(self, mnemonic_list, declarations):
        mnemo_start = len(mnemonic_list._list)
        added_mnemos = 0

        for cmd in self.commands:
            added_mnemos += cmd.translate(mnemonic_list, declarations)
            if mnemo_start + added_mnemos != len(mnemonic_list._list):
                print("COuNTING WENT WRONG HERE: ", cmd)
                import ipdb;ipdb.set_trace()
        return added_mnemos


class AssignmentCmd(object):
    def __init__(self, tuple):
        self.identifier = Identifier(tuple[2])
        if len(tuple[3]) == 2:
            self.expression = ExpressionValue(tuple[3])
        else:
            self.expression = Expression(tuple[3])

    def translate(self, mnemonic_list, declarations):
        """ Assign value from expression to identifier. """
        if declarations.is_readonly(self.identifier.name):
            errors.assignment_to_readonly_variable(self.identifier.name)
        if self.identifier.type == 'array' and not declarations.is_array(self.identifier.name):
            errors.assignment_to_array_without_index(self.identifier.name)
        if self.identifier.type == 'pid' and declarations.is_array(self.identifier.name):
            errors.trying_to_index_non_array_variable(self.identifier.name)

        addr_temp = declarations.memory_counter; declarations.memory_counter += 1
        added_mnemos = 0
        added_mnemos += self.identifier.translate(mnemonic_list, declarations, just_address=True)
        mnemonic_list.add(STORE, arg=addr_temp); added_mnemos += 1

        added_mnemos += self.expression.translate(mnemonic_list, declarations)
        mnemonic_list.add(STOREI, arg=addr_temp); added_mnemos += 1

        declarations.memory_counter -= 1
        return added_mnemos

class IfElseCmd(object):
    def __init__(self, tuple):
        self.cond = Condition(tuple[2])
        self.commands = generate_commands(tuple[3])
        self.else_commands = generate_commands(tuple[4])

    def translate(self, mnemonic_list, declarations):
        added_mnemos = 0
        added_mnemos += self.cond.translate(mnemonic_list, declarations)

        jzero = mnemonic_list.add(JZERO); added_mnemos += 1
        commands_len = self.commands.translate(mnemonic_list, declarations)
        added_mnemos += commands_len
        jzero.arg = commands_len + 1 + 1

        jump = mnemonic_list.add(JUMP); added_mnemos += 1
        commands_len = self.else_commands.translate(mnemonic_list, declarations)
        added_mnemos += commands_len
        jump.arg = commands_len + 1

        return added_mnemos

class IfCmd(object):
    def __init__(self, tuple):
        self.cond = Condition(tuple[2])
        self.commands = generate_commands(tuple[3])

    def translate(self, mnemonic_list, declarations):
        added_mnemos = 0
        added_mnemos += self.cond.translate(mnemonic_list, declarations)

        jzero = mnemonic_list.add(JZERO); added_mnemos += 1
        commands_len = self.commands.translate(mnemonic_list, declarations)
        added_mnemos += commands_len
        jzero.arg = commands_len + 1
        return added_mnemos


class WhileCmd(object):
    def __init__(self, tuple):
        self.cond = Condition(tuple[2])
        self.commands = generate_commands(tuple[3])

    def translate(self, mnemonic_list, declarations):
        added_mnemos = 0
        cond_len = self.cond.translate(mnemonic_list, declarations)
        added_mnemos += cond_len

        jzero = mnemonic_list.add(JZERO); added_mnemos += 1
        commands_len = self.commands.translate(mnemonic_list, declarations)
        added_mnemos += commands_len
        jzero.arg = commands_len + 1 + 1

        mnemonic_list.add(JUMP, arg=-(commands_len + 1  + cond_len)); added_mnemos += 1

        return added_mnemos


class ForToCmd(object):
    def __init__(self, tuple):
        self.pid = tuple[2]
        self.begin = Value(tuple[3])
        self.end = Value(tuple[4])
        self.commands = generate_commands(tuple[5])

    def translate(self, mnemonic_list, declarations):
        declarations.add_variable(self.pid, readonly=True)
        addr_i = declarations.get_address(self.pid)
        addr_end = declarations.memory_counter; declarations.memory_counter+=1

        added_mnemos = 0
        added_mnemos += self.begin.translate(mnemonic_list, declarations)
        mnemonic_list.add(STORE, arg=addr_i); added_mnemos += 1

        end_translate_len = self.end.translate(mnemonic_list, declarations)
        added_mnemos += end_translate_len
        mnemonic_list.add(STORE, arg=addr_end); added_mnemos += 1

        mnemonic_list.add(LOAD, arg=addr_end); added_mnemos += 1
        mnemonic_list.add(INC); added_mnemos += 1
        mnemonic_list.add(SUB, arg=addr_i); added_mnemos += 1
        jzero = mnemonic_list.add(JZERO); added_mnemos += 1

        cmds_len = self.commands.translate(mnemonic_list, declarations)
        added_mnemos += cmds_len

        mnemonic_list.add(LOAD, arg=addr_i); added_mnemos += 1
        mnemonic_list.add(INC); added_mnemos += 1
        mnemonic_list.add(STORE, arg=addr_i); added_mnemos += 1
        mnemonic_list.add(JUMP, arg= -(7 + cmds_len)); added_mnemos += 1
        jzero.arg = (5 + cmds_len)

        declarations.delete_variable(self.pid)
        return added_mnemos


class ForDowntoCmd(object):
    def __init__(self, tuple):
        self.pid = tuple[2]
        self.begin = Value(tuple[3])
        self.end = Value(tuple[4])
        self.commands = generate_commands(tuple[5])

    def translate(self, mnemonic_list, declarations):
        declarations.add_variable(self.pid, readonly=True)
        addr_i = declarations.get_address(self.pid)
        addr_end = declarations.memory_counter; declarations.memory_counter+=1

        added_mnemos = 0
        added_mnemos += self.begin.translate(mnemonic_list, declarations)
        mnemonic_list.add(STORE, arg=addr_i); added_mnemos += 1

        added_mnemos += self.end.translate(mnemonic_list, declarations)
        mnemonic_list.add(STORE, arg=addr_end); added_mnemos += 1

        # Warunek
        mnemonic_list.add(LOAD, arg=addr_end); added_mnemos += 1
        mnemonic_list.add(SUB, arg=addr_i); added_mnemos += 1
        mnemonic_list.add(JZERO, arg=+2); added_mnemos += 1
        skip = mnemonic_list.add(JUMP); added_mnemos += 1

        # Cialo petli
        cmds_len = self.commands.translate(mnemonic_list, declarations)
        added_mnemos += cmds_len

        # Dekrementacja
        mnemonic_list.add(LOAD, arg=addr_i); added_mnemos += 1
        mnemonic_list.add(JZERO, arg=+4); added_mnemos += 1
        mnemonic_list.add(DEC); added_mnemos += 1
        mnemonic_list.add(STORE, arg=addr_i); added_mnemos += 1

        # Skok do warunku
        mnemonic_list.add(JUMP, arg= -(4 + cmds_len + 4)); added_mnemos += 1
        skip.arg = (6 + cmds_len)

        declarations.delete_variable(self.pid)

        return added_mnemos

class ReadCmd(object):
    def __init__(self, tuple):
        self.identifier = Identifier(tuple[2])

    def translate(self, mnemonic_list, declarations):
        added_mnemos = 0
        added_mnemos += self.identifier.translate(mnemonic_list, declarations,
                                                  just_address=True)
        
        address_temp = declarations.memory_counter; declarations.memory_counter += 1
        mnemonic_list.add(STORE, arg=address_temp); added_mnemos += 1
        mnemonic_list.add(GET); added_mnemos += 1
        mnemonic_list.add(STOREI, arg=address_temp); added_mnemos += 1

        declarations.memory_counter -= 1;
        return added_mnemos


class WriteCmd(object):
    def __init__(self, tuple):
        self.value = Value(tuple[2])

    def translate(self, mnemonic_list, declarations):
        added_mnemos = self.value.translate(mnemonic_list, declarations)
        mnemonic_list.add(PUT); added_mnemos += 1
        return added_mnemos


class Expression(object):
    def __init__(self, tuple):
        self.val1 = Value(tuple[2])
        self.val2 = Value(tuple[3])
        self.action = tuple[1]

        translate_dict = {'add': self._translate_exp_add,
                          'subtract': self._translate_exp_sub,
                          'multiply': self._translate_exp_mul,
                          'divide': self._translate_exp_div,
                          'modulo': self._translate_exp_mod}
        self.translate = translate_dict[tuple[1]]

    def _translate_exp_add(self, mnemonic_list, declarations):
        """ Calculate expression, put the result in register 'a'. """
        addr_temp = declarations.memory_counter; declarations.memory_counter += 1
        added_mnemos = 0
        
        added_mnemos += self.val1.translate(mnemonic_list, declarations)
        mnemonic_list.add(STORE, arg=addr_temp); added_mnemos += 1
        added_mnemos += self.val2.translate(mnemonic_list, declarations)
        mnemonic_list.add(ADD, arg=addr_temp); added_mnemos += 1
        
        declarations.memory_counter -= 1;
        return added_mnemos

    def _translate_exp_sub(self, mnemonic_list, declarations):
        """ Calculate expression, put the result in register 'a'. """
        addr_temp = declarations.memory_counter; declarations.memory_counter += 1
        added_mnemos = 0
        
        added_mnemos += self.val2.translate(mnemonic_list, declarations)
        mnemonic_list.add(STORE, arg=addr_temp); added_mnemos += 1
        added_mnemos += self.val1.translate(mnemonic_list, declarations)
        mnemonic_list.add(SUB, arg=addr_temp); added_mnemos += 1

        declarations.memory_counter -= 1;
        return added_mnemos

    def _translate_exp_mul(self, mnemonic_list, declarations):
        """ Calculate expression, put the result in register 'a'. """
        addr_a = declarations.memory_counter; declarations.memory_counter += 1
        addr_b = declarations.memory_counter; declarations.memory_counter += 1
        addr_result = declarations.memory_counter; declarations.memory_counter += 1

        added_mnemos = 0
        added_mnemos += self.val1.translate(mnemonic_list, declarations)
        mnemonic_list.add(STORE, arg=addr_a); added_mnemos += 1
        added_mnemos += self.val2.translate(mnemonic_list, declarations)
        mnemonic_list.add(STORE, arg=addr_b); added_mnemos += 1
        
        mnemonic_list.add(ZERO); added_mnemos += 1
        mnemonic_list.add(STORE, arg=addr_result); added_mnemos += 1
        mnemonic_list.add(LOAD, arg=addr_b); added_mnemos += 1
        mnemonic_list.add(JZERO, arg=+17); added_mnemos += 1
        mnemonic_list.add(JODD, arg=+7); added_mnemos += 1
        mnemonic_list.add(SHR); added_mnemos += 1
        mnemonic_list.add(STORE, arg=addr_b); added_mnemos += 1
        mnemonic_list.add(LOAD, arg=addr_a); added_mnemos += 1
        mnemonic_list.add(SHL); added_mnemos += 1
        mnemonic_list.add(STORE, arg=addr_a); added_mnemos += 1
        mnemonic_list.add(JUMP, arg=-8); added_mnemos += 1
        mnemonic_list.add(SHR); added_mnemos += 1
        mnemonic_list.add(STORE, arg=addr_b); added_mnemos += 1
        mnemonic_list.add(LOAD, arg=addr_a); added_mnemos += 1
        mnemonic_list.add(SHL); added_mnemos += 1
        mnemonic_list.add(STORE, arg=addr_a); added_mnemos += 1
        mnemonic_list.add(SHR); added_mnemos += 1
        mnemonic_list.add(ADD, arg=addr_result); added_mnemos += 1
        mnemonic_list.add(STORE, arg=addr_result); added_mnemos += 1
        mnemonic_list.add(JUMP, arg=-17); added_mnemos += 1
        mnemonic_list.add(LOAD, arg=addr_result); added_mnemos += 1

        declarations.memory_counter -= 3
        return added_mnemos


    def _translate_exp_div(self, mnemonic_list, declarations):
        """ Calculate expression, put the result in register 'a'. """
        addr_n = declarations.memory_counter; declarations.memory_counter += 1
        addr_m = declarations.memory_counter; declarations.memory_counter += 1
        addr_c = declarations.memory_counter; declarations.memory_counter += 1
        addr_mul = declarations.memory_counter; declarations.memory_counter += 1
        addr_result = declarations.memory_counter; declarations.memory_counter += 1
        addr_add = declarations.memory_counter; declarations.memory_counter += 1
        addr_temp =  declarations.memory_counter; declarations.memory_counter += 1

        added_mnemos = 0
        added_mnemos += self.val1.translate(mnemonic_list, declarations)
        mnemonic_list.add(STORE, arg=addr_n); added_mnemos += 1
        mnemonic_list.add(JZERO, arg=+50); added_mnemos += 1

        added_mnemos += self.val2.translate(mnemonic_list, declarations)
        mnemonic_list.add(STORE, arg=addr_m); added_mnemos += 1
        mnemonic_list.add(JZERO, arg=+48); added_mnemos += 1

        mnemonic_list.add(LOAD, arg=addr_n); added_mnemos += 1
        mnemonic_list.add(SUB, arg=addr_m); added_mnemos += 1
        mnemonic_list.add(JZERO, arg=+41); added_mnemos += 1
        mnemonic_list.add(ZERO); added_mnemos += 1
        mnemonic_list.add(INC); added_mnemos += 1
        mnemonic_list.add(STORE, arg=addr_c); added_mnemos += 1
        mnemonic_list.add(LOAD, arg=addr_m); added_mnemos += 1
        mnemonic_list.add(STORE, arg=addr_mul); added_mnemos += 1
        mnemonic_list.add(LOAD, arg=addr_mul); added_mnemos += 1
        mnemonic_list.add(SUB, arg=addr_n); added_mnemos += 1
        mnemonic_list.add(JZERO, arg=+4); added_mnemos += 1
        mnemonic_list.add(ZERO); added_mnemos += 1
        mnemonic_list.add(STORE, arg=addr_result); added_mnemos += 1
        mnemonic_list.add(JUMP, arg=+8); added_mnemos += 1
        mnemonic_list.add(LOAD, arg=addr_mul); added_mnemos += 1
        mnemonic_list.add(SHL); added_mnemos += 1
        mnemonic_list.add(STORE, arg=addr_mul); added_mnemos += 1
        mnemonic_list.add(LOAD, arg=addr_c); added_mnemos += 1
        mnemonic_list.add(SHL); added_mnemos += 1
        mnemonic_list.add(STORE, arg=addr_c); added_mnemos += 1
        mnemonic_list.add(JUMP, arg=-12); added_mnemos += 1
        mnemonic_list.add(STORE, arg=addr_add); added_mnemos += 1
        mnemonic_list.add(LOAD, arg=addr_c); added_mnemos += 1
        mnemonic_list.add(DEC); added_mnemos += 1
        mnemonic_list.add(JZERO, arg=+26); added_mnemos += 1
        mnemonic_list.add(INC); added_mnemos += 1
        mnemonic_list.add(SHR); added_mnemos += 1
        mnemonic_list.add(STORE, arg=addr_c); added_mnemos += 1
        mnemonic_list.add(LOAD, arg=addr_mul); added_mnemos += 1
        mnemonic_list.add(SHR); added_mnemos += 1
        mnemonic_list.add(STORE, arg=addr_mul); added_mnemos += 1
        mnemonic_list.add(STORE, arg=addr_temp); added_mnemos += 1
        mnemonic_list.add(ADD, arg=addr_add); added_mnemos += 1
        mnemonic_list.add(SUB, arg=addr_n); added_mnemos += 1
        mnemonic_list.add(JZERO, arg=+2); added_mnemos += 1
        mnemonic_list.add(JUMP, arg=-13); added_mnemos += 1
        mnemonic_list.add(LOAD, arg=addr_result); added_mnemos += 1
        mnemonic_list.add(ADD, arg=addr_c); added_mnemos += 1
        mnemonic_list.add(STORE, arg=addr_result); added_mnemos += 1
        mnemonic_list.add(LOAD, arg=addr_add); added_mnemos += 1
        mnemonic_list.add(ADD, arg=addr_temp); added_mnemos += 1
        mnemonic_list.add(STORE, arg=addr_add); added_mnemos += 1
        mnemonic_list.add(JUMP, arg=-20); added_mnemos += 1
        mnemonic_list.add(LOAD, arg=addr_m); added_mnemos += 1
        mnemonic_list.add(SUB, arg=addr_n); added_mnemos += 1
        mnemonic_list.add(JZERO, arg=+3); added_mnemos += 1
        mnemonic_list.add(ZERO); added_mnemos += 1
        mnemonic_list.add(JUMP, arg=+2); added_mnemos += 1
        mnemonic_list.add(INC); added_mnemos += 1
        mnemonic_list.add(STORE, arg=addr_result); added_mnemos += 1
        mnemonic_list.add(LOAD, arg=addr_result); added_mnemos += 1
      

        declarations.memory_counter -= 7
        return added_mnemos


    def _translate_exp_mod(self, mnemonic_list, declarations):
        """ Calculate expression, put the result in register 'a'. """
        addr_n = declarations.memory_counter; declarations.memory_counter += 1
        addr_m = declarations.memory_counter; declarations.memory_counter += 1
        addr_c = declarations.memory_counter; declarations.memory_counter += 1
        addr_mul = declarations.memory_counter; declarations.memory_counter += 1
        addr_a = declarations.memory_counter; declarations.memory_counter += 1
        addr_add = declarations.memory_counter; declarations.memory_counter += 1
        addr_temp =  declarations.memory_counter; declarations.memory_counter += 1

        added_mnemos = 0
        added_mnemos += self.val1.translate(mnemonic_list, declarations)
        mnemonic_list.add(STORE, arg=addr_n); added_mnemos += 1
        mnemonic_list.add(JZERO, arg=+53); added_mnemos += 1

        added_mnemos += self.val2.translate(mnemonic_list, declarations)
        mnemonic_list.add(STORE, arg=addr_m); added_mnemos += 1
        mnemonic_list.add(JZERO, arg=+51); added_mnemos += 1

        mnemonic_list.add(LOAD, arg=addr_n); added_mnemos += 1
        mnemonic_list.add(SUB, arg=addr_m); added_mnemos += 1
        mnemonic_list.add(JZERO, arg=+41); added_mnemos += 1
        mnemonic_list.add(ZERO); added_mnemos += 1
        mnemonic_list.add(INC); added_mnemos += 1
        mnemonic_list.add(STORE, arg=addr_c); added_mnemos += 1
        mnemonic_list.add(LOAD, arg=addr_m); added_mnemos += 1
        mnemonic_list.add(STORE, arg=addr_mul); added_mnemos += 1
        mnemonic_list.add(LOAD, arg=addr_mul); added_mnemos += 1
        mnemonic_list.add(SUB, arg=addr_n); added_mnemos += 1
        mnemonic_list.add(JZERO, arg=+4); added_mnemos += 1
        mnemonic_list.add(ZERO); added_mnemos += 1
        mnemonic_list.add(STORE, arg=addr_a); added_mnemos += 1
        mnemonic_list.add(JUMP, arg=+8); added_mnemos += 1
        mnemonic_list.add(LOAD, arg=addr_mul); added_mnemos += 1
        mnemonic_list.add(SHL); added_mnemos += 1
        mnemonic_list.add(STORE, arg=addr_mul); added_mnemos += 1
        mnemonic_list.add(LOAD, arg=addr_c); added_mnemos += 1
        mnemonic_list.add(SHL); added_mnemos += 1
        mnemonic_list.add(STORE, arg=addr_c); added_mnemos += 1
        mnemonic_list.add(JUMP, arg=-12); added_mnemos += 1
        mnemonic_list.add(STORE, arg=addr_add); added_mnemos += 1
        mnemonic_list.add(LOAD, arg=addr_c); added_mnemos += 1
        mnemonic_list.add(DEC); added_mnemos += 1
        mnemonic_list.add(JZERO, arg=+24); added_mnemos += 1
        mnemonic_list.add(INC); added_mnemos += 1
        mnemonic_list.add(SHR); added_mnemos += 1
        mnemonic_list.add(STORE, arg=addr_c); added_mnemos += 1
        mnemonic_list.add(LOAD, arg=addr_mul); added_mnemos += 1
        mnemonic_list.add(SHR); added_mnemos += 1
        mnemonic_list.add(STORE, arg=addr_mul); added_mnemos += 1
        mnemonic_list.add(STORE, arg=addr_temp); added_mnemos += 1
        mnemonic_list.add(ADD, arg=addr_add); added_mnemos += 1
        mnemonic_list.add(SUB, arg=addr_n); added_mnemos += 1
        mnemonic_list.add(JZERO, arg=+2); added_mnemos += 1
        mnemonic_list.add(JUMP, arg=-13); added_mnemos += 1
        mnemonic_list.add(LOAD, arg=addr_a); added_mnemos += 1
        mnemonic_list.add(ADD, arg=addr_c); added_mnemos += 1
        mnemonic_list.add(STORE, arg=addr_a); added_mnemos += 1
        mnemonic_list.add(LOAD, arg=addr_add); added_mnemos += 1
        mnemonic_list.add(ADD, arg=addr_temp); added_mnemos += 1
        mnemonic_list.add(STORE, arg=addr_add); added_mnemos += 1
        mnemonic_list.add(JUMP, arg=-20); added_mnemos += 1  
        mnemonic_list.add(LOAD, arg=addr_m); added_mnemos += 1
        mnemonic_list.add(SUB, arg=addr_n); added_mnemos += 1
        mnemonic_list.add(JZERO, arg=+5); added_mnemos += 1
        mnemonic_list.add(LOAD, arg=addr_n); added_mnemos += 1
        mnemonic_list.add(JUMP, arg=+3); added_mnemos += 1
        mnemonic_list.add(LOAD, arg=addr_n); added_mnemos += 1
        mnemonic_list.add(SUB, arg=addr_add); added_mnemos += 1
        mnemonic_list.add(STORE, arg=addr_c); added_mnemos += 1
      

        declarations.memory_counter -= 7
        return added_mnemos



class ExpressionValue(object):
    def __init__(self, tuple):
        self.value = Value(tuple[1])

    def translate(self, mnemonic_list, declarations):
        """ Leave the value to the register 'a'. """
        return self.value.translate(mnemonic_list, declarations)


class Condition(object):
    def __init__(self, tuple):
        self.val1 = Value(tuple[2])
        self.val2 = Value(tuple[3])

        translate_dict = {'equal': self._translate_op_eq,
                          'different': self._translate_op_neq,
                          'smaller': self._translate_op_lt,
                          'greater': self._translate_op_gt,
                          'smallerORequal': self._translate_op_lte,
                          'greaterORequal': self._translate_op_gte}
        self.translate = translate_dict[tuple[1]]

    def _translate_op_eq(self, mnemonic_list, declarations):
        """ Calculate condition, leave 0 in register 'a' if it's False,
        anything else otherwise. """
        added_mnemos = 0

        added_mnemos += self.val1.translate(mnemonic_list, declarations)
        address_a = declarations.memory_counter; declarations.memory_counter += 1
        mnemonic_list.add(STORE, arg=address_a); added_mnemos += 1

        added_mnemos += self.val2.translate(mnemonic_list, declarations)
        address_b = declarations.memory_counter; declarations.memory_counter += 1
        mnemonic_list.add(STORE, arg=address_b); added_mnemos += 1

        mnemonic_list.add(SUB, arg=address_a); added_mnemos += 1
        mnemonic_list.add(JZERO, arg=+2); added_mnemos += 1
        mnemonic_list.add(JUMP, arg=+4); added_mnemos += 1
        mnemonic_list.add(LOAD, arg=address_a); added_mnemos += 1
        mnemonic_list.add(SUB, arg=address_b); added_mnemos += 1
        mnemonic_list.add(JZERO, arg=+3); added_mnemos += 1
        mnemonic_list.add(ZERO); added_mnemos += 1
        mnemonic_list.add(JUMP, arg=+2); added_mnemos += 1
        mnemonic_list.add(INC); added_mnemos += 1

        declarations.memory_counter -= 2
        return added_mnemos

    def _translate_op_neq(self, mnemonic_list, declarations):
        """ Calculate condition, leave 0 in register 'a' if it's False,
        anything else otherwise. """
        added_mnemos = self._translate_op_eq(mnemonic_list, declarations)
        mnemonic_list.add(JZERO, arg=+3); added_mnemos += 1
        mnemonic_list.add(ZERO); added_mnemos += 1
        mnemonic_list.add(JUMP, arg=+2); added_mnemos += 1
        mnemonic_list.add(INC); added_mnemos += 1
        return added_mnemos

    def _translate_op_lt(self, mnemonic_list, declarations):
        """ Calculate condition, leave 0 in register 'a' if it's False,
        anything else otherwise. """
        added_mnemos = self._translate_op_neq(mnemonic_list, declarations)
        address_a = declarations.memory_counter; declarations.memory_counter += 1
        address_b = declarations.memory_counter; declarations.memory_counter += 1

        mnemonic_list.add(JZERO, arg=+7); added_mnemos += 1
        mnemonic_list.add(LOAD, arg=address_a); added_mnemos += 1
        mnemonic_list.add(SUB, arg=address_b); added_mnemos += 1
        mnemonic_list.add(JZERO, arg=+3); added_mnemos += 1
        mnemonic_list.add(ZERO); added_mnemos += 1
        mnemonic_list.add(JUMP, arg=+2); added_mnemos += 1
        mnemonic_list.add(INC); added_mnemos += 1

        declarations.memory_counter -= 2
        return added_mnemos

    def _translate_op_gt(self, mnemonic_list, declarations):
        """ Calculate condition, leave 0 in register 'a' if it's False,
        anything else otherwise. """
        # Switch values
        self.val1, self.val2 = self.val2, self.val1
        return self._translate_op_lt(mnemonic_list, declarations)

    def _translate_op_lte(self, mnemonic_list, declarations):
        """ Calculate condition, leave 0 in register 'a' if it's False,
        anything else otherwise. """
        added_mnemos = 0

        added_mnemos += self.val2.translate(mnemonic_list, declarations)
        address_b = declarations.memory_counter; declarations.memory_counter += 1
        mnemonic_list.add(STORE, arg=address_b); added_mnemos += 1

        added_mnemos += self.val1.translate(mnemonic_list, declarations)
        address_a = declarations.memory_counter; declarations.memory_counter += 1
        mnemonic_list.add(STORE, arg=address_a); added_mnemos += 1
        mnemonic_list.add(SUB, arg=address_b); added_mnemos += 1
        mnemonic_list.add(JZERO, arg=+3); added_mnemos += 1
        mnemonic_list.add(ZERO); added_mnemos += 1
        mnemonic_list.add(JUMP, arg=+2); added_mnemos += 1
        mnemonic_list.add(INC); added_mnemos += 1

        declarations.memory_counter -= 2
        return added_mnemos

    def _translate_op_gte(self, mnemonic_list, declarations):
        """ Calculate condition, leave 0 in register 'a' if it's False,
        anything else otherwise. """
        # Switch values
        self.val1, self.val2 = self.val2, self.val1
        return self._translate_op_lte(mnemonic_list, declarations)


class Value(object):
    def __init__(self, tuple):
        if self._isInt(tuple[1]):
            self.value = Number(tuple[1])
        else:
            self.value = Identifier(tuple[1])

    def _isInt(self, x):
        try:
            int(x)
            return True
        except ValueError:
            return False
        except TypeError:
            return False

    def translate(self, mnemonic_list, declarations):
        """ Move the value to the register 'a' """
        return self.value.translate(mnemonic_list, declarations)


class Number(object):
    def __init__(self, number):
        self.number = number

    def translate(self, mnemonic_list, declarations, zero_register=True):
        """ Move the number to register 'a' """
        boolstr = bin(self.number)[2:]

        added_mnemos = 0
        if zero_register:
            mnemonic_list.add(ZERO); added_mnemos += 1

        for digit in boolstr[:-1]:
            if digit == '1':
                mnemonic_list.add(INC); added_mnemos += 1
                mnemonic_list.add(SHL); added_mnemos += 1
            else:
                mnemonic_list.add(SHL); added_mnemos += 1
        if boolstr[-1] == '1':
            mnemonic_list.add(INC); added_mnemos += 1

        return added_mnemos


class Identifier(object):
    def __init__(self, tuple):
        self.name = tuple[2]
        type = tuple[1]
        self.type = type
        if type == 'pid':
            self.translate = self._translate_pid
        elif type == 'array' and self._isInt(tuple[3]):
            self.translate = self._translate_arr_num
            self.index = tuple[3]
            self.type = "array_num"
        else:
            self.translate = self._translate_arr_pid
            self.index = tuple[3]
            self.type = "array_pid"

    def _isInt(self, x):
        try:
            int(x)
            return True
        except ValueError:
            return False
        except TypeError:
            return False

    def _translate_pid(self, mnemonic_list, declarations, just_address=False):
        """ Move value under pid (or its address) to register 'a' """
        if declarations.is_array(self.name):
            errors.trying_to_access_array_as_variable(self.name)

        address = declarations.get_address(self.name)

        if just_address:
            return Number(address).translate(mnemonic_list, declarations)

        mnemonic_list.add(LOAD, arg=address)
        return 1

    def _translate_arr_num(self, mnemonic_list, declarations, just_address=False):
        """ Move value under arr[num] (or its address) to register 'a' """
        if not declarations.is_array(self.name):
            errors.trying_to_access_variable_as_array(self.name)

        address = declarations.get_address(self.name)
        address += self.index

        if just_address:
            return Number(address).translate(mnemonic_list, declarations)

        mnemonic_list.add(LOAD, arg=address)
        return 1

    def _translate_arr_pid(self, mnemonic_list, declarations, just_address=False):
        """ Move value under arr[pid] (or its address) to register 'a' """
        if not declarations.is_array(self.name):
            errors.trying_to_access_variable_as_array(self.name)
        if declarations.is_array(self.index):
            errors.trying_to_access_array_as_variable(self.name)

        added_mnemos = 0

        address = Number(declarations.get_address(self.name))
        added_mnemos += address.translate(mnemonic_list, declarations)

        idx_address = declarations.get_address(self.index)
        mnemonic_list.add(ADD, arg=idx_address)
        added_mnemos += 1


        if just_address:
            return added_mnemos

        temp_addr = declarations.memory_counter; declarations.memory_counter += 1
        mnemonic_list.add(STORE, arg=temp_addr)
        added_mnemos += 1

        mnemonic_list.add(LOADI, arg=temp_addr)
        added_mnemos += 1
        
        declarations.memory_counter -= 1
        return added_mnemos


###### TODO: FIND ALL ERRORS, CHECK IF THEY ARE IMPLEMENTED, ADD POSITION TRACKING
# TODO: UNIINITIALIZED VARS SHOULD THROW ERRORS
