from functools import partialmethod
import json
from tokenize import Token
import token_class as TC
import csv
import os
import shutil
from datetime import datetime
from string import Template
from parser_ import Parser
import token_class
import importlib
from pprint import pprint

from tokenizer import Lexer

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
    def __init__(self,tree,script) -> None:
        if tree:
            self.tree = tree
        else:
            print('Error')
            return
        self.script = script
        self.wID = self.getWID()
        self.tree['workout']['id'] = self.wID
        self.configFile = open(Parser.CONFIG, 'r')
        self.config = json.load(self.configFile)

        self.metaFile = open(self.config['paths']['meta'])
        self.meta = json.load(self.metaFile)

        self.setFile = open(self.config['paths']['set'])
        self.set = json.load(self.setFile)

        self.workoutFile = open(self.config['paths']['workout'])
        self.workout = json.load(self.workoutFile)
        if self.getCSV() or self.getScript():
            self.outputDir = self.createWorkoutFile(self.wID)# here output dir is the workout dir
            if self.getCSV():
                self.file = open(os.path.join(self.outputDir, 'data.csv'),'w',newline='')
                self.csv = csv.writer(self.file)

                self.workout_file = open(os.path.join(self.outputDir, 'workout.csv'),'w',newline='')
                self.csv_workout = csv.writer(self.workout_file)

        if self.getDB():
            
            self.DBFile = open(self.config['paths']['database'])
            self.DB = json.load(self.DBFile)
            import psycopg2
            try:
                self.conn = psycopg2.connect(host=self.DB['host'],
                                        database=self.DB['database'],
                                        user=self.DB['user'],
                                        password=self.DB['password'])
            except:
                print('Database does not exist')
                print(f"Creating Database {self.DB['database']}")
                self.conn = psycopg2.connect(host=self.DB['host'],
                                        database='postgres',
                                        user=self.DB['user'],
                                        password=self.DB['password'])
                
                self.cur = self.conn.cursor()
                self.conn.autocommit = True
                self.cur.execute(f"CREATE DATABASE {self.DB['database']}")
                self.conn.commit()
                self.conn.close()

                print('Database successfully created.')

                self.conn = psycopg2.connect(host=self.DB['host'],
                                            database=self.DB['database'],
                                            user=self.DB['user'],
                                            password=self.DB['password'])
                self.conn.autocommit = True

            self.cur = self.conn.cursor()
            self.cur.execute("select * from information_schema.tables where table_name=%s", (self.DB['workoutTable'],))
            workoutTableExists = bool(self.cur.rowcount)
            
            self.cur.execute("select * from information_schema.tables where table_name=%s", (self.DB['setTable'],))
            setTableExists = bool(self.cur.rowcount)

            if workoutTableExists:
                
                # self.workout = json.load(open(self.config['paths']['workout']))
                self.cur.execute(f"Select * FROM {self.DB['workoutTable']} LIMIT 0")
                colFromDB = set([desc[0] for desc in self.cur.description])
                colFromScript = set([item.replace('-','_') for item in self.workout])
                
                if not colFromScript == colFromDB:
                    removedColumns = colFromDB - colFromScript
                    if removedColumns:
                        print(f'The following column(s) has/have been removed from TABLE {self.DB["workoutTable"]}: ')
                        for item in removedColumns:
                            print('\t' + item)
                        print('''\nThe column(s) will not be dropped as it/they might still hold\ndata from previous workouts. If you want to remove it/them, you will need to do so manually.''')
                        print()
                    addedColumns = colFromScript - colFromDB

                    if addedColumns:
                        print(f'The following colums(s) has/have been added to TABLE {self.DB["workoutTable"]}: : ')
                        
                        partial = ''
                        for item in addedColumns:
                            print('\t' + item)
                            # dictToAlter[item] = self.workout[item]
                            typeInDict = self.workout[item]['dataType']
                            sqlType =  typeInDict if not isinstance(typeInDict, list) else typeInDict[0]

                            partial += 'ADD COLUMN ' + item + ' ' +  getattr(importlib.import_module('token_class'),sqlType).SQLDataType + ', '


                        print('The table will be alterd and the column(s) will be added.')

                        partial = partial[:-2]
                        full = f'''ALTER TABLE {self.DB['workoutTable']} 
                                {partial}'''

                        self.cur.execute(full)
                        self.conn.commit()
                        print('New columns committed.')
                        
                    
                
            else:
                print(f"Creating {self.DB['workoutTable']}")
                partial = self.getSQLTableDefinition('workout')
                fullDefinition = f'''CREATE TABLE {self.DB['workoutTable']}(\n{partial},\nPRIMARY KEY(id)
                                )'''
                # self.cur.execute(f"CREATE TABLE {self.DB['workoutTable']}")
                # self.conn.commit()
                # print(fullDefinition)
                self.cur.execute(fullDefinition)
                print(f"{self.DB['workoutTable']} successfully created.")
                self.conn.commit()
                

            if setTableExists:
                
                self.set = json.load(open(self.config['paths']['set']))
                self.cur.execute(f"Select * FROM {self.DB['setTable']} LIMIT 0")
                colFromDB = set([desc[0] for desc in self.cur.description])
                colFromScript = set([item.replace('-','_') for item in self.set])
                
                if not colFromScript == colFromDB:
                    removedColumns = colFromDB - colFromScript
                    removedColumns-= {'rep_id','cum_rep', 'w_id', 'set_id', 'ex_id' }
                    if removedColumns:
                        print(f'The following column(s) has/have been removed from TABLE {self.DB["setTable"]}: : ')
                        for item in removedColumns:
                            print('\t' + item)
                        print('''The column(s) will not be dropped as it/they might still hold\ndata from previous sets. If you want to remove it/them, you will need to do so manually.''')
                        print()
                    addedColumns = colFromScript - colFromDB

                    if addedColumns:
                        print(f'The following colums(s) has/have been added to TABLE {self.DB["setTable"]}: : ')
                        
                        partial = ''
                        for item in addedColumns:
                            print(item)
                            # dictToAlter[item] = self.workout[item]
                            typeInDict = self.set[item]['dataType']
                            sqlType =  typeInDict if not isinstance(typeInDict, list) else typeInDict[0]

                            partial += 'ADD COLUMN ' + item + ' ' +  getattr(importlib.import_module('token_class'),sqlType).SQLDataType + ', '


                        print('The table will be alterd and the column(s) will be added.')

                        partial = partial[:-2]
                        full = f'''ALTER TABLE {self.DB['setTable']} 
                                {partial}'''

                        self.cur.execute(full)
                        self.conn.commit()
                        print('New columns committed.')
                        
            else:
    
                print(f"Creating {self.DB['setTable']}")
                partial = self.getSQLTableDefinition('set')
                fullDefinition = f'''CREATE TABLE {self.DB['setTable']}(
                    "w_id" INT REFERENCES workout(id) ON DELETE CASCADE ,
                    "set_id" INT,
                    "ex_id" INT,
                    "rep_id" INT,
                    "cum_rep" INT,
                    {partial},\nPRIMARY KEY("self.workoutid", "set_id", "ex_id", "rep_id")
                                )'''
                # self.cur.execute(f"CREATE TABLE {self.DB['workoutTable']}")
                # self.conn.commit()
                # print(fullDefinition)
                self.cur.execute(fullDefinition)
                print(f"{self.DB['setTable']} successfully created.")
                self.conn.commit()
                input()


    def getSQLTableDefinition(self, pour):
        
        f = open(self.config['paths'][pour])
        d = json.load(f)
        partialDefinition = ''
        for attribute in d:
            typeInDict = d[attribute]['dataType']
            sqlType =  typeInDict if not isinstance(typeInDict, list) else typeInDict[0]
            partialDefinition += attribute.replace('-','_') + ' '
            partialDefinition += getattr(importlib.import_module('token_class'),sqlType).SQLDataType+ ',\n'
        
        return partialDefinition[:-2]



    


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_value, tb):
        if self.getCSV():
            self.workout_file.close()
            self.file.close()
            
        self.configFile.close()


    def getPrint(self):
        return self.tree['meta']['print-output'].getValue()

    def getCSV(self):
        return self.tree['meta']['csv'].getValue()

    def getOutputDir(self):
        return self.tree['meta']['output-dir'].getValue()

    def getDebug(self):
        return self.tree['meta']['debug'].getValue()

    def getExcludeUnit(self):
        return self.tree['meta']['exclude-unit'].getValue()

    def getScript(self):
        return self.tree['meta']['script'].getValue()

    def getDB(self):
        return True
        return self.tree['meta']['db'].getValue()

    def checkIfTablesExist(self):
        pass

    def getWID(self):
        
        wID = self.tree['workout']['id']
        
        # check if dir exists
        existed = True
        if not os.path.isdir(self.getOutputDir()):
            # create it 
            if self.getCSV():
                os.makedirs(self.getOutputDir())
            existed = False

        if wID == TC.NaN:
            
            if existed:
                if not self.getCSV():
                    return -1
                # check if there's smth in there
                ls =  os.listdir(self.getOutputDir())
                if ls:
                
                    # dir is not empty
                    # 
                    # sort content in descending order and pick the next id    
                    ls = list(map(int, ls))
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
        orderToPrint = [attribute for attribute in self.meta] #self.config['interpreter']['order']['meta']

        # print attributes name row
        if self.getPrint():
            self.printRow(*orderToPrint,alignment='^')

        
        metaTree = self.tree['meta']
        tempPrintList = []
        for attribute in orderToPrint:
            if attribute in metaTree:
                if self.getExcludeUnit():
                    if metaTree[attribute] == TC.Token:
                        metaTree[attribute].setExcludeUnit(True)
                tempPrintList.append(metaTree[attribute])

            else:
                print(f'attribute <{attribute}> not found in meta')
        
        if self.getPrint():
            self.printRow(*tempPrintList,alignment='^')

        return True

    def timeCalc(self):
        # time calculations
        start, end, duration = self.tree['workout']['start-time'], self.tree['workout']['end-time'], self.tree['workout']['duration']

        if all([start,end,duration]):
        
            if not (start == TC.Time and end == TC.Time):
                
                return TC.ExpectedTimeDataType(start.line,start.start,end.line,end.start)
               

            calc_duration = (end:= end.getDateTimeObj()) - (start := start.getDateTimeObj()) 

            if (duration := duration.getTimeDeltaObj()) != calc_duration:
                try:
                    return TC.DurationArithmeticError(*duration.getAll())
                except:
                    return TC.DurationArithmeticError(*self.tree['workout']['duration'].getAll())

                
            #else:

                # self.tree['workout']['start-time'] = start.getDateTimeObj().strftime("%H:%M:%S")
            self.tree['workout']['duration'] = strfdelta(duration,'%H:%M:%S')
                # self.tree['workout']['end-time'] = end.getDateTimeObj().strftime("%H:%M:%S")

        elif all([start,end]):
            if not (start == TC.Time and end == TC.Time):
               
                return TC.ExpectedTimeDataType(start.line,start.start,end.line,end.start)

                

            start =  start.getDateTimeObj()
            end =  end.getDateTimeObj()


            duration = end - start
            self.tree['workout']['duration'] = strfdelta(duration,'%H:%M:%S')


            

        
        
        elif all([start,duration]):
            if start == TC.HourMinute or start == TC.MinuteSecond or start == TC.Minute or start == TC.Second:
                start = datetime.now() - start.getTimeDeltaObj()
            else: 
                # tc.time
                start =  start.getDateTimeObj()



            end = start + duration.getTimeDeltaObj()
            # self.tree['workout']['start-time'] = start.strftime("%H:%M:%S")
            self.tree['workout']['duration'] = strfdelta(duration.getTimeDeltaObj(),'%H:%M:%S')
            # self.tree['workout']['end-time'] = end.strftime("%H:%M:%S")

        elif all([end,duration]):
            
            if end == TC.HourMinute or end == TC.MinuteSecond or end == TC.Minute or start == TC.Second:
                end = datetime.now() - end.getTimeDeltaObj()
            else: 
                # tc.time
                end =  end.getDateTimeObj()



            start = end - duration.getTimeDeltaObj()
            # self.tree['workout']['start-time'] = start.strftime("%H:%M:%S")
            self.tree['workout']['duration'] = strfdelta(duration.getTimeDeltaObj(),'%H:%M:%S')
            # self.tree['workout']['end-time'] = end.strftime("%H:%M:%S")

        else: 
            c = 0
            for t, n in zip([start, end, duration],['start-time','end-time','duration']):
                if t == TC.Nothing:
                    print(f'{n} is missing.')
                    c+=1

            print(f'Time Auto Calculation Failed.\nProvide at least {c-1} of the time attribute(s) above.')

            return TC.TimeAutoCalculationFailed()

        self.tree['workout']['start-time'] = start.strftime("%H:%M:%S")
        # self.tree['workout']['duration'] = strfdelta(duration.getTimeDeltaObj(),'%H:%M:%S')
        self.tree['workout']['end-time'] = end.strftime("%H:%M:%S")

        return True







    def do_Workout(self):

        timeCalc_result = self.timeCalc()
        if not timeCalc_result:
            return timeCalc_result

        self.updateDateInWorkout() 


        orderToPrint = [attribute for attribute in self.workout] #self.config['interpreter']['order']['workout']
        # print attributes name row
        if self.getPrint():
            self.printRow(*orderToPrint,alignment='^')

        if self.getCSV():
            self.csv_workout.writerow(orderToPrint)
        

        
        workoutTree = self.tree['workout']
        tempPrintList = []
        for attribute in orderToPrint:
            if attribute in workoutTree:
                if self.getExcludeUnit() or self.getDB():
                    if workoutTree[attribute] == TC.Token:
                        workoutTree[attribute].setExcludeUnit(True)
                tempPrintList.append(workoutTree[attribute])

            else:
                print(f'attribute <{attribute}> not found in workout')

        if self.getDB():
            print(tempPrintList)
            SQLValues = []
            for item in tempPrintList:
                if isinstance(item, str):
                    SQLValues.append(f"'{item}'")
                    continue
                    
                if isinstance(item, TC.Token):
                    SQLValues.append(item.getSQLString())
                    continue

                SQLValues.append(str(item))

            insert = f'''INSERT INTO {self.DB['workoutTable']}({','.join([item.replace('-','_') for item in self.workout])})
            VALUES({','.join([item for item in SQLValues])})'''
            print(insert)
            self.cur.execute(insert)
            self.conn.commit()
            print('success')
            input()
        
        if self.getPrint():
            self.printRow(*tempPrintList,alignment='^')

        if self.getCSV():
            self.csv_workout.writerow(tempPrintList)

        if self.getPDPrint():
            import pandas as pd
            print()
           
            df = pd.DataFrame({k:v for k,v in zip(orderToPrint,tempPrintList)}, index=[0])
            print('workout')
            print(df)
        return True

    def do_Sets(self):
        orderToPrint = [attribute for attribute in self.set] #self.config['interpreter']['order']['sets']
        
        # print attributes name row
        if self.getPrint():
            self.printRow(* (['wID','setID','exID','repID','CumRep']+orderToPrint),alignment='^')

        if self.getCSV():
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
                            
                            return TC.RepError(*rep.getAll(),'Rep cannot end with 0')

                    if start != 1:
                        
                        return TC.RepError(*rep.getAll(),'For a new exercise, Rep should start with a 1')

                        # add zero too and prevent that in strict mode (TO-DO)

                    prevEnd = end

                    tempPrintList = []
                    for attribute in orderToPrint:
                        if self.getExcludeUnit():
                            line[attribute].setExcludeUnit(True)
                        tempPrintList.append(line[attribute])
                    

                    for i in range(start, end+1):
                        if self.getPrint():
                            self.printRow(*([workoutID,setID,exerciseID,repID,CummulativeRep]+tempPrintList))

                        if self.getCSV():
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
                            return TC.RepError(*rep.getAll(),'Invalid rep. Either Rep starts with 0 or 1 or the end of the previous Rep')





                    else:
                        #Integer
                        start =  prevEnd+1
                        end = prevEnd + rep.getValue()

                        if end <= 0:
                            return TC.RepError(*rep.getAll(),'Rep cannot end with 0')
                            

                    prevEnd = end

                    tempPrintList = []
                    for attribute in orderToPrint:
                        if self.getExcludeUnit():
                            line[attribute].setExcludeUnit(True)
                        tempPrintList.append(line[attribute])


                    for i in range(start, end+1):
                        if self.getPrint():
                            self.printRow(*([workoutID,setID,exerciseID,repID,CummulativeRep]+tempPrintList))

                        if self.getCSV():
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

        if self.getScript():
            with open(os.path.join(self.outputDir, 'script.wo'), 'w') as script:
                script.writelines(self.script)


        return True

    def interprete(self):
        if self.getDebug():
           
            pprint(self.tree, sort_dicts=False)
        
        if not (m := self.do_Meta()):
            return m
        
        
        if not (w := self.do_Workout()):
            return w

        
        if not (s := self.do_Sets()):
            return s

        if self.getCSV():
            self.file.close()
            self.workout_file.close()
            self.configFile.close()

        return True

        

                        
if __name__ == '__main__':  
    
    l = Lexer(r'test.wo').tokenize2()
    
    p = Parser(**l).parse()
   
    i = Interpreter(**p)