# This module wil allow the tester to use log data to run tests and get profiles
#

import re
import sys
import os
import csv
import SimulationObjects as Sim

def readLog(fileName, fileDirectory):
	# return a list of stepLists
	filePath = None
	if fileDirectory:
		filePath = os.path.join(fileDirectory, fileName)
	else:
		filePath = fileName

	with open(filePath, 'r') as log:
		pointPattern = re.compile(r'\((?P<x>-{0,1}?[0-9]+), (?P<y>-{0,1}?[0-9]+)\)')
		deletePattern = re.compile(r'\'label\':\'(?P<label>.*)\'')

		user = ''
		logReader = csv.reader(log)
		currentStepList = []
		StepLists = []
		problem = None;
		# dupli_check = []
		for line, row in enumerate(logReader):
			if len(row) == 11:

				# we expect the correct format here
				# print(currentProblem, row[7], line)
				if 'prompt' in row or 'attribution' in row or 'checked emotions' in row:
					continue
				if row[9] != user:
					user = row[9]

				# META STEP

				if 'moveDistance' in row[1]:
					distance = int(row[2])
					label = 'Move ' + str(distance)
					name = 'moveDistance'
					op = Sim.Op(distance=distance,angle=None)
					pid = row[7]
					step = Sim.Step(label=label,name=name,op=op,problemId=pid)
					currentStepList.append(step)
					# print('moved')
				elif 'turnAngle' == row[1]:
					angle = int(row[2])
					label = 'Turn '+ str(angle)
					name = 'turnAngle'
					pid = row[7]
					op = Sim.Op(distance=None,angle=angle)
					step = Sim.Step(label=label,name=name,op=op,problemId=pid)
					currentStepList.append(step)
					# print('turn')
				elif 'plotPoint' in row[1]:
					pid = row[7]
					op = None
					step = Sim.Step(label='Plot Point', name='plotPoint', op=op,problemId=pid)
					currentStepList.append(step)
					# print('plot').append(step)y

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
				# 	step = Sim.Step(label=label,name=name,op=op)
				# 	currentStepList.append(step)
				#
				elif 'reset' in row or 'replay' in row:
					# NOTE we may want to just ingore this
					# print(currentStepList,'reset', line)
					label = 'reset'
					name = 'reset'
					step = Sim.Step(label=label,name=name,op=None)
					currentStepList.append(step)

				elif 'Refresh' in row:
					label = 'refresh'
					name = 'refresh'
					op = None
					step = Sim.Step(label=label,name=name,op=op)
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
					# print(probId, problemString)
					match = pointPattern.search(problemString)
					# print(match)
					if match:
						x = int(match.group('x'))
						y = int(match.group('y'))
						# print(x,y)
						point = Sim.Point('P1',x,y)
					else:
						point = Sim.Point('P1',0,0)
					solution = Sim.Solution([], [point])
					problem = Sim.Problem(probId=probId,solution=solution)
					# print('Added step list, problem tuple')
					StepLists.append((problem,list(currentStepList),user,correct,line))
					currentStepList = []
					currentProblem = -1
		# print(len(StepLists))
		# wait to see what we got
		# input()
		return StepLists

if __name__ == '__main__':
	readLog('p34.csv','test_logs')
