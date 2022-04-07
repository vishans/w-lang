import sys
from parser_ import Parser
from tokenizer import Lexer
from interpreter import Interpreter


try:
    filePath = sys.argv[1]
except:
    print('A file path pointing to the workout script is required.')
    sys.exit(1)


with Lexer(filePath) as lexer:
    lexer_result = lexer.tokenize2() # returns a list of tokens
                                     # else returns an Error token which evaluates to False


    if lexer_result:
        with  Parser(lexer_result) as parser:
            parser_result = parser.parse() # return a treeish dict
                                           # else returns an Error Token if something goes wrong


            if parser_result:
                with Interpreter(parser_result ) as interpreter:
                    interpreter_result = interpreter.interprete() 
                    if not interpreter_result:
                        print(interpreter_result)

            else:
                print(parser_result)

    else:
        print(lexer_result)




