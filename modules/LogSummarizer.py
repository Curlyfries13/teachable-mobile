import re
import csv
import os
import sys
import datetime

symbolTranslate = {'moveDistance':'Move Distance       ', 'turnAngle':'Turn Angle          ', 'plotPoint':'Plot Point          ', 'Refresh':'Refresh             ', 'correctness feedback':'Correctness Feedback', 'prompt':'Prompt              ', 'checked emotions':'Checked Emotions    ', 'reset':'Reset               ', 'replay':'Replay              ', 'attribution':'Attribution         ','Deleted step from list':'Delete Step         '}

textFile = []

timeStampPattern = re.compile(r'(?P<month>[0-9]{1,2})/(?P<day>[0-9]{1,2})/(?P<year>[0-9]{4}) - (?P<hour>[0-9]{1,2}):(?P<minute>[0-9]{1,2}):(?P<second>[0-9]{1,2})')

directory = sys.argv[1]

os.chdir(directory)
promptLoop = False
correct = ' '
lastTimeStamp = None
moveSymbol = '  '
problem = 540

for log in os.listdir():
    with open(log, 'r') as logFile:
        logReader = csv.reader(logFile)

        for line, row in enumerate(logReader):
            if len(row) == 11:
                correct = ' '
                move = row[1]
                if(row[7] != problem and row[7] != 'undefined' and row[7] != ''):
                    textFile += '\n'
                if(row[7] == 'undefined'):
                    pass
                else:
                    problem = row[7]
                condition = row[10]
                if move != 'prompt':
                    timeStampMatch = timeStampPattern.search(row[0])
                    timeStamp = datetime.datetime(year=int(timeStampMatch.group('year')), month=int(timeStampMatch.group('month')), day=int(timeStampMatch.group('day')), hour=int(timeStampMatch.group('hour')), minute=int(timeStampMatch.group('minute')),  second = int(timeStampMatch.group('second')))

                if lastTimeStamp == None or move == 'prompt':
                    lastTimeStamp = timeStamp

                if move in symbolTranslate:
                    moveSymbol = symbolTranslate[move]
                else:
                    moveSymbol = '  '

                diff = str(timeStamp - lastTimeStamp)
                # Prompts appear to have bad timestamps, we'll try to avoid this
                if move == 'prompt':
                    promptLoop = True
                    store = ' '.join([correct, moveSymbol, diff, problem, condition, '\n'])
                    continue

                elif promptLoop == True:
                    textFile += store
                    promptLoop = False
                else:
                    promptLoop = False

                if move == 'correctness feedback':
                    if row[2] == 'correct':
                        correct = '+'
                    elif row[2] == 'incorrect':
                        correct = 'X'
                else:
                    correct = ' '

                textFile += ' '.join([correct, moveSymbol, diff, problem, condition, '\n'])
                lastTimeStamp = timeStamp

    os.chdir('..')
    os.chdir('log_mod')
    outFile = open(log, 'w')
    outFile.write(''.join(textFile))
    os.chdir('..')
    os.chdir(directory)
    textFile = ''
    lastTimeStamp = None

os.chdir('..')
