#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from lexer import lexer
from yacc import parser
from syntaxtree import Program

def run():
    if len(sys.argv) == 1:
        print("Podaj nazwę pliku.")
        sys.exit(1)
    filename = sys.argv[1]

    with open(filename) as f:
        code = f.read()
    try:
        tuple_tree = parser.parse(code, lexer=lexer)
        tree = Program(tuple_tree)
        mnemonics = tree.translate()
        # mnemonics.lineno = True
        assembler = str(mnemonics)
    except RuntimeError as exc:
        print(exc.message)
        sys.exit(1)

    if len(sys.argv) == 2:
        print(assembler)
    elif len(sys.argv) == 3:
        with open(sys.argv[2], 'w') as f:
            f.write(assembler)

if __name__ == "__main__":
    run()
