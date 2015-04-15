# This is the class that holds data for the learner profiles
# given data, the model will update
# written by: Jon Yocky

import sys
import json

class Profile:

	def __init__(self):
		print "Initiating learner profile"
		# these probabilistic factors will be used to model the subject
		# start all measures at 0 (we don't know how the student will behave yet)
		self.xFirst = 0
		self.yFirst = 0

		self.inefficientCorrect = 0
		self.efficientCorrect = 0
		self.efficientIncorrect = 0
		self.inefficientIncorrect = 0
		# these should only work with problems that have negative values should use this
		self.movesReverse = 0
		self.rotatesReverse = 0

		self.correctProb = 0
		self.problems = 0
		self.attempts = 0

		self.offByNx = 0
		self.offByNy = 0
		self.sumError = 0
		self.ignoreX = 0
		self.ignoreY = 0

		self.lastProblem = -1

class LearnerProfile:

	p = None

	def getProfile(self):
		# DEBUG
		# print "getting profile"
		if LearnerProfile.p != None:
			return self.p
		else:
			LearnerProfile.p = Profile()
			return LearnerProfile.p

	def getValues(self):
		return json.dumps(self)

	def parseEfficiency(self, stepList, problem, isCorrect):
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
		if isCorrect and (problem.solution.x == 0 or problem.solution.y == 0):
			# 1 dimensional problem
			if problem.solution.x != 0:
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

	def parseError(self, problem, answer):

		# TODO check if point has been plotted
		profile = getProfile()
		if str.find(answer.final, 'P1') == -1:
			# forgot to plot point
			print 'forgot point'

		isProbOneDimensional = checkOneDimensional(problem)
		isAnsOnedimensional = checkAnsOneDimensional(answer)
		if(isAnsOnedimensional and isProbOneDimensional):
			# both solutions are correct we are off by N
			parseOffByN(problem, answer)
		elif(isProbOneDimensional):
			# odd case
			print 'resolved1'
		elif(isAnsOnedimensional):
			if isSumming(problem, answer):
				# resolved
				print 'summing'
				getProfile().sumError += 1
			elif ParseIgnore(problem, answer):
				# resolved
				print 'ignoring'
		else:
			distance = parseOffByN(problem, answer)
			if profile.offByNx == 0:
				profile.offByNx = distance[0]
			else:
				profile.offByNx = (distance[0] + profile.offByNx)/2

			if profile.offByNy == 0:
				profile.offByNy = distance[1]
			else:
				profile.offbyNy = (distance[1] + profile.offByNy)/2


	def isSumming(problem, answer):
		coordinates = pasrseAnswer(answer)
		ax = coordinates[0]
		ay = coordinates[1]

		px = problem.points[0].x
		py = problem.points[0].y

		possibleAnswers = [ax + ay, ay - ax, ax - ay]

		for answer in possibleAnswers:
			if px == answer or py == answer:
				return True

		return False

	def ParseIgnore(problem, answer):
		coordinates = pasrseAnswer(answer)
		ax = coordinates[0]
		ay = coordinates[1]

		px = problem.points[0].x
		py = problem.points[0].y

		if px == ax and py != ay and ay == 0:
			getProfile().ignoreY += 1
			return True

		if py == ay and px != ax and ax == 0:
			getProfile().ignoreX += 1
			return True

		return False

	def isFlipping(problem, answer):
		coordinates = pasrseAnswer(answer)
		ax = coordinates[0]
		ay = coordinates[1]

		px = problem.points[0].x
		py = problem.points[0].y

		if abs(ax) == abs(py) and abs(ay) == abs(px):
			return True
		else:
			return False


	def parseOffByN(self, problem, answer):
		coordinates = pasrseAnswer(answer)
		ax = coordinates[0]
		ay = coordinates[1]

		px = problem.points[0].x
		py = problem.points[0].y

		difference = [0, 0]
		if px == ax and py == ay:
			return difference
		else:
			difference[0] = px - ax
			differnece[1] = py - ay

		return difference


	def checkAnOneDimensional(self, problem):
		if problem.soulution.points[0].x == 0 or problem.solution.points[0].y == 0:
			return True
		else:
			return False

	def checkAnsOneDimensional(self, answer):
		coordinates = parseAnswer(answer)
		x = coordinates[0]
		y = coordinates[1]

		if x == 0 or y == 0:
			return True	x
		else:
			return False

	def parseAnswer
		subString = answer[str.find(answer.final, 'P1'):]
		print subString
		subString = subString[str.find(subString, ',') + 1:]
		stringOffset = str.find(subString, ',')
		x = int(subString[:stringOffset])
		subString = subString[stringOffset + 1:]
		stringOffset = str.find(subString, ':')
		if stringOffset == -1:
			y = int(subString)
		else:
			y = int(subString[:stringOffset])

		coordinates = [x, y]
		return tup

	def parseCorrect(self, stepList, problem):
		getProfile().attempts += 1
		getProfile().correctProb += 1
		getProfile().efficientCorrect += 1 if getProfile().parseEfficiency(stepList, problem, True) == 1 else getProfile().inefficientCorrect += 1
		if (getProfile().lastProblem != problem.id and getProfile.lastProblem != -1):
			getProfile().problems += 1
		getProfile().lastProblem = problem.id
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
				getProfile().movesReverse += 1
				movedReverse = True
			elif movedReverse and problemContainsNeg:
				getProfile().rotatesReverse += 1

	def parseIncorrect(self, stepList, problem, answer):
		getProfile().attempts += 1
		getProfile().efficientIncorrect += 1 if getProfile().parseEfficiency(stepList, problem, False) == 1 else getProfile().inefficientIncorrect += 1

		if (getProfile().lastProblem != problem.id and getProfile.lastProblem != -1):
			getProfile().problems += 1
		getProfile().lastProblem = problem.id
		errorType = parseError(problem, answer)
