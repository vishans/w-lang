import json
import token_class as TC
import csv
import os
import shutil
from datetime import date, time, datetime
from string import Template

class DeltaTemplate(Template):
    delimiter = "%"

def strfdelta(tdelta, fmt):
    d = {"D": tdelta.days}
    hours, rem = divmod(tdelta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    d["H"] = '{:02d}'.format(hours)
    d["M"] = '{:02d}'.format(minutes)
    d["S"] = '{:02d}'.format(seconds)
    t = DeltaTemplate(fmt)
    return t.substitute(**d)




class Interpreter:
    def __init__(self,tree) -> None:
        if tree:
            self.tree = tree
        else:
            print('Error')
            return

        self.wID = self.getWID()
        self.tree['workout']['id'] = self.wID
        self.configFile = open(Parser.CONFIG, 'r')
        self.config = json.load(self.configFile)
        if self.getSave():
            self.outputDir = self.createWorkoutFile(self.wID)# here output dir is the workout dir
            self.file = open(os.path.join(self.outputDir, 'data.csv'),'w',newline='')
            self.csv = csv.writer(self.file)

            self.workout_file = open(os.path.join(self.outputDir, 'workout.csv'),'w',newline='')
            self.csv_workout = csv.writer(self.workout_file)

    def __enter__(self):
        return self


    def __exit__(self):
        self.workout_file.close()
        self.file.close()
        self.configFile.close()


    def getPrint(self):
        return self.tree['meta']['print-output'].getValue()

    def getSave(self):
        return self.tree['meta']['save'].getValue()

    def getOutputDir(self):
        return self.tree['meta']['output-dir'].getValue()


    def getWID(self):
        
        wID = self.tree['workout']['id']
        # check if dir exists
        existed = True
        if not os.path.isdir(self.getOutputDir()):
            # create it 
            if self.getSave():
                os.makedirs(self.getOutputDir())
            existed = False

        if wID == TC.NaN:
            print('in')
            if existed:
                # check if there's smth in there
                ls =  os.listdir(self.getOutputDir())
                if ls:
                
                    # dir is not empty
                    # 
                    # sort content in descending order and pick the next id    
                   
                    newID = int(sorted(ls)[-1]) + 1
                
                else:
                    newID = 1
            else:
                newID = 1
        
        else: 
            newID = wID

                
        return newID

    def getPDPrint(self):
        
        return self.tree['meta']['pd-print'].getValue()

    def getDate(self):
        return self.tree['workout']['date']

    def updateDateInWorkout(self):
        if self.getDate():
            self.tree['workout']['date'] = self.getDate().getDateTimeObj()

        else:
            self.tree['workout']['date'] = datetime.today()

        #update day
        self.tree['workout']['day'] = self.tree['workout']['date'].strftime("%A")
        self.tree['workout']['date'] = self.tree['workout']['date'].strftime("%d-%m-%y")

        

    def createWorkoutFile(self, id):
        # print(os.path.join( self.getOutputDir() ,str(id)))
        if  (os.path.isdir(p := os.path.join( self.getOutputDir() ,str(id)))):
            print(f'Warning. The workout folder with ID {id} already exists.\nIt will be overwritten.')
            shutil.rmtree(p)


        # create the folder
        
        os.mkdir(p)
       
        return p

        


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

    def timeCalc(self):
        # time calculations
        start, end, duration = self.tree['workout']['start-time'], self.tree['workout']['end-time'], self.tree['workout']['duration']
       
        if all([start,end,duration]):

            if not (start == TC.Time and end == TC.Time):
                print('Error11')

            calc_duration = end.getDateTimeObj() - start.getDateTimeObj() 

            if duration.getTimeDeltaObj() != calc_duration:
                print('Error10')
                return
            #else:

                # self.tree['workout']['start-time'] = start.getDateTimeObj().strftime("%H:%M:%S")
                # self.tree['workout']['duration'] = strfdelta(duration.getTimeDeltaObj(),'%H:%M:%S')
                # self.tree['workout']['end-time'] = end.getDateTimeObj().strftime("%H:%M:%S")

        elif all([start,duration]):
            
            if start == TC.HourMinute or start == TC.MinuteSecond or start == TC.Minute or TC.Second:
                start = datetime.now() - start.getTimeDeltaObj()
            else: 
                # tc.time
                start =  start.getDateTimeObj()



            end = start + duration.getTimeDeltaObj()
            # self.tree['workout']['start-time'] = start.strftime("%H:%M:%S")
            # self.tree['workout']['duration'] = strfdelta(duration.getTimeDeltaObj(),'%H:%M:%S')
            # self.tree['workout']['end-time'] = end.strftime("%H:%M:%S")

        elif all([end,duration]):
            
            if end == TC.HourMinute or end == TC.MinuteSecond or end == TC.Minute or TC.Second:
                end = datetime.now() - end.getTimeDeltaObj()
            else: 
                # tc.time
                end =  end.getDateTimeObj()



            start = end - duration.getTimeDeltaObj()
            # self.tree['workout']['start-time'] = start.strftime("%H:%M:%S")
            # self.tree['workout']['duration'] = strfdelta(duration.getTimeDeltaObj(),'%H:%M:%S')
            # self.tree['workout']['end-time'] = end.strftime("%H:%M:%S")

        else: 
            c = 0
            for t, n in zip([start, end, duration],['start-time','end-time','duration']):
                if t == TC.Nothing:
                    print(f'{n} is missing.')
                    c+=1

            print(f'Time Auto Calculation Failed.\nProvide at least {c-1} of the time attribute(s) above.')

            return

        self.tree['workout']['start-time'] = start.strftime("%H:%M:%S")
        self.tree['workout']['duration'] = strfdelta(duration.getTimeDeltaObj(),'%H:%M:%S')
        self.tree['workout']['end-time'] = end.strftime("%H:%M:%S")







    def do_Workout(self):

        self.timeCalc()

        self.updateDateInWorkout()


        orderToPrint = self.config['interpreter']['order']['workout']
        # print attributes name row
        if self.getPrint():
            self.printRow(*orderToPrint,alignment='^')

        if self.getSave():
            self.csv_workout.writerow(orderToPrint)
        

        
        metaTree = self.tree['workout']
        tempPrintList = []
        for attribute in orderToPrint:
            if attribute in metaTree:
                tempPrintList.append(self.tree['workout'][attribute])

            else:
                print(f'attribute <{attribute}> not found in workout')
        
        if self.getPrint():
            self.printRow(*tempPrintList,alignment='^')

        if self.getSave():
            self.csv_workout.writerow(tempPrintList)

        if self.getPDPrint():
            import pandas as pd
            print()
           
            df = pd.DataFrame({k:v for k,v in zip(orderToPrint,tempPrintList)}, index=[0])
            print('workout')
            print(df)

    def do_Sets(self):
        orderToPrint = self.config['interpreter']['order']['sets']
        
        # print attributes name row
        if self.getPrint():
            self.printRow(* (['wID','setID','exID','repID','CumRep']+orderToPrint),alignment='^')

        if self.getSave():
            self.csv.writerow(['wID','setID','exID','repID','CumRep']+orderToPrint)

        if self.getPDPrint():
            setsDict = {}
            for k in ['wID','setID','exID','repID','CumRep']+orderToPrint:
                setsDict[k] = []



        workoutID = self.wID
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

                        if self.getSave():
                            self.csv.writerow([workoutID,setID,exerciseID,repID,CummulativeRep]+tempPrintList)

                        if self.getPDPrint():
                            for k, v in zip(['wID','setID','exID','repID','CumRep']+orderToPrint,[workoutID,setID,exerciseID,repID,CummulativeRep]+tempPrintList):
                                setsDict[k].append(v)


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

                        if self.getSave():
                            self.csv.writerow([workoutID,setID,exerciseID,repID,CummulativeRep]+tempPrintList)

                        if self.getPDPrint():
                            for k, v in zip(['wID','setID','exID','repID','CumRep']+orderToPrint,[workoutID,setID,exerciseID,repID,CummulativeRep]+tempPrintList):
                                setsDict[k].append(v)

                        repID+=1
                        CummulativeRep+=1

                prevExerciseName = exerciseName

            setID+=1
        
        if self.getPDPrint():
            import pandas as pd
            print('sets')
            print(pd.DataFrame(setsDict))
            print()

    def interprete(self):
        self.do_Meta()
        print()
        self.do_Workout()
        print()
        self.do_Sets()

        if self.getSave():
            self.file.close()

        

                        
   

from parser_ import Parser
from tokenizer import Lexer
from pprint import pprint

# Interpreter.printRow(*list('abcedf'))

l = Lexer()
if (r := l.tokenize2()):
    # print(r)
    p = Parser(r)
    print(f' ====> {p.parse()}')
    pprint(p.tree,sort_dicts=False)
    i = Interpreter(p.tree)
    i.interprete()
    # import pandas as pd
    # df = pd.DataFrame(i.tree['workout'], index=[0])
    # print(df)
    print('done')
    


    
else:
    print(r)
