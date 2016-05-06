# This module wil allow the tester to use log data to run tests and get profiles

import re
import sys
import os
import csv
import datetime
import SimulationObjects as Sim

def readLog(fileName, fileDirectory, graphFlag=False):
	# return a list of stepLists
	# Metadata of the step lists follows this order:
	# (problem, stepList) tuple, user, correctness, line (in the log)
	# timeStamp, currentState tuple
	filePath = None
	if fileDirectory:
		filePath = os.path.join(fileDirectory, fileName)
	else:
		filePath = fileName

	with open(filePath, 'r') as log:
		pointPattern = re.compile(r'\((?P<x>-{0,1}?[0-9]+), (?P<y>-{0,1}?[0-9]+)\)')
		deletePattern = re.compile(r'\'label\':\'(?P<label>.*)\'')
		timeStampPattern = re.compile(r'(?P<month>[0-9]{1,2})/(?P<day>[0-9]{1,2})/(?P<year>[0-9]{4}) - (?P<hour>[0-9]{1,2}):(?P<minute>[0-9]{1,2}):(?P<second>[0-9]{1,2})')
		# This pattern should catch the robot's position and the
		# last point placed.
		currentStatePattern = re.compile(r'^R,(?P<x>-?[0-9]{1,2}),(?P<y>-?[0-9]{1,2}),(?P<rot>-?[0-9]{1,3}).*(:P[0-9],(?P<px>-?[0-9](\.[0-9]{2})?),(?P<py>-?[0-9](\.[0-9]{2}))$)?')

		user = ''
		logReader = csv.reader(log)
		currentStepList = []
		StepLists = []
		TimeStamps = []
		problem = None
		currentState = []
		lastRowTS = None
		condition = ''

		for line, row in enumerate(logReader):
			if len(row) == 11:
				# we expect the correct format hereafter
				if 'prompt' in row or 'attribution' in row or 'checked emotions' in row:
					continue

				stateMatch = currentStatePattern.search(row[3])
				timeStampMatch = timeStampPattern.search(row[0])
				timeStamp = datetime.datetime(year=int(timeStampMatch.group('year')), month=int(timeStampMatch.group('month')), day=int(timeStampMatch.group('day')), hour=int(timeStampMatch.group('hour')), minute=int(timeStampMatch.group('minute')),  second = int(timeStampMatch.group('second')))
				TimeStamps.append(timeStamp)
				if row[10]:
					# get the session condition
					condition = row[10]
				# the state tuple is as follows:
				# x position, y position, last point x, last point y

				if stateMatch:
					if stateMatch.group('px') and stateMatch.group('py'):
						currentState = (float(stateMatch.group('x')), float(stateMatch.group('y')), int(stateMatch.group('rot')), float(stateMatch.group('px')), float(stateMatch.group('py')))
					else:
						currentState = (float(stateMatch.group('x')), float(stateMatch.group('y')), int(stateMatch.group('rot')), None, None)
				else:
					currentState = (None, None, None, None)

				if row[8] != user:
					user = row[8]

				if 'moveDistance' in row[1]:
					distance = int(row[2])
					label = 'Move ' + str(distance)
					name = 'moveDistance'
					op = Sim.Op(distance=distance, angle=None)
					pid = row[7]
					step = Sim.Step(label=label, name=name, op=op, problemId=pid, state=currentState)
					currentStepList.append(step)

				elif 'turnAngle' == row[1]:
					angle = int(row[2])
					label = 'Turn '+ str(angle)
					name = 'turnAngle'
					pid = row[7]
					op = Sim.Op(distance=None, angle=angle)
					step = Sim.Step(label=label, name=name, op=op, problemId=pid, state=currentState)
					currentStepList.append(step)

				elif 'plotPoint' in row[1]:
					pid = row[7]
					op = None
					step = Sim.Step(label='Plot Point', name='plotPoint', op=op, problemId=pid, state=currentState)
					currentStepList.append(step)

				##### META STEPS #####
				#
				# THIS SECTION ISNT USEFUL, delete does nothing!
				# if 'Deleted step from list' in row:
				# 	# remove the last step
				# 	# NOTE some deletes dont change the robot's position!
				# 	name = 'delete'
				# 	match = deletePattern.search(row[3])
				# 	if match:
				# 		label = match.group('label')
				# 		print(label)
				# 	op = None
				# 	step = Sim.Step(label=label, name=name, op=op)
				# 	currentStepList.append(step)
				#
				elif 'reset' in row or 'replay' in row:
					# NOTE we may want to just ingore this
					# print(currentStepList, 'reset', line)
					label = 'reset'
					name = 'reset'
					step = Sim.Step(label=label, name=name, op=None, state=currentState)
					currentStepList.append(step)

				elif 'Deleted step from list' in row:
					lable = 'delete'
					name = 'delete'
					step = Sim.Step(label=label, name=name, op=None, state=currentState)
					currentStepList.append(step)

				elif 'Refresh' in row:
					label = 'refresh'
					name = 'refresh'
					op = None
					step = Sim.Step(label=label, name=name, op=op, state=currentState)
					currentStepList.append(step)

				elif 'correctness feedback' in row:
					# determine the problem as well
					# print('check')
					correct = None
					if 'correct' in row:
						correct = True
					else:
						correct = False
					probId = row[7]
					problemString = row[6]


					match = pointPattern.search(problemString)
					if match:
						x = int(match.group('x'))
						y = int(match.group('y'))
						point = Sim.Point('P1', x, y)
					else:
						point = Sim.Point('P1', 0, 0)
					solution = Sim.Solution([], [point])
					problem = Sim.Problem(probId=probId, solution=solution)
					StepLists.append( {'problem':problem, 'stepList':list(currentStepList), 'user':user, 'correct':correct, 'line':line, 'timeStamps':TimeStamps, 'condition':condition} )
					TimeStamps = []
					currentStepList = []
					stateList = []
					currentProblem = -1

		return StepLists

if __name__ == '__main__':
	readLog('p34.csv', 'test_logs')
