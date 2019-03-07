# -*- coding: utf-8 -*-
import ply.lex as lex
from errors import illegal_symbol, unknown_symbol


#-----------------------------------------------------------
#    'VAR', 'BEGIN', 'END',
#    'IF', 'THEN', 'ELSE', 'ENDIF',
#    'WHILE', 'DO', 'ENDWHILE',
#    'FOR', 'FROM', 'TO', 'DOWNTO', 'ENDFOR',
#    'READ', 'WRITE',
#-----------------------------------------------------------
keywords = ['VAR', 'BEGIN', 'END',
            'IF', 'THEN', 'ELSE', 'ENDIF',
            'WHILE', 'DO', 'ENDWHILE',
            'FOR', 'FROM', 'TO', 'DOWNTO', 'ENDFOR',
            'READ', 'WRITE',]

tokens = keywords + [
    'NUM', 'PIDENTIFIER',
    'ASGN',
    'ADD', 'SUB', 'MUL', 'DIV', 'MOD',
    'EQUAL', 'DIFF', 'SMALL', 'GREAT', 'SMEQ', 'GREQ',
    'SEMI', 'COMMENT', 'LBRACKET', 'RBRACKET'
    ]

# Tokens
t_ASGN  = r':='
t_ADD   = r'\+'
t_SUB   = r'-'
t_MUL   = r'\*'
t_DIV   = r'/'
t_MOD   = r'\%'
t_EQUAL = r'='
t_SMALL = r'<'
t_GREAT = r'>'
t_DIFF  = r'<>'
t_SMEQ  = r'<='
t_GREQ  = r'>='
t_SEMI  = r';'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'

t_PIDENTIFIER = r'[_a-z]+'

def t_KEYWORD(t):
    r'[A-Z]+' 
    if t.value in keywords:
        t.type = t.value
        return t
    else:
        unknown_symbol(t.value, t.lexer.lineno)

def t_NUM(t):
    r'\d+'
    t.value = int(t.value)
    return t

t_ignore_COMMENT = r'\([^\)]*\)'
t_ignore_WHITE = r'[ \t]+'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    illegal_symbol(t.lexer.lineno)

# Build the lexer
lexer = lex.lex()

def lextest():
    data = ''
    while True:
        try:
            data += raw_input('lex > ')   # use input() on Python 3
        except EOFError:
            break

    lexer.input(data)

    while True:
        token = lexer.token()
        if token is None:
            break
        print(token)
