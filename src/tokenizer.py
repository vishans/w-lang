import re
from regex_pattern import RegexPattern
import token_class as TC
from pprint import pprint
from matchmaking import matchAndMakeToken

validate = lambda token, pattern: re.search(pattern,token)

class Lexer:
    '''Responsible for lexical analysis'''

    def __init__(self) -> None:
        self.filePath = 'test.txt'

        # if needed adds an newline at the end of the file
        # the lexer needs it
        # else the line number information will be all messed up near the end
        with open(self.filePath,'rb+') as f:
            f.seek(-1,2)
            lastchar = f.read(1)
            if lastchar != b'\n':
                f.write(b'\n')

        #file stream
        self.fileStream = open(self.filePath, 'r')

        #tokenization variables
        self.nextChar = self.__getNextChar()

        self.initialIndent = 0
        self.lineCounter = 1
        self.characterPointer = 1
        self.tokens = []

        self.lineStart = False

        

    
        


    def __getNextChar(self) -> str:

        return self.fileStream.read(1)

    
    def getFirstToken(self):
        self.initialIndent = 0
        tempIndentCount = 0 #temporary indentation counter
        firstToken = ''
        # tokenStartPointer = 0

        self.nextChar = self.__getNextChar()
        while 1:
            while self.nextChar == ' ':
                tempIndentCount+=1
                self.characterPointer+=1
                self.nextChar = self.__getNextChar()
                


            if self.nextChar == '':
                #end of file

                break


            if self.nextChar ==  '\n':
                self.lineCounter+=1

                tempIndentCount = 0
                self.characterPointer = 1

                self.nextChar = self.__getNextChar()
                self.lineStart = True

            
            else:

                tokenStartPointer = self.characterPointer
                while self.nextChar not in [' ', '\n']:
                    firstToken+=self.nextChar
                    self.characterPointer+=1

                    self.nextChar = self.__getNextChar()


                self.initialIndent = tokenStartPointer-1 # tempIndentCount
                break


        print(self.initialIndent)
        print(f'token: {firstToken}')
        print(f'line: {self.lineCounter}')
        print(f'start: {tokenStartPointer}')


    def getNextToken(self) -> str:
        
        token = ''

        while 1:
           
            while self.nextChar == ' ':
                
                self.characterPointer+=1
                self.nextChar = self.__getNextChar()
                


            if self.nextChar == '':
                #end of file
                tokenStartPointer = self.characterPointer
                return 'eof',self.lineCounter, tokenStartPointer

            if self.nextChar ==  '\n':
                tempLineCounter = self.lineCounter
                self.lineCounter+=1 
                self.characterPointer = 1
                tokenStartPointer = self.characterPointer

                self.nextChar = self.__getNextChar()
                
                return 'newline',tempLineCounter, tokenStartPointer


            if self.nextChar in ['"',"'"]:  #special case for string

                tokenStartPointer = self.characterPointer
                while 1:
                   
                    token+=self.nextChar
                    self.characterPointer+=1

                    self.nextChar = self.__getNextChar()

                    if self.nextChar in ['"', '\n', '',"'"]:
                        break

                # loop stops at " but the quote needs to be included in the token
                # so these 3 instructions below are executed once more to include the "
                token+=self.nextChar
                self.characterPointer+=1
                self.nextChar = self.__getNextChar()

            

               
                return token, self.lineCounter, tokenStartPointer

                

            
            else:

                tokenStartPointer = self.characterPointer
                sentinel = [' ', '\n', '']
                while self.nextChar not in sentinel:
                    token+=self.nextChar
                    self.characterPointer+=1

                    self.nextChar = self.__getNextChar()

                    # special case for string assignment
                    if self.nextChar in ['"',"'"]:
                        token+=self.nextChar
                        self.characterPointer+=1

                        self.nextChar = self.__getNextChar()

                        while self.nextChar not in ['"','',"'",'\n']:
                            token+=self.nextChar
                            self.characterPointer+=1

                            self.nextChar = self.__getNextChar()

                        token+=self.nextChar
                        self.characterPointer+=1

                        self.nextChar = self.__getNextChar()
                        break


                
                
                return token, self.lineCounter, tokenStartPointer


    def getMasterIndent(self) -> int:
        # return 0
        token, line, start = self.getNextToken()
        while token in ['newline']:
            #skip all the newlines 
            token, line, start = self.getNextToken()

        self.fileStream.close()
        self.fileStream = open(self.filePath,'r')
        self.nextChar = self.__getNextChar()
       
        self.lineCounter = 1
        self.characterPointer = 1
       
        return start  - 1

                


    def tokenize2(self): #-> 'list of Token Objest or an Error Objest':
        masterrIndent = self.getMasterIndent()
        clause = False
        tokens = []
        currentClause = None
        prevToken = None
        #first token


        token, line, start = self.getNextToken()
        
        
        while token in ['newline']:
            #skip all the newlines 
            token, line, start = self.getNextToken()
            

        while not self.isEOF():
            
            # get the clause token

            if start -1 < masterrIndent:
                print(token,line,start)
                return TC.IndentationError(token,line,start)
                
            currentClause = token
            
            if not isinstance(returnedObject := matchAndMakeToken(token, line, start), TC.Error):
                tokens.append(returnedObject)
            else:
                return returnedObject
            
            if token != 'newline':
                    prevToken = token, line, start
            

            if validate(token, TC.Clause.RegexPattern):
                clause = True
            else:
               
                return TC.ClauseError(token, line , start)

   
            
            # get the first token (on the first line) of the clause

            token, line, start = self.getNextToken()
            
            while token in ['newline']:
                
                #skip all the newlines 
                token, line, start = self.getNextToken()
                

            if start-1 == masterrIndent:
              
                return TC.EmptyClauseError(*prevToken)

            if validate(token, TC.Clause.RegexPattern):
              
                return TC.NestedClauseError(token, line, start)

            if not validate(token,TC.String.RegexPattern) and token != '.' and currentClause == 'set:':
               
                return TC.StringorDotExpectedError(token,line,start)

            
            if not isinstance(returnedObject := matchAndMakeToken(token, line, start), TC.Error):
                tokens.append(returnedObject)
            else:
                return returnedObject

            if token != 'newline':
                    prevToken = token, line, start

            clauseIndentation = start - 1

            if clauseIndentation <= masterrIndent:
                
                return TC.IndentationError(token,line,start)
                

            # get the rest of the first line ici

            token, line, start = self.getNextToken()
            
            while token not in ['newline', 'eof']:
                if not isinstance(returnedObject := matchAndMakeToken(token, line, start), TC.Error):
                    if token == '.':
                            return TC.DotNotAllowed(token,line, start)
                    tokens.append(returnedObject)
                else:
                    return returnedObject

                if token != 'newline':
                    prevToken = token, line, start
                token, line, start = self.getNextToken()
                





            while token in ['newline']:
                #skip all the newlines 
                token, line, start = self.getNextToken()
                

            if token == 'eof':
               
                if clause:
                    tokens.append(TC.EndofLine(token,line,start))
                    tokens.append(TC.EndofClause(token,line,start))


                tokens.append(TC.EndofFile(token,line,start))
                return tokens

            
            tokens.append(TC.EndofLine(*prevToken))
            
            if start -1 == masterrIndent:
                # tokens.append(TC.EndofLine(*prevToken))
                tokens.append(TC.EndofClause(token,line,start))
                
                
                clause = False # break

            

            elif start - 1 == clauseIndentation:
                clause = True

            else:
              
                return TC.IndentationError(token,line,start)

            


            # get the rest of the lines if any

            while clause:
               

                if start-1 != clauseIndentation:
                    # print(token,line,start)
                    return TC.ClauseError(token,line,start)
                    return TC.IndentationError(token,line,start)
                    
                    
                
                if start -1 < masterrIndent:
                   
                    return TC.IndentationError(token,line,start)
                    

                if validate(token, TC.Clause.RegexPattern):
                    
                    return TC.NestedClauseError(token, line, start)
                

                if not validate(token,TC.String.RegexPattern) and token != '.' and currentClause == 'set:':
                   
                    return TC.StringorDotExpectedError(token,line,start)

    
               

                

                if not isinstance(returnedObject := matchAndMakeToken(token, line, start), TC.Error):
                   
                    tokens.append(returnedObject)
                else:
                    return returnedObject

                if token != 'newline':
                    prevToken = token, line, start
                
                # get the rest of the  line if any

                token, line, start = self.getNextToken()
                
                while token not in ['newline', 'eof']:

                    if not isinstance(returnedObject := matchAndMakeToken(token, line, start), TC.Error):
                        if token == '.':
                            return TC.DotNotAllowed(token,line, start)
                        tokens.append(returnedObject)
                    else:
                        return returnedObject

                    prevToken = token, line, start
                    token, line, start = self.getNextToken()
                    


                tokens.append(TC.EndofLine(token,line,start))




                while token in ['newline']:
                    #skip all the newlines 
                    token, line, start = self.getNextToken()
                  

                if token == 'eof':
                    if clause:
                        tokens.append(TC.EndofClause(*prevToken))

                    tokens.append(TC.EndofFile(token,line,start))
                    
                    return tokens

                if start -1 == masterrIndent:
                   
                    tokens.append(TC.EndofClause(*prevToken))

                    if validate(token, TC.Clause.RegexPattern):
                        clause = False # break

                

                elif start - 1 == clauseIndentation:
                    clause = True

                else:
                    
                    return TC.IndentationError(token,line,start)
                    

        
        



    def tokenize(self):

        return self.getMasterIndent()

        # clause = False
        # tokens = []

        # token, line, start = self.getNextToken()
        # while token in ['newline']:
        #     #skip all the newlines 
        #     token, line, start = self.getNextToken()


        # if ':' in token:
        #     clause = True
        #     # get the clause start token e.g set:
        #     tokens.append(token)







                



        
        


    def makeToken(self):
        pass


    def isEOF(self):
        return self.nextChar == ''


        
if __name__ == '__main__':


    t = Lexer()

    # while not t.isEOF():
    
    #     print(t.getNextToken())

    # print(t.getNextToken())
    
    l = t.tokenize2()
    pprint(l)
    # for i in range(3):
    #     print()

    # pprint(sorted(l,key=f))








    

            