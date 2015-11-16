# This is the class that holds data for the learner profiles
# given data, the model will update
# written by: Jon Yocky

# TODO: names should probably be named a little better/more consistently

import sys
import json
import re
import SimulationObjects as Sim
import time

class Profile:

	def __init__(self):
		print('Initiating learner profile')
		# these probabilistic factors will be used to model the subject
		# start all measures at 0 (we don't know how the student will behave yet)
		self.ErrorTracking = {
			"xFirst": 0,
			"yFirst": 0,

			"inefficientCorrect": 0,
			"efficientCorrect": 0,
			"efficientIncorrect": 0,
			"inefficientIncorrect" : 0,

			"movesReverse": 0,
			"rotatesReverse": 0,

			"correctProb": 0,
			"problems": 0,
			"attempts": 0,

			"offByNx": 0,
			"offByNy": 0,
			"offByCount": 0,
			"sumError": 0,
			"ignoreX": 0,
			"ignoreY": 0,
			"flippingError": 0,
			"wandering": 0,
			"lastProblem": -1
		}

	def __str__(self):
		string = []
		for key in self.ErrorTracking:
			string.append(str(key))
			string.append(': ')
			string.append(str(self.ErrorTracking[key]))
			string.append('\n')
		return ''.join(string)

	def reset(self):
		for element in self.ErrorTracking:
			self.ErrorTracking[element] = 0

		self.lastProblem = -1

p = None
quiet = False

# this is used when we call from the webpagge
def parseStepList(stepList, problem):
	answer = findAnswer(stepList)
	print('Parsing steplist: ', [step for step in stepList])
	if 'correct' in request.vars and reqest.vars['correct'] == 'true':
		parseCorrect(stepList, problem)
	elif 'correct' in request.vars and request.vars['correct'] == 'false':
		parseIncorrect(stepList, problem, answer)
	else:
		# TODO: not a helpful message
		print('Error!')


def findAnswer(stepList):
	location = [0,0]
	orientation = 0
	points = []
	answer = Sim.Answer([],[])
	deleteTarget = re.compile(r'(?P<move>Move)|(?P<turn>Turn) (?P<mag>[0-9]*)')
	# print(stepList, len(stepList))
	stepMax = len(stepList)
	for index, step in enumerate(stepList):
		if index+1 < stepMax:
			if step.problemId != stepList[index+1].problemId:
				if step.label == stepList[index+1].label and step.name == stepList[index+1].name:
					stepList.remove(step)
	# print('filtered ', stepList)

	for index, step in enumerate(stepList):
		### Useful for stepping ###
		# input()
		# print(location, orientation, step, index)

		#####  META STEPS #####
		# NOTE each meta step must be deleted after it is executed;
		# meta-steps only help the log simulator to copy the actions of the old system
		if step.name == 'reset':
			# NOTE we aren't doing anything with the data
			# after the submitted data is correctly parsed, we need
			# to look at the unsubmitted data as well!
			#stepList.remove(step)
			location = [0,0]
			orientation = 0
			points = []

		elif step.name == 'refresh':
			# NOTE refresh != reset, reset also removes all points
			#stepList.remove(step)
			location = [0,0]
			orientation = 0

		###### TRUE STEPLIST OBJECTS ######
		# NOTE don't delete these from the list
		elif step.name == 'moveDistance':
			if step.op.distance > 10:
				# these should just be ignored; the system does this
				continue
			if orientation == 0:
				location[0] += step.op.distance
			elif orientation == 90:
				location[1] += step.op.distance
			elif orientation == 180:
				location[0] -= step.op.distance
			elif orientation == 270:
				location[1] -= step.op.distance
		elif step.name == 'turnAngle':
			orientation = (orientation + step.op.angle) % 360
		elif step.name == 'plotPoint':
			points.append(location)

	answer.lines = []
	pointCounter = 1
	for point in points:
		newPoint = Sim.Point('P' + str(pointCounter),point[0], point[1])
		answer.points.append(newPoint)
		pointCounter += 1

	### only useful in stepmode
	# print ('Answer: ', [point for point in answer.points])
	return answer

# this will be used in other applications (looking at logs or tests)
# returns if the answer was correct or not
def parseAnswer(problem, stepList):
	# print(problem.solution, stepList)
	# NOTE the last point is the one examined by the system

	### only useful in step mode
	# print('parrseAnswer', stepList)
	###

	answer = findAnswer(stepList)
	if answer.points:
		answerPoint = [answer.points[-1].x, answer.points[-1].y]

	else:
		# print('parsing incorrect - missing point')
		parseIncorrect(stepList, problem, answer)
		return False

	if problem.solution.points:
		solutionPoint = [problem.solution.points[-1].x, problem.solution.points[-1].y]

		# print (answerPoint, solutionPoint)
		if answerPoint == solutionPoint:
			# correct answer
			# print('parsing correct')
			parseCorrect(stepList, problem)
			return True
		else:
			# print('parsing incorrect')
			parseIncorrect(stepList, problem, answer)
			return False

def setQuiet(isQuiet):
	global quiet
	if isQuiet:
		quiet = True
	else:
		quiet = False

def getProfile():
	# DEBUG
	# print "getting profile"
	global p
	if p != None:
		return p
	else:
		p = Profile()
		# print(p)
		return p

def getSystemState():
	global s
	if s != None:
		return s
	else:
		s = SystemState()
		return s

def getValues():
	return json.dumps((p,s))

def parseEfficiency(stepList, problem, isCorrect):
	# expects a stepList, problem, and boolean
	# stepList is a list with elements of the following format {name, label, op{}}
	# problem is a problem object in the folloing format
	'''
	problemObject{
		lines, name, points, problemType, solution{
			lines, points, text, type
		}
	}

	problemObject.solution.points {name, x, y}
	'''
	if(problem.text == 'Learning to use TAG'):
		# skip this analysis
		return

	stepListLength = len(stepList)
	if isCorrect and (problem.solution.points[0].x == 0 or problem.solution.points[0].y == 0):
		# 1 dimensional problem
		if problem.solution.points[0].x != 0:
			if stepListLength == 2:
				return 1
			elif stepListLength == 3 and stepList[0].name == 'turnAngle':
				return 1
			else:
				return 0
		else:
			# moves in the y direction only
			if stepListLength == 3:
				return 1
			else:
				return 0
	elif isCorrect:
		# problem has 2 dimmensions
		if stepListLength == 5 and stepList[0].name == 'turnAngle':
			return 1
		elif stepListLength == 4:
			return 1
		else:
			return 0
	else:
		# TODO Jon some of these cases are inefficient! esp. (x, 0) or (0, y)!

		# incorrecct solution, may be able to glean useful information
		for step in stepList:
			if (step.name == 'turnAngle' and step.op.angle == 360) or (step.name == 'moveDistance' and step.op.distance == 0):
				# we can detect this as a null move
				return 0

			# should fix TODO above
			if(step.name == 'turnAngle' and step.op.angle == 180):
				if stepList[0].name != 'turnAngle' or stepList[0].op.angle != 180:
					# the only case where turning 180 is efficient is on the first move
					# here we've found a 180 turn that was not the first move
					return 0

		if stepListLength == 5:
			# check to see if the movement pattern matches an efficient solution.
			if stepList[0].name == 'turnAngle' and stepList[1].name == 'moveDistance' and stepList[2].name == 'turnAngle' and stepList[3].name == 'moveDistance' and stepList[4].name == 'plotPoint':
				return 1
			else:
				return 0

		elif stepListLength == 4:
			# if the solution is on the x-axis and student turns 180 this will register as efficient
			if stepList[0].name == 'moveDistance' and stepList[1].name == 'turnAngle' and stepList[2].name == 'moveDistance' and stepList[3].name == 'plotPoint':
				return 1
			else:
				return 0

		elif stepListLength == 3:
			if stepList[0].name == 'turnAngle' and stepList[1].name == 'moveDistance' and stepList[2].name == 'plotPoint':
				return 1
			else:
				return 0

		elif stepListLength == 2:
			if stepList[0] == 'moveDistance' and stepList[1].name == 'plotPoint':
				return 1
			else:
				return 0

		elif stepListLength > 5:
			# the solution is inefficient
			return 0
		else:
			# in this case the student either doesn't understand how to use the system
			# or the system is inefficient.
			return 0

def parseError(problem, answer):

	# TODO check if point has been plotted
	if len(answer.points) == 0:
		# forgot to plot point
		# print('forgot point')
		# TODO figure things to do here!
		return

	isProbOneDimensional = checkOneDimensional(problem)
	isAnsOnedimensional = checkAnsOneDimensional(answer)
	if(isAnsOnedimensional and isProbOneDimensional):
		# both solutions are 1D
		if isFlipping(problem, answer):
			getProfile().ErrorTracking['flippingError'] += 1
	elif(isProbOneDimensional):
		# odd case
		# print('resolved')
		# UNIMPLEMENTED
		pass
	elif(isAnsOnedimensional):
		if isSumming(problem, answer):
			# resolved
			# print('summing')
			getProfile().ErrorTracking['sumError'] += 1
		elif isFlipping(problem, answer):
			getProfile.ErrorTracking['flippingError'] += 1
		elif parseIgnore(problem, answer):
			# resolved
			# print('ignoring')
			pass
	else:
		profile = getProfile()
		distance = parseOffByN(problem, answer)
		profile.ErrorTracking['offByCount'] += 1
		if profile.ErrorTracking['offByNx'] == 0:
			profile.ErrorTracking['offByNx'] = distance[0]
		else:
			profile.ErrorTracking['offByNx'] = (distance[0] + profile.ErrorTracking['offByNx'])/2

		if profile.ErrorTracking['offByNy'] == 0:
			profile.ErrorTracking['offByNy'] = distance[1]
		else:
			profile.ErrorTracking['offByNy'] = (distance[1] + profile.ErrorTracking['offByNy'])/2
		# print(profile.offByNx,profile.offByNy)

def isSumming(problem, answer):
	# print('checking isSumming')
	ax = answer.points[0].x
	ay = answer.points[0].y

	px = problem.solution.points[0].x
	py = problem.solution.points[0].y

	possibleAnswers = [px + py, py - px, px - py]

	if ax in possibleAnswers or ay in possibleAnswers:
		return True

	return False

def parseIgnore(problem, answer):
	# print('checking ignoring')
	ax = answer.points[0].x
	ay = answer.points[0].y

	px = problem.solution.points[0].x
	py = problem.solution.points[0].y

	if px == ax and py != ay and ay == 0:
		getProfile().ErrorTracking['ignoreY'] += 1
		return True

	if py == ay and px != ax and ax == 0:
		getProfile().ErrorTracking['ignoreX'] += 1
		return True

	return False

# A flip is defined as the student switching the x and y coordinates
# exaples would be giving (1,2) for a problem (2,1)
def isFlipping(problem, answer):
	# print('checking flip')
	ax = answer.points[0].x
	ay = answer.points[0].y

	px = problem.solution.points[0].x
	py = problem.solution.points[0].y

	#print(ax, ay)
	#print(px, py)

	if abs(ax) == abs(py) and abs(ay) == abs(px):
		# print('flipping')
		return True
	else:
		return False

def parseOffByN(problem, answer):
	# print('check off by N')
	# print("checking off by N")
	ax = answer.points[0].x
	ay = answer.points[0].y

	px = problem.solution.points[0].x
	py = problem.solution.points[0].y

	difference = [0, 0]
	if px == ax and py == ay:
		return difference
	else:
		difference[0] = px - ax
		difference[1] = py - ay
	# print(difference)
	return difference

def checkOneDimensional(problem):
	# print('check 1D problem')
	if problem.solution.points[0].x == 0 or problem.solution.points[0].y == 0:
		# print('is 1D')
		return True
	else:
		return False

def checkAnsOneDimensional(answer):
	# print('check 1D ans')
	ax = answer.points[0].x
	ay = answer.points[0].y

	if ax == 0 or ay == 0:
		# print('is 1D')
		return True
	else:
		return False

def parseCorrect(stepList, problem):
	getProfile().ErrorTracking['attempts'] += 1
	getProfile().ErrorTracking['correctProb'] += 1
	if parseEfficiency(stepList, problem, True) == 1:
		getProfile().ErrorTracking['efficientCorrect'] += 1
	else:
		getProfile().ErrorTracking['inefficientCorrect'] += 1
	if (getProfile().ErrorTracking['lastProblem'] != problem.id and getProfile().ErrorTracking['lastProblem'] != -1):
		getProfile().ErrorTracking['problems'] += 1
	getProfile().ErrorTracking['lastProblem'] = problem.id
	stepLength = len(stepList)
	problemContainsNeg = False
	movedReverse = False

	if problem.solution.points[0].x < 0:
		problemContainsNeg = True
	if problem.solution.points[0].y < 0:
		problemContainsNeg = True

	for step in stepList:
		# check for moving in reverse
		if step.name == 'moveDistance' and step.op.distance < 0 and problemContainsNeg:
			getProfile().ErrorTracking['movesReverse'] += 1
			movedReverse = True
		elif movedReverse and problemContainsNeg:
			getProfile().ErrorTracking['rotatesReverse'] += 1

def parseIncorrect(stepList, problem, answer):
	getProfile().ErrorTracking['attempts'] += 1
	if parseEfficiency(stepList, problem, False) == 1:
		getProfile().ErrorTracking['efficientIncorrect'] += 1
	else:
		getProfile().ErrorTracking['inefficientIncorrect'] += 1

	if (getProfile().ErrorTracking['lastProblem'] != problem.id and getProfile().ErrorTracking['lastProblem'] != -1):
		getProfile().ErrorTracking['problems'] += 1
	getProfile().ErrorTracking['lastProblem'] = problem.id
	errorType = parseError(problem, answer)

def reset():
	getProfile().reset()
