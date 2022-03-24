import json
class Interpreter:
    def __init__(self,tree) -> None:
        if tree:
            self.tree = tree
        else:
            print('Error')
            # return

        self.config = json.load(open(Parser.CONFIG, 'r'))

    @staticmethod
    def printRow(*attributes, sep = ' '*2, columnWidth = 8, padding=' ',alignment = '<'):
        for element in attributes[:-1]:
            # formattingStr = '{:_^'+ str(columnWidth) +'s}'
            formattingStr = '{:'+str(padding)+alignment+ str(columnWidth) +'s}'

            print(formattingStr.format(str(element)), end=sep)

        print(formattingStr.format(str(attributes[-1])))
            

    def do_Meta(self):
        orderToPrint = self.config['interpreter']['order']['meta']

        # print attributes name row
        self.printRow(*orderToPrint,alignment='^')

        
        metaTree = self.tree['meta']
        tempPrintList = []
        for attribute in orderToPrint:
            if attribute in metaTree:
                tempPrintList.append(self.tree['meta'][attribute])

            else:
                print(f'attribute <{attribute}> not found in meta')

        self.printRow(*tempPrintList,alignment='^')

        

                


from parser_ import Parser
from tokenizer import Lexer
from pprint import pprint

# Interpreter.printRow(*list('abcedf'))

l = Lexer()
if (r := l.tokenize2()):
    # print(r)
    p = Parser(r)
    print(f' ====> {p.parse()}')
    # pprint(p.tree,sort_dicts=False)
    Interpreter(p.tree).do_Meta()

else:
    print(r)
