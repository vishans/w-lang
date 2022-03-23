from regex_pattern import RegexPattern
from datetime import date, time, timedelta


class Token:
    def __init__(self,token, line, start) -> None:
        self.literal = token
        self.line = line
        self.start = start
        self.value = self.literal

    def getValue(self):
        return self.value

    def getLiteral(self):
        return self.literal

    def getAll(self):
        return self.literal,self.line,self.start

    def __eq__(self, __o: object) -> bool:
        return isinstance(self,__o)

    def __repr__(self) -> str:
        return f'Token <{self.literal}> at line {self.line} at position {self.start}'


class Rep(Token):
    RegexPattern = r'^\d+-\d+$'

    def __init__(self, token, line, start) -> None:
        super().__init__(token, line, start)

    def __repr__(self) -> str:
        return f'Rep <{self.literal}> at line {self.line} at position {self.start}'


class Assignment(Token):
    RegexPattern = r'^[^=]+=[^=]+$'

    def __init__(self, token,lv, rv, line, start) -> None:
        super().__init__(token, line, start)
        self.lv, self.rv = lv, rv

    def __repr__(self) -> str:
        return f'Assignment LV<{self.lv}>, RV<{self.rv}> at line {self.line} at position {self.start}'


class Nothing(Token):
    RegexPattern = r'^None$'
    def __init__(self, token, line, start) -> None:
        super().__init__(token, line, start)

    def __repr__(self) -> str:
        return f'Nothing Token at line {self.line} at position {self.start}'

class Variable(Token):
    RegexPattern = r'^[A-Za-z][A-Za-z\-]*[A-Za-z]$'  

    def __init__(self, token, line, start) -> None:
        super().__init__(token, line, start)
       

    def __repr__(self) -> str:
        return f'Variable <{self.literal}> at line {self.line} at position {self.start}'

class NaN(Token):
    RegexPattern = r'''^NaN$'''

    def __init__(self, token, line,start) -> None:
        super().__init__( token, line,start)
        

    def __repr__(self) -> str:
        return f'NaN at line {self.line} at position {self.start}'
    


class String(Token):
    RegexPattern = r'''^("[A-Za-z0-9 \.\-]*"|'[A-Za-z0-9 \.\-]*')$'''

    def __init__(self, token, line,start) -> None:
        super().__init__( token, line,start)
        self.value = self.literal[1:-1]

    def __repr__(self) -> str:
        return f'String <{self.literal}> at line {self.line} at position {self.start}'


class Integer(Token):
    RegexPattern = r'^(-?[1-9][0-9]*|0)$'

    def __init__(self, token, line, start) -> None:
        super().__init__(token, line, start)
        self.value = int(self.literal)

    def __repr__(self) -> str:
        return f'Integer <{self.literal}> at line {self.line} at position {self.start}'


class Float(Token):
    RegexPattern = r'^((-)?(0|([1-9][0-9]*))(\.[0-9]+)?)$'#r'^([+-]?([0-9]+([.][0-9]*)?|[.][0-9]+))$' #r'^(-?[1-9]?\.\d+|-?[1-9]\d+\.\d+|-?0\.\d*[1-9])$'

    def __init__(self, token, line, start) -> None:
        super().__init__(token, line, start)

    def __repr__(self) -> str:
        return f'Float <{self.literal}> at line {self.line} at position {self.start}'


class Boolean(Token):
    RegexPattern = r'^(true|false)$'

    def __init__(self, token, line, start) -> None:
        super().__init__(token, line, start)
        self.value = True if self.literal == 'true' else False

    def __repr__(self) -> str:
        return f'Boolean <{self.value}> at line {self.line} at position {self.start}'


# quantity

class Quantity(Token):
    def __init__(self,token, line,start) -> None:
        super().__init__( token, line,start)

    def __repr__(self) -> str:
        return f'Quantity <{self.literal}> at line {self.line} at position {self.start}'


class Percentage(Quantity):
    RegexPattern = r'^([1-9]?\d%|100%)$'

    def __init__(self, token, line, start) -> None:
        super().__init__(token, line, start)
        self.value = token[:-1]
       

    def __repr__(self) -> str:
        return f'Percentage <{self.literal}> at line {self.line} at position {self.start}'


class Kilogram(Quantity):
    RegexPattern = r'^([1-9]*\d|\.\d+|[1-9]\d*\.\d+|0\.\d+)kg$'
    
    def __init__(self, token, line, start) -> None:
        super().__init__(token, line, start)
        self.value = token[:-2]
        
    
    def __repr__(self) -> str:
        return f'Kilogram <{self.value}> at line {self.line} at position {self.start}'


class Second(Quantity):
    RegexPattern = r'^(([1-9][0-9]*s)|(0s)|(:[0-5][0-9]))$'

    def __init__(self, token, line, start) -> None:
        super().__init__(token, line, start)
        if ':' not in self.literal:
            self.value = int(token[:-1])
        else:
            self.value = int(token[1:])

    def getTimeDeltaObj(self):
        return timedelta(minutes=self.value)

    def getTimeObj(self):
        return time(minute=self.value)


    def __repr__(self) -> str:
        return f'Second <{self.value}> at line {self.line} at position {self.start}'


class Minute(Token):
    RegexPattern = r'^([1-9]\d*min|0min)$'

    def __init__(self, token, line, start) -> None:
        super().__init__(token, line, start)
        self.value = int(token[:-3])
        

    def getTimeDeltaObj(self):
        return timedelta(minutes=self.value)

    def getTimeObj(self):
        return time(minute=self.value)

    def __repr__(self) -> str:
        return f'Minute <{self.value}> at line {self.line} at position {self.start}'
    

class MinuteSecond(Token):
    RegexPattern = r'^((([1-9][0-9]*min)|(0min))([0-5][0-9]s)?)$'

    '''Accepted syntax:
    0min45s
    30min13s
   
    
    Not accepted:
    1) Starting with more than 1 zero
    2) The second part should strictly be 2-digit i.e 2min4s is wrong instead write 2min04s

    '''

    def __init__(self, token, line, start) -> None:
        super().__init__(token, line, start)

        if ':' in self.literal:
            self.minute, self.second = self.literal.split(':')
            print(self.literal.split(':'))

        else:
            index_min = self.literal.find('min')
            self.minute = 0 if not self.literal[:index_min] else self.literal[:index_min]
            self.second = self.literal[index_min+3:-1]
        
        self.minute, self.second = int(self.minute), int(self.second)

    def getTimeDeltaObj(self):
        return timedelta(minutes=self.minute,seconds=self.second)

    def getTimeObj(self):
        return time(minute=self.minute, second=self.second)

    def __repr__(self) -> str:
        return f'MinuteSecond <{self.minute, self.second}> at line {self.line} at position {self.start}'

class HourMinute(Token):
    RegexPattern = r'^((([1-9]\d*h)([0-5][0-9]min)?))$'

    '''Accepted syntax:
    0h45min
    30h13min
   
    
    Not accepted:
    1) Starting with more than 1 zero
    2) The second part should strictly be 2-digit i.e 2min4s is wrong instead write 2min04s

    '''

    def __init__(self, token, line, start) -> None:
        super().__init__(token, line, start)

       
        self.hour, self.minute = self.literal.split('h')
        
        if self.minute:
            self.minute = self.minute[:2]

        
        self.hour, self.minute = int(self.hour), int(self.minute)

    def getTimeDeltaObj(self):
        return timedelta(hours=self.hour,minutes=self.minute)

    def getTimeObj(self):
        return time(hour=self.hour, minute=self.minute)

    def __repr__(self) -> str:
        return f'HourMinute <{self.hour, self.minute}> at line {self.line} at position {self.start}'

# time
class Date(Token):
    RegexPattern = r'^(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/|-|\.)(?:0?[13-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})$'

    def __init__(self, token, line, start) -> None:
        super().__init__(token, line, start)

        if '-' in self.literal:
            sep = '-'
        elif '/' in self.literal:
            sep = '-'
        elif '.' in self.literal:
            sep = '-'

        

        self.d,self.m,self.y = [int(c) for c in self.literal.split(sep)]
        if self.y < 100:
            self.y+=2000
           
    def getDateObj(self):
        return date(self.y,self.m,self.d)
        

    
    def __repr__(self) -> str:
        return f'Date <{self.literal}> at line {self.line} at position {self.start} '


class Time(Token):
    RegexPattern = r'^(([0-1]?[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9])?)$'
    def __init__(self, token, line, start) -> None:
        super().__init__(token, line, start)
        split = self.literal.split(':')
        if len(split) == 3:
            self.h,self.min,self.s = [int(i) for i in split]
        else:
            self.h,self.min,self.s = [int(i) for i in split+[0]]

    def getTimeDeltaObj(self):
        return timedelta(hours=self.h,minutes=self.min,seconds=self.s)

    def getTimeObj(self):
        return time(hour=self.h,minute=self.min,second=self.s)

    def __repr__(self) -> str:
        return f'Time <{self.literal}> at line {self.line} at position {self.start} '





# errors

class Error(Token):
    def __init__(self,*args) -> None:
        super().__init__(*args)

    def __bool__(self):
        return False

    def __repr__(self) -> str:
        return f'Error({self.literal}) at line {self.line} at position {self.start}'


class UnknownToken(Error):
    def __init__(self, token, line, start) -> None:
        super().__init__(token, line, start)

    def __repr__(self) -> str:
        return f'''Unknown Token Error
            <{self.literal}> at line {self.line}'''

class IndentationError(Error):
    def __init__(self,token, line, start) -> None:
        super().__init__(token, line, start)

    def __repr__(self) -> str:
        return f'''Indentation Error
            <{self.literal}>  at line {self.line}'''


class ClauseError(Error):
    def __init__(self,token, line, start) -> None:
        super().__init__(token, line, start)

    def __repr__(self) -> str:
        return f'''Clause Error
            A clause was expected but <{self.literal}> was given at line {self.line}'''


class NestedClauseError(Error):
    def __init__(self,token, line, start) -> None:
        super().__init__(token, line, start)

    def __repr__(self) -> str:
        return f'''Nested Clause Error
            There is a clause <{self.literal}> inside another clause at line {self.line}'''


class StringorDotExpectedError(Error):
    def __init__(self,token, line, start) -> None:
        super().__init__(token, line, start)

    def __repr__(self) -> str:
        return f'''String or Dot Expected Error
            A line inside a clause should start with a string or a dot but <{self.literal}> was given at line {self.line}'''


class EmptyClauseError(Error):
    def __init__(self,token, line, start) -> None:
        super().__init__(token, line, start)

    def __repr__(self) -> str:
        return f'''Empty Clause Error
            A clause cannot be empty (line {self.line})'''

# parser error 

class DotNotAllowedError(Error):
    def __init__(self, token, line, start, clause) -> None:
        super().__init__(token, line, start)
        self.clause = clause

    def __repr__(self) -> str:
        return f'''Dot Not Allowed Error
            Dot is not allowed in {self.clause} on line {self.line}'''


class ReAssignmentError(Error):
    def __init__(self, token, line, start,with_='') -> None:
        super().__init__(token, line, start)
        self.with_ = with_

    def __repr__(self) -> str:
        return f'''Re-assignment Error
            f"You are trying to re-assign attibute <{self.literal}> with value <{self.with_}> on line {self.line}'''


class AttributeDoesNotExist(Error):
    def __init__(self, token, line, start, clause) -> None:
        super().__init__(token, line, start)
        self.clause = clause

    def __repr__(self) -> str:
        return f'''Attribute Does Not Exist
           Attribute <{self.literal}> does not exist in {self.clause} on line {self.line}'''

class NotABoolean(Error):
    def __init__(self, token, line, start) -> None:
        super().__init__(token, line, start)
       

    def __repr__(self) -> str:
        return f'''Not A Boolean
           Attribute <{self.literal}> is not a Boolean on line {self.line}'''


class NoAttributeAcceptThisValue(Error):
    def __init__(self, token, line, start) -> None:
        super().__init__(token, line, start)
       

    def __repr__(self) -> str:
        return f'''No Attribute Accept This Value
           No attribute accepts the value <{self.literal}> on line {self.line}'''


class DotNotAllowed(Error):
    # token to be used in lexer
    def __init__(self, token, line, start) -> None:
        super().__init__(token, line, start)
       

    def __repr__(self) -> str:
        return f'''Dot Not Allowed
           Illegal Dot on line {self.line} at position {self.start}'''


class ExerciseNotFound(Error):
    # token to be used in lexer
    def __init__(self, token, line, start) -> None:
        super().__init__(token, line, start)
       

    def __repr__(self) -> str:
        return f'''Exercise Not Found
           Exercise <{self.value}> on line {self.line} was not found'''


        


class Newline(Token):
    def __init__(self, token, line, start) -> None:
        super().__init__(token, line, start)


class Dot(Token):
    RegexPattern = r'^\.$'
    def __init__(self, token, line, start) -> None:
        super().__init__(token, line, start)

    def __repr__(self) -> str:
        return f'Dot at line {self.line} at position {self.start}'

# clause
class Clause(Token):
    RegexPattern = r'^(set:|meta:|workout:)$'# r'^[a-z]+:$'
    def __init__(self,*args) -> None:
        super().__init__(*args)


class Set(Clause):
    def __init__(self,token,line,start) -> None:
        super().__init__(token,line,start)

    def __repr__(self) -> str:
        return f'Set at line {self.line}'


class Workout(Clause):
    def __init__(self,token,line,start) -> None:
        super().__init__(token,line,start)

    def __repr__(self) -> str:
        return f'Workout at line {self.line}'


class Meta(Clause):
    def __init__(self,token,line,start) -> None:
        super().__init__(token,line,start)

    def __repr__(self) -> str:
        return f'Meta at line {self.line}'


# end token

class End(Token):
    def __init__(self, token, line, start) -> None:
        super().__init__(token, line, start)

    
class EndofClause(End):
    def __init__(self, token, line, start) -> None:
        super().__init__(token, line, start)

    def __repr__(self) -> str:
        return f'End of Clause at line {self.line}'

class EndofLine(End):
    def __init__(self, token, line, start) -> None:
        super().__init__(token, line, start)

    def __repr__(self) -> str:
        return f'End of Line at line {self.line}'


class EndofFile(End):
    def __init__(self, token, line, start) -> None:
        super().__init__(token, line, start)

    def __repr__(self) -> str:
        return f'End of File at line {self.line}'

        


