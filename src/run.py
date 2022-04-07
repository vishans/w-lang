import sys
from parser_ import Parser
from tokenizer import Lexer
from interpreter import Interpreter


try:
    filePath = sys.argv[1]
except:
    print('A file path pointing to the workout script is required.')
    sys.exit(1)

lexer = Lexer(filePath)
lexer_result = lexer.tokenize2() # returns a list of tokens 
                                 # else returns an Error token which evaluates to False

if (lexer_result):
    
    parser = Parser(lexer_result)
    parser_result = parser.parse() # return a treeish dict
                                   # else returns an Error Token if something goes wrong

    if parser_result:

        interpreter = Interpreter(parser_result)
        interpreter_result = interpreter.interprete() 
        if not interpreter_result:
            print(interpreter_result)
   
    else:
        # print error of parser
        print(parser_result)
 
else:
    # print error of lexer
    print(lexer_result)
