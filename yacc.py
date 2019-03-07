import ply.yacc as yacc
import lexer
from errors import invalid_syntax, unexpected_eof

#Taking the tokens map from the lexer
#from lexer import tokens
tokens = lexer.tokens 

def p_program(p):
    '''program : VAR vdeclarations BEGIN commands END'''
    p[0] = ('program', p[2], p[4])
        
def p_vdeclarations(p):
    '''vdeclarations : vdeclarations PIDENTIFIER
                    | vdeclarations PIDENTIFIER LBRACKET NUM RBRACKET
                    |  
    '''
    if len(p) == 3:
        p[0] = ('vdeclarations', p[1], p[2])
    elif len(p) == 6:
        p[0] = ('vdeclarations', p[1], p[2], p[4])
    else:
        p[0] = ('vdeclarations',)


def p_commands(p):
    '''commands : commands command
                | command
    '''
    if len(p) == 3:
        p[0] = ('commands', p[1], p[2])
    else:
        p[0] = ('commands', p[1])

def p_command(p):
    '''command : identifier ASGN expression SEMI
                | IF condition THEN commands ELSE commands ENDIF
                | IF condition THEN commands ENDIF
                | WHILE condition DO commands ENDWHILE
                | FOR PIDENTIFIER FROM value TO value DO commands ENDFOR
                | FOR PIDENTIFIER FROM value DOWNTO value DO commands ENDFOR
                | READ identifier SEMI
                | WRITE value SEMI
    '''
    if len(p) == 5:
        p[0] = ('command', 'asgn', p[1], p[3])
    elif p[1] == 'IF' and p[5] == 'ELSE':
        p[0] = ('command', 'ifelse', p[2], p[4], p[6])
    elif p[1] == 'IF' and p[5] == 'ENDIF':
        p[0] = ('command', 'if', p[2], p[4])
    elif p[1] == 'WHILE':
        p[0] = ('command', 'while', p[2], p[4])
    elif p[1] == 'FOR' and p[5] == 'TO':
        p[0] = ('command', 'forto', p[2], p[4], p[6], p[8])
    elif p[1] == 'FOR' and p[5] =='DOWNTO':
        p[0] = ('command', 'fordownto', p[2], p[4], p[6], p[8])
    elif p[1] == 'READ':
        p[0] = ('command', 'read', p[2])
    elif p[1] == 'WRITE':
        p[0] = ('command', 'write', p[2])


    


def p_expression(p):
    '''expression : value ADD value
                  | value SUB value
                  | value MUL value
                  | value DIV value
                  | value MOD value
                  | value
    '''
    if len(p) == 2:
        p[0] = ('expression', p[1])
    elif p[2] == '+':
        p[0] = ('expression', 'add', p[1], p[3])
    elif p[2] == '-':
        p[0] = ('expression', 'subtract', p[1], p[3])
    elif p[2] == '*':
        p[0] = ('expression', 'multiply', p[1], p[3])
    elif p[2] == '/':
        p[0] = ('expression', 'divide', p[1], p[3])
    elif p[2] == '%':
        p[0] = ('expression', 'modulo', p[1], p[3])

def p_condition(p):
    '''condition : value EQUAL value
                 | value DIFF value
                 | value SMALL value
                 | value GREAT value
                 | value SMEQ value
                 | value GREQ value
    '''
    if p[2] == '=':
        p[0] = ('condition', 'equal', p[1], p[3])
    elif p[2] == '<>':
        p[0] = ('condition', 'different', p[1], p[3])
    elif p[2] == '<':
        p[0] = ('condition', 'smaller', p[1], p[3])
    elif p[2] == '>':
        p[0] = ('condition', 'greater', p[1], p[3])
    elif p[2] == '<=':
        p[0] = ('condition', 'smallerORequal', p[1], p[3])
    elif p[2] == '>=':
        p[0] = ('condition', 'greaterORequal', p[1], p[3])



def p_value(p):
    '''value : NUM
             | identifier
    '''
    p[0] = ('value', p[1])

def p_identifier(p):
    '''identifier : PIDENTIFIER
                  | PIDENTIFIER LBRACKET PIDENTIFIER RBRACKET
                  | PIDENTIFIER LBRACKET NUM RBRACKET
    '''
    if len(p) == 2:
        p[0] = ('identifier', 'pid', p[1])
    else:
        p[0] = ('identifier', 'array', p[1], p[3])

# Error rule for syntax errors
def p_error(p):
    if p is None:
        unexpected_eof()
    elif isinstance(p.lineno, int):
        invalid_syntax(p.lineno)
    else:
        invalid_syntax(p.lineno(0))

# Build the parser
parser = yacc.yacc()
