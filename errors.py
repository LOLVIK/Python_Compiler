def variable_already_declared(name, lineno):
    raise RuntimeError("Error in line {}: variable {} already declared.".format(lineno, name))

def unknown_variable(name):
    raise RuntimeError("Error : unknown variable {}.".format(name))

def unknown_symbol(symbol, lineno):
	raise RuntimeError("Error in line {}: unknown symbol '{}'.".format(lineno, symbol))

def variable_already_declared(name):
	raise RuntimeError("Error: redeclaration of variable '{}'.".format(name))

def illegal_symbol(lineno):
	raise RuntimeError("Error in line {}: illegal symbol.".format(lineno))

def invalid_syntax(lineno):
	raise RuntimeError("Error in line {}: invalid syntax.".format(lineno))

def unexpected_eof():
	raise RuntimeError("Error : unexpected end of file.")

def assignment_to_array_without_index(name):
	raise RuntimeError("Error : assignment to array variable '{}' without subscript.".format(name))

def trying_to_index_non_array_variable(name):
	raise RuntimeError("Error : variable '{}' is not subscriptable.".format(name))

def assignment_to_readonly_variable(name):
	raise RuntimeError("Error : variable '{}' is read-only and cannot be assigned to.").format(name)

def trying_to_access_variable_as_array(name):
	raise RuntimeError("Error : trying to access normal variable '{}' as an array.".format(name))

def trying_to_access_array_as_variable(name):
	raise RuntimeError("Error : trying to access array variable '{}' without a subscript.".format(name))