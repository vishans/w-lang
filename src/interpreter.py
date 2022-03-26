import json
import token_class as TC
import csv
class Interpreter:
    def __init__(self,tree) -> None:
        if tree:
            self.tree = tree
        else:
            print('Error')
            # return

        self.config = json.load(open(Parser.CONFIG, 'r'))
        self.outputDir = r'output/out.csv'
        self.csv = csv.writer(open(self.outputDir,'w'))

    def getPrint(self):
        return self.tree['meta']['print-output'].getValue()

    def getCSV(self):
        return self.tree['meta']['csv'].getValue()


    @staticmethod
    def printRow(*attributes, sep = ' '*4, columnWidth = 14, padding=' ',alignment = '<',offset=''):
        for element in attributes[:-1]:
            # formattingStr = '{:_^'+ str(columnWidth) +'s}'
            formattingStr = '{:'+str(padding)+alignment+ str(columnWidth) +'s}'

            print(offset + formattingStr.format(str(element)), end=sep)

        print(offset + formattingStr.format(str(attributes[-1])))
            

    def do_Meta(self):
        orderToPrint = self.config['interpreter']['order']['meta']

        # print attributes name row
        if self.getPrint():
            self.printRow(*orderToPrint,alignment='^')

        
        metaTree = self.tree['meta']
        tempPrintList = []
        for attribute in orderToPrint:
            if attribute in metaTree:
                tempPrintList.append(self.tree['meta'][attribute])

            else:
                print(f'attribute <{attribute}> not found in meta')
        
        if self.getPrint():
            self.printRow(*tempPrintList,alignment='^')

    def do_Workout(self):
        orderToPrint = self.config['interpreter']['order']['workout']

        # print attributes name row
        if self.getPrint():
            self.printRow(*orderToPrint,alignment='^')
        

        
        metaTree = self.tree['workout']
        tempPrintList = []
        for attribute in orderToPrint:
            if attribute in metaTree:
                tempPrintList.append(self.tree['workout'][attribute])

            else:
                print(f'attribute <{attribute}> not found in workout')
        
        if self.getPrint():
            self.printRow(*tempPrintList,alignment='^')

    def do_Sets(self):
        orderToPrint = self.config['interpreter']['order']['sets']
        
        # print attributes name row
        if self.getPrint():
            self.printRow(* (['wID','setID','exID','repID','CumRep']+orderToPrint),alignment='^')

        if self.getCSV():
            self.csv.writerow(['wID','setID','exID','repID','CumRep']+orderToPrint)



        workoutID = 1
        setID = 1
        exerciseID = 0
        repID = 1
        CummulativeRep = 1

        start = None
        end = None
        prevStart = None
        prevEnd = None

        prevExerciseName = None

        for set_ in self.tree['sets']:
            exerciseID = 0
            for line in set_:
                rep = line['rep']
                exerciseName = line['exercise-name']

                if str(exerciseName) != str(prevExerciseName):
                    # new exercise

                    repID = 1
                    exerciseID+=1
                    CummulativeRep = 1

                    if rep == TC.Rep:
                        start = rep.getStart()
                        end = rep.getEnd()
                        
                    else:
                        #Integer
                        start =  1
                        end = rep.getValue()

                        if end <= 0:
                            print('error 4')
                            return

                    if start != 1:
                        print('Error1')
                        return

                    prevEnd = end

                    tempPrintList = []
                    for attribute in orderToPrint:
                        tempPrintList.append(line[attribute])


                    for i in range(start, end+1):
                        if self.getPrint():
                            self.printRow(*([workoutID,setID,exerciseID,repID,CummulativeRep]+tempPrintList))

                        if self.getCSV():
                            self.csv.writerow([workoutID,setID,exerciseID,repID,CummulativeRep]+tempPrintList)

                        repID+=1
                        CummulativeRep+=1

                    

                else:
                    if rep == TC.Rep:
                        start = rep.getStart()
                        end = rep.getEnd()

                        if start == 1:
                            CummulativeRep = 1
                        
                        elif start == prevEnd+1:
                            pass

                        elif start == 0:
                            start = 1
                            exerciseID+=1
                            repID = 1
                            CummulativeRep = 1

                        else:
                            print('error2')




                    else:
                        #Integer
                        start =  prevEnd+1
                        end = prevEnd + rep.getValue()

                        if end <= 0:
                            print('error 5')
                            return

                    prevEnd = end

                    tempPrintList = []
                    for attribute in orderToPrint:
                        tempPrintList.append(line[attribute])


                    for i in range(start, end+1):
                        if self.getPrint():
                            self.printRow(*([workoutID,setID,exerciseID,repID,CummulativeRep]+tempPrintList))

                        if self.getCSV():
                            self.csv.writerow([workoutID,setID,exerciseID,repID,CummulativeRep]+tempPrintList)

                        repID+=1
                        CummulativeRep+=1

                prevExerciseName = exerciseName

            setID+=1

    def interprete(self):
        self.do_Meta()
        print()
        self.do_Workout()
        print()
        self.do_Sets()

                        
   

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
    i = Interpreter(p.tree)
    i.interprete()

    
else:
    print(r)
