#### Python_Compiler
College project. Creating a compiler of a given imperative language to the registration machine code

#### THE IMPLEMENTATION LANGUAGE
Python 2

#### ADDITIONAL REQUIREMENTS
A PLY package is required to run the program
(Https://github.com/dabeaz/ply.git)

python -m pip install --user ply

#### CALL
Attention! The [interpreter] program was downloaded from the website running the course
1.
python ./main.py <program_name> .imp <program_name> .ml
./interpreter <program_name> .ml

2. More convenient call (bash):
FILE = <program_name>
python ./main.py $ FILE.imp $ FILE.ml; ./interpreter $ FILE.ml


#### CONTENTS OF FILES
-- lexer.py - a list of tokens
-- yacc.py - parser
-- errors.py - error handling
-- mnemonics.py - declaration of the mnemonic list of the compiler; All classes implemented mnemonic with the specified result    string of the registration machine
-- symbolstable.py - variable support; It contains the functions of adding / removing variables to / from the list declared   
   variables, returning length or address, sending a flag 'readonly', returning errors
-- syntaxtree.py - generating registration machine code for a token tree; separation the parser output code to the appropriate 
   subroutines and returning the code registration machine
-- main.py - launching the project
