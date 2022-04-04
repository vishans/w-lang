from copy import deepcopy
from matchmaking import matchAndMakeToken
import json
from pprint import pprint
import token_class as TC
from sys import exit

class Parser:
    CONFIG = r'config\config.json'

    def __init__(self, tokens = None) -> None:
        self.configFile = open(Parser.CONFIG, 'r')
        self.config = json.load(self.configFile)

        self.metaFile=open(self.config['paths']['meta'], 'r')
        self.workoutFile=open(self.config['paths']['workout'], 'r')
        self.setFile=open(self.config['paths']['set'], 'r')
        self.exerciceFile=open(self.config['paths']['exercises'], 'r')

        
        self.meta = json.load(self.metaFile)
        self.workout = json.load(self.workoutFile)
        self.set = json.load(self.setFile)
        self.exercises = json.load(self.exerciceFile)

        self.metaDTypeMap = self.makeDataTypeMap()
        self.workoutDTypeMap = self.makeDataTypeMap('workout')
        self.setDTypeMap = self.makeDataTypeMap('set')

        
        self.tokenStream = tokens
        self.tokenStreamIterator = self.getTokenIterator()

        # tree
        self.tree = {
            'meta':None,
            'workout':None,
            'sets':[]
        }
        self.tree['meta'] = self.getVirginMeta()
        self.tree['workout'] = self.getVirginWorkout()

       
        #counters
        self.metaCounter = 0
        self.setCounter = 0
        self.workoutCounter = 0


        self.strict = False

        # set warning cache
        self.setWarningCache = {}

    def __enter__(self):
        return self

    def __exit__(self):
        self.configFile.close()
        self.metaFile.close()
        self.workoutFile.close()
        self.setFile.close()
        self.exerciceFile.close()

    def createDictWithTokens(self, dict):
        for key in dict:
            pass


    # 'pour' means 'for' in french
    def makeDataTypeMap(self, pour='meta'):
        dataTypeMap = {}
        if pour == 'meta':
            clause = self.meta

        if pour == 'workout':
            clause = self.workout

        if pour == 'set':
            clause = self.set

        for key in clause:
            
            dt = clause[key]['dataType']
            if not isinstance(dt,list):
                if dt in dataTypeMap:
                    dataTypeMap[dt].append(key)
                else:
                    dataTypeMap[dt] = [key]

            else:
                for d in dt:
                    if d in dataTypeMap:
                        dataTypeMap[d].append(key)
                    else:
                        dataTypeMap[d] = [key]
        
        return dataTypeMap

    def removeFromDataTypeMap(self,var,dataTypeMap, pour='meta'):
        
        if pour == 'meta':
            lookup = self.meta

        if pour == 'workout':
            lookup = self.workout
        
        if pour == 'set':
            lookup = self.set
           
        dataTypeList = lookup[var]['dataType'] if isinstance(lookup[var]['dataType'],list) else [lookup[var]['dataType']]

        for dt in dataTypeList:
            if dt in dataTypeMap:
                if var in dataTypeMap[dt]:
                    dataTypeMap[dt].remove(var)
                    if not len(dataTypeMap[dt]):
                        del dataTypeMap[dt]

    def getFirstOccurenceOfVarFromDT(self, dt, dtMap):
        # does not perform presence check assume there's at leat 1 occurence

        var = dtMap[dt].pop(0) # pop first element in the list
        if not len(dtMap[dt]):
            del dtMap[dt]
        
        return var


          
    
    def getVirginMeta(self):
        meta = {}
        for key in self.meta:
            meta[key] = matchAndMakeToken(str(self.meta[key]['defaultValue']),-1,-1)

            listOfDT = (self.meta[key]['dataType']) if isinstance(self.meta[key]['dataType'],list) else [self.meta[key]['dataType']]
            listOfDT.extend(['Nothing'])
            # print(listOfDT)
            # input()
            if type(meta[key]).__name__ not in listOfDT:
                print(f'Warning: Attribute {key} does not accept type {type(meta[key]).__name__ }')
                print('Please check meta.json file.')
                print()

        return meta

    def getVirginWorkout(self):
        workout = {}
        for key in self.workout:
            workout[key] = matchAndMakeToken(str(self.workout[key]['defaultValue']),-1,-1)

            listOfDT = (self.workout[key]['dataType']) if isinstance(self.workout[key]['dataType'],list) else [self.workout[key]['dataType']]
            listOfDT.extend(['Nothing'])
            # print(listOfDT)
            # input()
            if type(workout[key]).__name__ not in listOfDT:
                print(f'Warning: Attribute {key} does not accept type {type(workout[key]).__name__ }')
                print('Please check meta.json file.')
                print()

        return workout

    def getVirginSet(self):
        set = {}
        for key in self.set:
            set[key] = matchAndMakeToken(str(self.set[key]['defaultValue']),-1,-1)
            listOfDT = (self.set[key]['dataType']) if isinstance(self.set[key]['dataType'],list) else [self.set[key]['dataType']]
            listOfDT.extend(['Nothing'])
            # print(listOfDT)
            # input()
            if type(set[key]).__name__ not in listOfDT and key not in self.setWarningCache:
                self.setWarningCache[key] = 69
                print(f'Warning: Attribute {key} does not accept type {type(set[key]).__name__ }')
                print('Check your exercises.json and/or set.json files.')

                print()

        return set

    def getTokenIterator(self):
        if not self.tokenStream:
            return

        for token in self.tokenStream:
            yield token

    def getNextToken(self):
        return next(self.tokenStreamIterator)

    def checkForBlankedAttribute(self, clause='meta'):
        headerPrinted = False
        for key in self.tree[clause]:
            if self.tree[clause][key] == TC.Nothing and key in self.config['interpreter']['order'][clause]:
                
                if clause == 'workout' and key in ['start-time','end-time','duration','date']:
                    continue

                if not headerPrinted:
                    print(f'The following attributes in {clause} are required:')
                    headerPrinted = True

                
                print('\t'+key)

    def checkForBlankAttributesInSet(self):
        for i, set_ in enumerate(self.tree['sets']):
           
            headerPrinted = False
            valid = True
            for j, exercise in enumerate(set_):
                exercisePrinted = False
                for  key in exercise:
                    token = exercise[key]
                    if token == TC.Nothing and key in self.config['interpreter']['order']['sets']:
                        valid = False
                        if not headerPrinted:
                            print(f'In set {i+1}, these attributes are required:')
                            headerPrinted = True

                        if not exercisePrinted:
                            print(f'\tIn exercise {j+1}')
                            exercisePrinted = True


                        print(f'\t\t{key}')

        
        return valid

        


    def parseMeta(self):
        
        dTypeMap = self.makeDataTypeMap()
        currentToken = self.getNextToken()
        metaTokenList = []
        while currentToken != TC.EndofClause:
            metaTokenList.append(currentToken)
            currentToken = self.getNextToken()

        # re-order the list so that Assignment Tokens are at the begining
        metaTokenList = sorted(metaTokenList, key = lambda token: -1 if token == TC.Assignment else 1)

      
        
        for currentToken in metaTokenList:
            if currentToken == TC.EndofLine:
                continue

            if currentToken == TC.Dot:
                return TC.DotNotAllowedError(*currentToken.getAll(),'meta')

            if currentToken == TC.Variable:
                var = currentToken.getLiteral()
               
                if var in self.meta:
                    if 'Boolean' in dTypeMap:
                        if var in dTypeMap['Boolean']:
                            self.tree['meta'][var] = TC.Boolean('true',currentToken.getLine(),currentToken.getStart())

                            self.removeFromDataTypeMap(var,dTypeMap)
                            continue
                        
                    if 'Boolean' in self.meta[var]['dataType']:      
                        return TC.ReAssignmentError(*currentToken.getAll(),'true')
                    else:
                        return TC.NotABoolean(*currentToken.getAll())
                else:
                    return TC.AttributeDoesNotExist(*currentToken.getAll(), 'meta')

                continue


            # print(currentToken)
            if currentToken != TC.Assignment:
                className = type(currentToken).__name__
                if className in dTypeMap:
                   
                    var = self.getFirstOccurenceOfVarFromDT(className, dTypeMap)
                    self.removeFromDataTypeMap(var,dTypeMap)
                    
                    self.tree['meta'][var] = currentToken
                else:
                    value = currentToken.getLiteral()
                    
                    if className in self.metaDTypeMap:
                        print(f'All attributes of type <{className}> have been assigned')
                        
                    return TC.NoAttributeAcceptThisValue(*currentToken.getLiteral())
            else:
                var, value = currentToken.lv , currentToken.rv
                className = type(value).__name__
                # check if var is present in dtype map
                if className in dTypeMap:
                    if var in dTypeMap[className]:
                        # if this is the case
                        self.tree['meta'][var] = value #value is actually a Token

                        # remove the var from dtype
                        self.removeFromDataTypeMap(var,dTypeMap)
                    else:
                        if var in self.meta:
                            return TC.ReAssignmentError(*currentToken.getAll(),value)
                        else:
                            return TC.AttributeDoesNotExist(*currentToken.getAll(),'meta')
                else:
                    # value = currentToken.getLiteral()
                    if className in self.metaDTypeMap:
                        print(f'All attributes of type <{className}> have been assigned')

                    return TC.NoAttributeAcceptThisValue(*currentToken.getAll())

    def parseWorkout(self):
        
        dTypeMap = self.makeDataTypeMap('workout')
        currentToken = self.getNextToken()
        workoutTokenList = []
        while currentToken != TC.EndofClause:
            workoutTokenList.append(currentToken)
            currentToken = self.getNextToken()

        # re-order the list so that Assignment Tokens are at the begining
        workoutTokenList = sorted(workoutTokenList, key = lambda token: -1 if token == TC.Assignment else 1)

    
        
        for currentToken in workoutTokenList:
            if currentToken == TC.EndofLine:
                continue

            if currentToken == TC.Dot:
                return TC.DotNotAllowedError(*currentToken.getAll(),'workout')

            if currentToken == TC.Variable:
                var = currentToken.getLiteral()
               
                if var in self.workout:
                    if 'Boolean' in dTypeMap:
                        if var in dTypeMap['Boolean']:
                            self.tree['workout'][var] = TC.Boolean('true',currentToken.getLine(),currentToken.getStart())

                            self.removeFromDataTypeMap(var,dTypeMap,'workout')
                            continue
                        
                    if 'Boolean' in self.workout[var]['dataType']:      
                        TC.ReAssignmentError(*currentToken.getAll(),'true')
                    else:
                        TC.NotABoolean(*currentToken.getAll())
                else:
                    TC.AttributeDoesNotExist(*currentToken.getAll(),'workout')

                continue

            # print(currentToken)
            if currentToken != TC.Assignment:
                className = type(currentToken).__name__
                if className in dTypeMap:
                   
                    var = self.getFirstOccurenceOfVarFromDT(className, dTypeMap)
                    self.removeFromDataTypeMap(var,dTypeMap,'workout')
                    value = currentToken
                    self.tree['workout'][var] = value
                else:
                    value = currentToken.getLiteral()
                    
                   
                    if className in self.workoutDTypeMap:
                        print(f'All attributes of type <{className}> have been assigned')

                    return TC.NoAttributeAcceptThisValue(*currentToken.getAll())
            else:
                var, value = currentToken.lv , currentToken.rv
                className = type(value).__name__
                # check if var is present in dtype map
                if className in dTypeMap:
                    if var in dTypeMap[className]:
                        # if this is the case
                        self.tree['workout'][var] = value 

                        # remove the var from dtype
                        self.removeFromDataTypeMap(var,dTypeMap, 'workout')
                    else:
                        if var in self.workout:
                            return TC.ReAssignmentError(*currentToken.getAll(),value)
                        else:
                            TC.AttributeDoesNotExist(*currentToken.getAll(), 'workout')
                else:
                        value = currentToken.getLiteral()

                        
                        if className in self.workoutDTypeMap:
                            print(f'All attributes of type <{className}> have been assigned')

                        return TC.NoAttributeAcceptThisValue(*currentToken.getAll())


    def parseSets(self):
        currentLine = self.getVirginSet()
        dTypeMap = self.makeDataTypeMap('set')
        currentToken = self.getNextToken()
        workoutTokenList = []
        prevLine = None
        while currentToken != TC.EndofClause:
            
            workoutTokenList.append(currentToken)
            currentToken = self.getNextToken()

        # re-order the list so that Assignment Tokens are at the begining
        # but the first element which could either a string or a dot stays there
        listOfExercisesInOneSet = []
        temp = []
        result = []
        for token in workoutTokenList:
            if token == TC.EndofClause:
                break

            if token != TC.EndofLine:
                temp.append(token)
            else:
                temp.append(token)
                firstElement, rest = temp[0],temp[1:]
                temp = sorted(rest, key = lambda token: -1 if token == TC.Assignment else 1)
                temp = [firstElement] + temp
                result.extend(temp)
               
                temp = []

        
        
        for currentToken in result:
            if currentToken == TC.EndofLine:
                prevLine = deepcopy(currentLine)
                listOfExercisesInOneSet.append(currentLine)
                currentLine = self.getVirginSet()
                dTypeMap = self.makeDataTypeMap('set')
                

                continue

            if currentToken == TC.Dot:
                if prevLine:
                    currentLine = deepcopy(prevLine)
                    self.removeFromDataTypeMap('exercise-name',dTypeMap,'set')
                    continue

                else:
                    return TC.DotNotAllowedError(*currentToken.getAll())

            

            if currentToken == TC.Variable:
                var = currentToken.getLiteral()
               
                if var in self.set:
                    if 'Boolean' in dTypeMap:
                        if var in dTypeMap['Boolean']:
                            currentLine[var] = TC.Boolean('true',currentToken.getLine(),currentToken.getStart())

                            self.removeFromDataTypeMap(var,dTypeMap,'set')
                            continue
                        
                    if 'Boolean' in self.set[var]['dataType']:      
                        return TC.ReAssignmentError(*currentToken.getAll(),'true')
                    else:
                        TC.NotABoolean(*currentToken.getAll())
                else:
                    return TC.AttributeDoesNotExist(*currentToken.getAll())

                continue

            # print(currentToken)
            if currentToken != TC.Assignment:
                className = type(currentToken).__name__
                if className in dTypeMap:
                   
                    var = self.getFirstOccurenceOfVarFromDT(className, dTypeMap)
                
                    if var in self.set:
                        value = currentToken

                        if var == 'exercise-name':
                            #check if execercise exists in exercise.json
                            currentLine[var] = value
                            if not self.updateSetDict(currentLine,value.getValue()) and self.strict:
                                return TC.ExerciseNotFound(*currentToken.getAll())
                        else:
                            currentLine[var] = value

                        self.removeFromDataTypeMap(var,dTypeMap,'set')
                   
                else:
                    
                    if className in self.setDTypeMap:
                        print(f'All attributes of type <{className}> have been assigned')

                    return TC.NoAttributeAcceptThisValue(*currentToken.getAll())
            else:
                
                var, value = currentToken.lv , currentToken.rv
                className = type(value).__name__
                # check if var is present in dtype map
                if className in dTypeMap:
                    if var in dTypeMap[className]:
                        # if this is the case
                        currentLine[var] = value 

                        # remove the var from dtype
                        self.removeFromDataTypeMap(var,dTypeMap, 'set')
                    else:
                        if var in self.set:
                            return TC.ReAssignmentError(*currentToken.getAll(),value)
                        else:
                            return TC.AttributeDoesNotExist(*currentToken.getAll())
                else:
                        value = currentToken.getLiteral()

                        
                        if className in self.settDTypeMap:
                            print(f'All attributes of type <{className}> have been assigned')

                        return TC.NoAttributeAcceptThisValue(*currentToken.getAll())

        self.tree['sets'].append(listOfExercisesInOneSet)
        


    def updateSetDict(self, setDict, exercise_name):
        try:
            execiseDict = self.exercises[exercise_name]
            for key in execiseDict:
                if key in setDict:
                    setDict[key] = matchAndMakeToken(str(execiseDict[key]),-1,-1)
                    listOfDT = (self.set[key]['dataType']) if isinstance(self.set[key]['dataType'],list) else [self.set[key]['dataType']]
                    listOfDT.extend(['Nothing'])
                    # print(listOfDT)
                    # input()

                    if type(setDict[key]).__name__ not in listOfDT:
                        print(f'Warning: Attribute <{key}> does not accept type {type(setDict[key]).__name__}.')
                        print('Check your exercises.json and/or set.json files.')
                        print()

                else:
                    print('Attribute does not exist in set')

            return True
        except:
            
            return False
            
            

        

    def parse(self):
        currentToken = self.getNextToken()
        while currentToken != TC.EndofFile:
            if currentToken == TC.Meta:
                self.metaCounter += 1
                if (r :=self.parseMeta()) == TC.Error:
                    return r

                currentToken = self.getNextToken()
                
                if currentToken == TC.Workout:
                    
                    self.workoutCounter += 1
                    if (r :=self.parseWorkout()) == TC.Error:
                        return r
                    currentToken = self.getNextToken()

                    # if currentToken == TC.Set:
                    while currentToken != TC.EndofFile:
                        if currentToken == TC.Meta or currentToken == TC.Workout:
                            print('Expected set clause')
                            return

                        self.setCounter += 1
                        if (r :=self.parseSets()) == TC.Error:
                            return r
                        currentToken = self.getNextToken()
                    # else:
                    #     print('Expected a set clause')
                    #     return

                else:
                    
                    print('Expected a workout clause')
                    return






            else:
                print('Expected a meta clause')
                return



           
            # currentToken = self.getNextToken()


        self.checkForBlankedAttribute()
        print()
        self.checkForBlankedAttribute('workout')
        print()
        self.checkForBlankAttributesInSet()
        print()
        
            

if __name__ == "__main__":

    from tokenizer import Lexer

    l = Lexer()
    if (r := l.tokenize2()):
        # print(r)
        p = Parser(r)
        print(f' ====> {p.parse()}')
        pprint(p.tree,sort_dicts=False)

    else:
        print(r)

    # if not TC.Error(-1,-1,-1):
    #     print('hello')
    #     print(TC.ClauseError(-1,-1,-1) == TC.Error)
    #     print(bool(TC.ClauseError(-1,-1,-1)))
    #     print(bool(TC.Token(1,1,1)))





