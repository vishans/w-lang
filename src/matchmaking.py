
from tokenize import Token
import re
import token_class as TC

validate = lambda token, pattern: re.search(pattern,token)


def matchAndMakeToken(token: str, *others) -> TC.Token:
    # clause
    if token == 'set:':
        return TC.Set(token,*others)

    if token == 'meta:':
        return TC.Meta(token,*others)

    if token == 'workout:':
        return TC.Workout(token,*others)

    # None type
    if validate(token, TC.Nothing.RegexPattern):
        return TC.Nothing(token, *others)

    # dot 
    if token == '.':
        return TC.Dot(token,*others)

    # assignment
    if validate(token,TC.Assignment.RegexPattern):
        lv, rv = token.split('=')
        rv = matchAndMakeToken(rv,*others)
        if rv == TC.UnknownToken:
            return TC.UnknownToken(token,*others)

        return TC.Assignment(token,lv,rv,*others) 

    # rep
    if validate(token,TC.Rep.RegexPattern):
        return TC.Rep(token,*others)

    # string, integer, float, boolean

    # string
    if validate(token, TC.String.RegexPattern):
        return TC.String(token, *others)

    # integer
    if validate(token, TC.Integer.RegexPattern):
        return TC.Integer(token, *others)

    # float
    if validate(token, TC.Float.RegexPattern):
        return TC.Float(token, *others)

    # boolean
    if validate(token, TC.Boolean.RegexPattern):
        return TC.Boolean(token, *others)

    # quantity
    # NaN
    if validate(token, TC.NaN.RegexPattern):
        return TC.NaN(token, *others)

    # percentage
    if validate(token, TC.Percentage.RegexPattern):
        return TC.Percentage(token, *others)

    # kilogram
    if validate(token, TC.Kilogram.RegexPattern):
        return TC.Kilogram(token, *others)

    #second
    if validate(token, TC.Second.RegexPattern):
        return TC.Second(token, *others)

    # minute
    if validate(token, TC.Minute.RegexPattern):
        return TC.Minute(token, *others)

    if validate(token, TC.MinuteSecond.RegexPattern):
        return TC.MinuteSecond(token, *others)

    if validate(token, TC.Date.RegexPattern):
        return TC.Date(token, *others)

    if validate(token, TC.Time.RegexPattern):
        return TC.Time(token, *others)

    if validate(token, TC.Variable.RegexPattern):
        return TC.Variable(token, *others)

    if validate(token, TC.HourMinute.RegexPattern):
        return TC.HourMinute(token, *others)

    

    






    return TC.UnknownToken(token,*others)




    
if __name__ == '__main__':

    print(type(matchAndMakeToken('13:12', 1,1)))

    from datetime import date, time , datetime,timedelta

    print(datetime(2010,1,2) + timedelta(2010,1,1))
    print(type(datetime.now()))
