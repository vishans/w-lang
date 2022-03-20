from copy import deepcopy

import json
from pprint import pprint

import token_class as TC

class Parser:
    CONFIG = r'config\config.json'

    def __init__(self, tokens = None) -> None:
        config = json.load(open(Parser.CONFIG, 'r'))
        self.meta = json.load(open(config['paths']['meta'], 'r'))
        self.workout = json.load(open(config['paths']['workout'], 'r'))
        self.set = json.load(open(config['paths']['set'], 'r'))

        self.metaDTypeMap = self.makeDataTypeMap()
        self.workoutDTypeMap = self.makeDataTypeMap('workout')

        
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


    # 'pour' means 'for' in french
    def makeDataTypeMap(self, pour='meta'):
        dataTypeMap = {}
        if pour == 'meta':
            clause = self.meta

        if pour == 'workout':
            clause = self.workout



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
            # pprint(lookup)

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
            meta[key] = self.meta[key]['defaultValue']

        return meta

    def getVirginWorkout(self):
        workout = {}
        for key in self.workout:
            workout[key] = self.workout[key]['defaultValue']

        return workout

    def getVirginSet(self):
        set = {}
        for key in self.set:
            set[key] = self.set[key]['defaultValue']

        return set

    def getTokenIterator(self):
        if not self.tokenStream:
            return

        for token in self.tokenStream:
            yield token

    def getNextToken(self):
        return next(self.tokenStreamIterator)

    def checkForBlankedAttribute(self, clause='meta'):
        print(f'The following attributes in {clause} are required:')
        for key in self.tree[clause]:
            if self.tree[clause][key] == None:
                print('\t'+key)

        


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
                print('Dot is not allowed inside meta clause')

            if currentToken == TC.Variable:
                var = currentToken.getLiteral()
               
                if var in self.meta:
                    if 'Boolean' in dTypeMap:
                        if var in dTypeMap['Boolean']:
                            self.tree['meta'][var] = True

                            self.removeFromDataTypeMap(var,dTypeMap)
                            continue
                        
                    if 'Boolean' in self.meta[var]['dataType']:      
                        print(f"You are trying to re-assign attibute <{var}>")
                    else:
                        print(f'Attribute <{var}> is not a Boolean')
                else:
                    print(f'Attribute {var} does not exist in meta')

                continue


            # print(currentToken)
            if currentToken != TC.Assignment:
                className = type(currentToken).__name__
                if className in dTypeMap:
                   
                    var = self.getFirstOccurenceOfVarFromDT(className, dTypeMap)
                    self.removeFromDataTypeMap(var,dTypeMap)
                    
                    self.tree['meta'][var] = currentToken.getValue()
                else:
                    value = currentToken.getLiteral()
                    
                    print(f'No attribute accepts this value {value}')
                    if className in self.metaDTypeMap:
                        print(f'All attributes of type <{className}> have been assigned')
            else:
                var, value = currentToken.lv , currentToken.rv
                className = type(value).__name__
                # check if var is present in dtype map
                if className in dTypeMap:
                    if var in dTypeMap[className]:
                        # if this is the case
                        self.tree['meta'][var] = value.getValue() #value is actually a Token

                        # remove the var from dtype
                        self.removeFromDataTypeMap(var,dTypeMap)
                    else:
                        if var in self.meta:
                            print(f"You're trying to re-assign the attribute <{var}> with value <{value}>.")
                        else:
                            print(f'the attribute <{var}> does not exist')
                else:
                    value = currentToken.getLiteral()
                    print(f'No attribute accepts this value {value}')
                    if className in self.metaDTypeMap:
                        print(f'All attributes of type <{className}> have been assigned')


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
                print('Dot is not allowed inside workout clause')

            if currentToken == TC.Variable:
                var = currentToken.getLiteral()
               
                if var in self.workout:
                    if 'Boolean' in dTypeMap:
                        if var in dTypeMap['Boolean']:
                            self.tree['workout'][var] = True

                            self.removeFromDataTypeMap(var,dTypeMap,'workout')
                            continue
                        
                    if 'Boolean' in self.workout[var]['dataType']:      
                        print(f"You are trying to re-assign attibute <{var}>")
                    else:
                        print(f'Attribute <{var}> is not a Boolean')
                else:
                    print(f'Attribute {var} does not exist in workout')

                continue

            # print(currentToken)
            if currentToken != TC.Assignment:
                className = type(currentToken).__name__
                if className in dTypeMap:
                   
                    var = self.getFirstOccurenceOfVarFromDT(className, dTypeMap)
                    self.removeFromDataTypeMap(var,dTypeMap,'workout')
                    value = currentToken.getValue()
                    self.tree['workout'][var] = value
                else:
                    value = currentToken.getLiteral()
                    
                    print(f'No attribute accepts this value {value}')
                    print(className)
                    if className in self.workoutDTypeMap:
                        print(f'All attributes of type <{className}> have been assigned')
            else:
                var, value = currentToken.lv , currentToken.rv
                className = type(value).__name__
                # check if var is present in dtype map
                if className in dTypeMap:
                    if var in dTypeMap[className]:
                        # if this is the case
                        self.tree['workout'][var] = value.getValue() #value is actually a Token, .value is the Token's attribute

                        # remove the var from dtype
                        self.removeFromDataTypeMap(var,dTypeMap, 'workout')
                    else:
                        if var in self.workout:
                            print(f"You're trying to re-assign the attribute <{var}>  with value <{value}>.")
                        else:
                            print(f'the attribute <{var}> does not exist')
                else:
                        value = currentToken.getLiteral()

                        print(f'No attribute accepts this value {value}')
                        if className in self.workoutDTypeMap:
                            print(f'All attributes of type <{className}> have been assigned')





            
            

        

    def parse(self):
        currentToken = self.getNextToken()
        while currentToken != TC.EndofFile:
            if currentToken == TC.Meta:
                self.metaCounter += 1
                self.parseMeta()


            if currentToken == TC.Workout:
                print('                             inside')
                self.workoutCounter += 1
                self.parseWorkout()


            currentToken = self.getNextToken()


        self.checkForBlankedAttribute()
        self.checkForBlankedAttribute('workout')
        
            



from tokenizer import Lexer

l = Lexer()
p = Parser(l.tokenize2())
p.parse()
pprint(p.tree,sort_dicts=False)





   



