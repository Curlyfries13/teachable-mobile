# This is the class that holds data for the learner profiles
# given data, the model will update
# written by: Jon Yocky

import sys
import math
import json
import re
import SimulationObjects as Sim
import time
import datetime
import copy
from collections import OrderedDict

p = None
timeStamp = None
quiet = False

class Profile:
	def __init__(self, subjectID='-1'):
		self.problems = []
		self.currentProblem = -1
		self.average = ProblemStats()
		self.subjectID = subjectID
		self.condition = ''

	def updateAverage(self):
		self.average.reset()
		for problem in self.problems:
			for key in self.average.errorTracking:
				self.average.errorTracking[key] += problem.errorTracking[key]
			# self.average.errorTracking['correctProb'] += problem.errorTracking['correctProb']
			# self.average.errorTracking['attempts'] += problem.errorTracking['attempts']
			#
			# self.average.errorTracking['offByNx'] = (problem.errorTracking['offByNx'] + self.average.errorTracking['offByNx'])/2
			# self.average.errorTracking['offByNy'] = (problem.errorTracking['offByNy'] + self.average.errorTracking['offByNy'])/2
			# self.average.errorTracking['offByCount'] += problem.errorTracking['offByCount']
			# self.average.errorTracking['sumError'] += problem.errorTracking['sumError']
			# self.average.errorTracking['ignoreX'] += problem.errorTracking['ignoreX']
			# self.average.errorTracking['ignoreY'] += problem.errorTracking['ignoreY']
			# self.average.errorTracking['flippingError'] += problem.errorTracking['flippingError']
			# self.average.errorTracking['noPlot'] += problem.errorTracking['noPlot']
			#
			# self.average.behaviors['xFirst'] += problem.behaviors['xFirst']
			# self.average.behaviors['yFirst'] += problem.behaviors['yFirst']
			# self.average.behaviors['inefficientCorrect'] += problem.behaviors['inefficientCorrect']
			# self.average.behaviors['efficientCorrect'] += problem.behaviors['efficientCorrect']
			# self.average.behaviors['inefficientCorrect'] += problem.behaviors['inefficientCorrect']
			# self.average.behaviors['efficientIncorrect'] += problem.behaviors['efficientIncorrect']
			# self.average.behaviors['movesReverse'] += problem.behaviors['movesReverse']
			# self.average.behaviors['rotatesReverse'] += problem.behaviors['rotatesReverse']
			# self.average.behaviors['wandering'] += problem.behaviors['wandering']

	def reset(self):
		global quiet
		if not quiet:
			print('Dumping Profile\'s problem tracking')
		for problem in self.problems:
			problem.reset()

	def getProblemStats(self, problemId):
		for problem in self.problems:
			if problem.problemId == problemId:
				return problem
		problemStats = ProblemStats(problemId)
		self.problems.append(problemStats)
		return self.problems[-1]

	def setID(self, subjectID):
		self.subjectID = subjectID

	def setCondition(self, condition):
		self.condition = condition

	def cleanup(self):
		for problem in self.problems:
			if problem.errorTracking['attempts'] == 0:
				self.problems.remove(problem)

	def __str__(self):
		string = []
		string.append(self.subjectID + '\n')
		string.append('-Number of Problems: ' + str(len(self.problems)) + '\n')
		for problem in self.problems:
			string.append(str(problem))
			string.append('\n')
		return ''.join(string)

	def __repr__(self):
		return str(self)

class ProblemStats:

	def __init__(self, pId=-1):
		# print('Initiating learner profile')
		# these probabilistic factors will be used to model the subject's approach
		# start all measures at 0 (we don't know how the student will behave yet)
		problemDescriptorKeys = { 'quadrant':0 ,'negativeX':False,
		'negativeY':False, 'xComp':False, 'yComp':False }
		# off by n chirality is determined as nearer or farther from the origin
		# off by n closer to the origin is negative, farther is positive.
		errorTrackingKeys = { 'correctProb':0, 'attempts':0, 'offByNx':0,
		'offByNy':0, 'offByNxMag':0, 'offByNyMag':0, 'offByNxChir':0,
		'offByNyChir':0, 'invertX':0, 'invertY':0, 'offByCount':0, 'sumError':0,
		'ignoreX':0, 'ignoreY':0, 'flippingError':0, 'noPlot':0, 'deleteMoves':0 }
		behaviorKeys = { 'xFirst':0, 'yFirst':0, 'inefficientIncorrect':0,
		'efficientCorrect':0, 'efficientIncorrect':0,
		'inefficientCorrect':0, 'movesReverse':0, 'rotatesReverse':0,
			'wandering':0 }

		self.problemId = pId
		self.timeStamp = 0
		self.problemDescriptor = OrderedDict(sorted(problemDescriptorKeys.items(), key=lambda t: t[0]))
		self.errorTracking = OrderedDict(sorted(errorTrackingKeys.items(), key=lambda t: t[0]))
		self.behaviors = OrderedDict(sorted(behaviorKeys.items(), key=lambda t: t[0]))

	def __str__(self):
		string = []
		string.append('-Problem Id: ')
		string.append(str(self.problemId) + '\n')
		string.append('-Problem Descriptor\n')
		for key in self.problemDescriptor:
			string.append(key + ': ')
			string.append(str(self.problemDescriptor[key]))
			string.append('\n')
		string.append('\n-ErrorTracking\n')
		for key in self.errorTracking:
			string.append(key + ': ')
			string.append(str(self.errorTracking[key]))
			string.append('\n')
		string.append('\n-Behaviors\n')
		for key in self.behaviors:
			string.append(key + ': ')
			string.append(str(self.behaviors[key]))
			string.append('\n')
		return ''.join(string)

	def __repr__(self):
		return str(self)

	def __add__(self, other):
		if type(other) != type(self):
			raise TypeError('incompatible type')
		else:
			result = ProblemStats()
			for key in self.errorTracking:
				result.errorTracking[key] = (self.errorTracking[key] + other.errorTracking[key])
			for key in self.behaviors:
				result.behaviors[key] = (self.behaviors[key] + other.behaviors[key])
			result.problemDescriptor = copy.deepcopy(self.problemDescriptor)
			return result


	def reset(self):
		for element in self.errorTracking:
			self.errorTracking[element] = 0
		for element in self.behaviors:
			self.behaviors[element] = 0
		self.timeStamp = 0

# this is used when we call from the webpagge
def parseStepList(stepList, problem):
	answer = findAnswer(stepList, problem)
	print('Parsing steplist: ', [step for step in stepList])
	if 'correct' in request.vars and reqest.vars['correct'] == 'true':
		parseCorrect(stepList, problem)
	elif 'correct' in request.vars and request.vars['correct'] == 'false':
		parseIncorrect(stepList, problem, answer)
	else:
		# TODO: not a helpful message
		print('Error!')

def findAnswer(stepList, problem):
	location = [0,0]
	logLoc = [0,0]
	orientation = 0
	logRot = 0
	points = []
	provisionalPoint = None
	answer = Sim.Answer([],[])
	provisionalAnswer = Sim.Answer([],[])
	# deleteTarget = re.compile(r'(?P<move>Move)|(?P<turn>Turn) (?P<mag>[0-9]*)')
	stepMax = len(stepList)

	for index, step in enumerate(stepList):
		if (index+1) < stepMax:
			if step.problemId != stepList[index+1].problemId:
				if step.label == stepList[index+1].label and step.name == stepList[index+1].name:
					stepList.remove(step)
					stepMax -= 1

	for step in stepList:
		### Useful for stepping ###
		# input()
		# print(location, orientation, step, index)

		# try to reconcile the position given with that in the logs
		hasState = False
		if step.state[0] != None:
			hasState = True
			logLoc = [step.state[0], step.state[1]]
			logRot = step.state[2]

			if (location != logLoc):
				location = copy.deepcopy(logLoc)

			if orientation != logRot:
				orientation = logRot
		else:
			hasState = False

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
		elif step.name == 'delete':
			profile = getProfile()
			profile.getProblemStats(problem.id).errorTracking['deleteMoves'] += 1

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
			if(logLoc != location and hasState):
				print('Error plotting point!')
				points.append(copy.copy(logLoc))
			else:
				points.append(copy.copy(location))

	pointCounter = 1
	if len(points) == 0:
		provisionalPoint = Sim.Point('P' + str(pointCounter), location[0], location[1])
		provisionalAnswer.points.append(provisionalPoint)
	answer.lines = []
	for point in points:
		newPoint = Sim.Point('P' + str(pointCounter),point[0], point[1])
		answer.points.append(newPoint)
		pointCounter += 1
	### only useful in stepmode
	# print ('Answer: ', [point for point in answer.points])
	return answer, provisionalAnswer,

# this will be used in other applications (looking at logs or tests)
# returns if the answer was correct or not. Lower functions change the profile
def parseAnswer(problem, stepList):
	# print(problem.solution, stepList)
	# NOTE the last point is the one examined by the system

	### only useful in step mode
	# print('parrseAnswer', stepList)
	###
	answer, provisionalAnswer = findAnswer(stepList, problem)
	answerPoint = None; solutionPoint = None
	describeProblem(problem)
	parseBehavior(stepList, problem)
	if answer.points:
		answerPoint = [answer.points[-1].x, answer.points[-1].y]

	if problem.solution.points:
		solutionPoint = [problem.solution.points[-1].x, problem.solution.points[-1].y]

		if answerPoint == solutionPoint:
			# correct answer
			# print('parsing correct')
			parseCorrect(stepList, problem)
			return True, answerPoint
		else:
			# print('parsing incorrect')
			parseIncorrect(stepList, problem, answer, provisionalAnswer)
			return False, answerPoint
	else:
		print('Error! No problem point\n', problem, answer)
		return False, answer

# update the profile's description of the problem.
def describeProblem(problem):
	# detect the characteristics of the problem
	profile = getProfile()
	descriptor = profile.getProblemStats(problem.id).problemDescriptor
	solution = problem.solution

	if solution.points:
		if solution.points[0].x != 0:
			descriptor['xComp'] = True

		if solution.points[0].y != 0:
			descriptor['yComp'] = True

		if solution.points[0].x < 0:
			descriptor['negativeX'] = True

		if solution.points[0].y < 0:
			descriptor['negativeY'] = True

		if solution.points[0].x != 0 and solution.points[0].y != 0:
			if solution.points[0].x > 0:
				if solution.points[0].y > 0:
					descriptor['quadrant'] = 1
				else:
					descriptor['quadrant'] = 4
			else:
				if solution.points[0].y > 0:
					descriptor['quadrant'] = 2
				else:
					descriptor['quadrant'] = 3

def setQuiet(isQuiet):
	global quiet
	if isQuiet:
		quiet = True
	else:
		quiet = False

def getProfile():
	global p
	if p != None:
		return p
	else:
		p = Profile()
		return p

def getValues():
	return json.dumps((p,s))

def parseEfficiency(stepList, problem, isCorrect):
	# expects a stepList, problem, and boolean
	# stepList is a list with elements of the following format {name, label, op{}}
	# problem is a problem object in the folloing format
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

def parseError(problem, answer, provisionalAnswer):
	breakFlag = False
	print(problem, answer)
	if len(answer.points) == 0:
		getProfile().getProblemStats(problem.id).errorTracking['noPlot'] += 1
		# Just analyze as if there is an answer is here, provided by the provisional asnwer
		answer = provisionalAnswer
		return

	isProbOneDimensional = checkOneDimensional(problem)
	isAnsOnedimensional = checkAnsOneDimensional(answer)
	if(isAnsOnedimensional and isProbOneDimensional):
		# both solutions are 1D
		if isFlipping(problem, answer):
			getProfile().getProblemStats(problem.id).errorTracking['flippingError'] += 1
			return

	elif not isProbOneDimensional and isAnsOnedimensional and isSumming(problem, answer):
		# resolved

		getProfile().getProblemStats(problem.id).errorTracking['sumError'] += 1
		return

	elif isFlipping(problem, answer):
		getProfile().getProblemStats(problem.id).errorTracking['flippingError'] += 1
		return

	if isInvertingX(problem, answer):
		getProfile().getProblemStats(problem.id).errorTracking['invertX'] += 1
		breakFlag = True
	if isInvertingY(problem, answer):
		getProfile().getProblemStats(problem.id).errorTracking['invertY'] += 1
		breakFlag = True

	if parseIgnore(problem, answer):
		breakFlag = True

	elif not breakFlag:
		profile = getProfile()
		distance = parseOffByN(problem, answer)
		profile.getProblemStats(problem.id).errorTracking['offByCount'] += 1
		profile.getProblemStats(problem.id).errorTracking['offByNx'] = distance[0]
		profile.getProblemStats(problem.id).errorTracking['offByNy'] = distance[1]
		profile.getProblemStats(problem.id).errorTracking['offByNxMag'] = abs(distance[0])
		profile.getProblemStats(problem.id).errorTracking['offByNyMag'] = abs(distance[1])
		x_Chirality = int(math.copysign(1.0, (answer.points[0].x - problem.solution.points[0].x)))
		profile.getProblemStats(problem.id).errorTracking['offByNxChir'] = x_Chirality
		y_Chirality = int(math.copysign(1.0, (answer.points[0].y - problem.solution.points[0].y)))
		profile.getProblemStats(problem.id).errorTracking['offByNyChir'] = y_Chirality
		# print(profile.offByNx,profile.offByNy)

def isSumming(problem, answer):
	# print('checking isSumming')
	ax = answer.points[-1].x
	ay = answer.points[-1].y

	px = problem.solution.points[0].x
	py = problem.solution.points[0].y

	possibleAnswers = [px + py, py - px, px - py]
	if ax in possibleAnswers or ay in possibleAnswers:
		return True
	return False

def isInvertingX(problem, answer):
	ax = answer.points[-1].x

	px = problem.solution.points[0].x

	if (-1*ax) == px and ax != 0:
		return True
	else:
		return False

def isInvertingY(problem, answer):
	ay = answer.points[-1].y

	py = problem.solution.points[0].y
	if (-1*ay) == py and ay != 0:
		return True
	else:
		return False

def parseIgnore(problem, answer):
	# print('checking ignoring')
	ax = answer.points[-1].x
	ay = answer.points[-1].y

	px = problem.solution.points[0].x
	py = problem.solution.points[0].y
	detected = False

	if px == ax and py != ay and ay == 0:
		getProfile().getProblemStats(problem.id).errorTracking['ignoreY'] += 1
		detected = True

	if py == ay and px != ax and ax == 0:
		getProfile().getProblemStats(problem.id).errorTracking['ignoreX'] += 1
		detected = True

	return detected

# A flip is defined as the student switching the x and y coordinates
# exaples would be giving (1,2) for a problem (2,1)
def isFlipping(problem, answer):
	# print('checking flip')
	ax = answer.points[-1].x
	ay = answer.points[-1].y

	px = problem.solution.points[0].x
	py = problem.solution.points[0].y

	#print(ax, ay)
	#print(px, py)

	if ax == py and ay == px:
		# print('flipping')
		return True
	else:
		return False

def parseOffByN(problem, answer):
	# print('check off by N')
	# print("checking off by N")
	ax = answer.points[-1].x
	ay = answer.points[-1].y

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
	ax = answer.points[-1].x
	ay = answer.points[-1].y

	if ax == 0 or ay == 0:
		# print('is 1D')
		return True
	else:
		return False

def parseCorrect(stepList, problem):
	global timeStamp
	getProfile().getProblemStats(problem.id).timeStamp = timeStamp
	getProfile().getProblemStats(problem.id).errorTracking['attempts'] += 1
	getProfile().getProblemStats(problem.id).errorTracking['correctProb'] += 1
	if parseEfficiency(stepList, problem, True) == 1:
		getProfile().getProblemStats(problem.id).behaviors['efficientCorrect'] += 1
	else:
		getProfile().getProblemStats(problem.id).behaviors['inefficientCorrect'] += 1
	getProfile().currentProblem = problem.id
	stepLength = len(stepList)
	problemContainsNeg = False
	movedReverse = False

	if problem.solution.points[0].x < 0:
		problemContainsNeg = True
	if problem.solution.points[0].y < 0:
		problemContainsNeg = True

def parseIncorrect(stepList, problem, answer, provisionalAnswer):
	global timeStamp
	getProfile().getProblemStats(problem.id).timeStamp = timeStamp
	getProfile().getProblemStats(problem.id).errorTracking['attempts'] += 1
	if parseEfficiency(stepList, problem, False) == 1:
		getProfile().getProblemStats(problem.id).behaviors['efficientIncorrect'] += 1
	else:
		getProfile().getProblemStats(problem.id).behaviors['inefficientIncorrect'] += 1

	getProfile().lastProblem=problem.id
	errorType = parseError(problem, answer, provisionalAnswer)

def parseBehavior(stepList, problem):
	profile = getProfile()
	problemStats = profile.getProblemStats(problem.id)

	movedReverse = False
	for step in stepList:
		if step.name == 'moveDistance' and step.op.distance < 0 and (problemStats.problemDescriptor['negativeX'] or problemStats.problemDescriptor['negativeY']):
			problemStats.behaviors['movesReverse'] += 1
			movedReverse = True
	if (problemStats.problemDescriptor['negativeX'] or problemStats.problemDescriptor['negativeY']) and not movedReverse:
		problemStats.behaviors['rotatesReverse'] += 1

	if problemStats.problemDescriptor['xComp'] and problemStats.problemDescriptor['yComp']:
		orientation = 0
		for step in stepList:
			if step.name == 'moveDistance':
				if orientation == 0 or orientation == 180:
					problemStats.behaviors['xFirst'] += 1
					return
				else:
					problemStats.behaviors['yFirst'] += 1
					return
			elif step.name == 'turnAngle':
				orientation = (orientation + step.op.angle) % 360

def reset():
	getProfile().reset()

def updateTimeStamp(time):
	global timeStamp
	timeStamp = time
