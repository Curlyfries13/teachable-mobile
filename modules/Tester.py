# Testing apparatus
# Written by Jonathan Yocky

# right now this will only test the LearnerProfile.
# later on it may become more generalized

import argparse
import sys
import json
import os
import glob
import copy
from abc import ABCMeta
from collections import OrderedDict
import LearnerProfile
import SimulationObjects as Sim
import LogReader
import Grapher as Grapher

def readCommands(argv):
	parser =  argparse.ArgumentParser(description='Prepare testing apparatus')
	parser.add_argument('--test-names', '-n',
						metavar='xyz.test',
						dest = 'names',
						nargs='+',
						action = 'store',
						help='run particular tests'
						)
	# TODO: actually implement this
	parser.add_argument('--quiet', '--shh', '--silent' , '-q',
						dest = 'isQuiet',
						action = 'store_true',
						help = 'Tester will run without input (quietly)'
						)
	parser.add_argument('--test_directory', '-dir',
						default = 'tests',
						dest = 'testRoot',
						action = 'store',
						help = 'Specify the directory to look in for tests')
	parser.add_argument('--log', '-l',
						dest = 'logFiles',
						nargs = '+',
						help = 'Specify the logfile to simulate (may require -dir to be specified)')
	parser.add_argument('--graph', '-g',
						nargs='?',
						dest = 'graphName',
						action = 'store',
						metavar='xyz.png',
						help = 'Specifies the name of the graph to produce')
	options = parser.parse_args()
	return options

quiet = False
graph = None
graphFlag = False

class Tester:
	def __init__(self, numTests = 0, testNames = [], testRoot = '/tests', graph = False):
		global quiet
		if not quiet:
			print('---------Initializing Tester---------')
		self.numTests = numTests
		self.passedTests = 0
		self.testNames = testNames
		self.profile = LearnerProfile.getProfile()
		LearnerProfile.setQuiet(quiet)

	def runTest(self, testRoot='/tests', testName=""):
		global quiet
		if not quiet:
			print('\n---> running test ' + testName)
		testFile = open(os.path.join(testRoot,testName), 'r')
		test = json.load(testFile)
		testFile.close()
		failed = False
		if 'multi-test' in test:
			for subTest in test['multi-test']:
				failed = failed or self.runTest(testRoot, subTest)
		# print('loaded JSON: ' + test)

		else:
			if test['test']['module'] == 'LearnerProfile':
				global quiet
				if not quiet:
					print(test['test']['function'])
				if test['test']['function'] == 'parseError':
					testSolution = test['problem']['solution']
					testAnswer = test['answer']

					solutionPoint = Sim.Point(testSolution['points'][0]['name'], testSolution['points'][0]['x'], testSolution['points'][0]['y'])

					answerPoint = Sim.Solution([], [Sim.Point(testAnswer['points'][0]['name'], testAnswer['points'][0]['x'], testAnswer['points'][0]['y'])])

					parsedSolution = Sim.Solution([], [solutionPoint])

					testProblem = Sim.Problem(test['problem']['id'], test['problem']['lines'], test['problem']['name'], test['problem']['points'], test['problem']['prompts'], test['problem']['text'], parsedSolution, test['problem']['text'])

					testAnswer = answerPoint
					self.profile.reset()
					if not quiet:
						print('Engaging module...')
					LearnerProfile.parseError(testProblem, testAnswer)

				elif test['test']['function'] == 'parseAnswer':
					testSolution = test['problem']['solution']
					testAnswer = test['answer']

					solutionPoint = Sim.Point(testSolution['points'][0]['name'], testSolution['points'][0]['x'],
					testSolution['points'][0]['y'])

					parsedSolution = Sim.Solution([], [solutionPoint])

					stepList = []
					for step in test['stepList']:
						stepList.append(Sim.Step(step['label'],step['name'],step['op']))

					testProblem = Sim.Problem(test['problem']['id'], test['problem']['lines'], test['problem']['name'], test['problem']['points'], test['problem']['prompts'], test['problem']['text'], parsedSolution, test['problem']['text'])
					LearnerProfile.parseAnswer(testProblem,stepList)

			for expected in test['test-expected']:
				if test['test-expected'][expected] == self.profile.getProblemStats(1).errorTracking[expected]:
					print("+ " + test['test-name'] + " passed!")
				else:
					if not failed:
						# print failure message once when first detected
						print("- " + test['test-name'] + " failed")
					failed = True
					# print values that have failed
					if not quiet:
						print("    given value: ",
						self.profile.ErrorTracking[expected],
						" for ", test['test-expected'])

		# jsonFile = open(os.path.join('profile_end_states','profile'+testName+'.json'), 'w')
		# json.dump(self.profile, jsonFile)
		# jsonFile.close()
		return failed

def logSim(logName, fileDirectory):
	global quiet, graphFlag
	if quiet:
		LearnerProfile.setQuiet(quiet)

	if logName == 'all':
		return allSim(fileDirectory)

	stepLists = LogReader.readLog(logName, fileDirectory)
	profile = LearnerProfile.getProfile()

	if graphFlag:
		profiles = []
		graphCount = 0

	profile.reset()
	user = stepLists[0]['user']
	stepListStore = []
	stepList = []
	# stepListDict is a dictionary containing
	# {problem, stepList, user, correct, line, timeStamp, statesList}

	for stepListDict in stepLists:
		if not user == stepListDict['user']:
			profile.updateAverage()
			print(user+'\'s Profile Average:')
			print(profile.average)
			print(user+'\'s Profile:\n')
			print(profile)
			user = stepListDict['user']

			if graphFlag:
				profiles.append((copy.deepcopy(profile), stepListDict['timeStamps'][-1]))
			stepListStore = []
			profile.reset()

		# we don't look at problem 540, it's just a trial problem with no answer
		if not int(stepListDict['problem'].id) == 540:
			# construct the new steplist with the old (only if we haven't)
			if not stepListStore:
				stepList = stepListDict['stepList']
				stepListStore = stepList
			else:
				# we've stored the stepList, we should just append the list
				stepList = stepListStore + stepListDict['stepList']
				# verbose
				# print('a[pended', stepListStore, stepListDict['stepList'], '\n to ', stepList)
				stepListStore = stepList

			LearnerProfile.updateTimeStamp(stepListDict['timeStamps'][-1])
			correct, answer = LearnerProfile.parseAnswer(stepListDict['problem'], stepList)
			if correct is not stepListDict['correct']:
				print('~~~answer did not match up with log data~~~')
				print('StepList: ', stepList, 'Problem: ', stepListDict['problem'], answer, 'line: ', stepListDict['line'])

			if stepListDict['correct']:
				# empty the stepLsit to match the log state
				stepListStore = []

			if graphFlag:
				profile.updateAverage()
				profiles.append((copy.deepcopy(profile), stepListDict['timeStamps'][-1]))

	profile.updateAverage()
	print(user+'\'s Profile Average:')
	print(profile.average)
	print(user+'\'s Profile:\n')
	print(profile)

	if graphFlag:
		profile.updateAverage()
		profiles.append((copy.deepcopy(profile), stepListDict['timeStamps'][-1]))
		Grapher.Graph(profiles, name=graphName, number=graphCount, title=user)
		graphCount += 1

# Perform slightly different analysis
# This analysis will perform lateral analysis on problems to figure out the
# common pitfalls
def allSim(fileDirectory):
	global quiet, graphFlag
	if quiet:
		LearnerProfile.setQuiet(quiet)

	stepLists = []
	# expect a tuple of (profile, timestamp, isFinal)
	profiles = []

	os.chdir(fileDirectory)
	logNames = os.listdir()
	os.chdir('..')

	for log in logNames:
		print(os.path.splitext(log)[0])
		stepLists.append((LogReader.readLog(log, fileDirectory), os.path.splitext(log)[0]))

	profile = LearnerProfile.getProfile()

	if graphFlag:
		graphCount = 0

	profile.reset()
	user = stepLists[0][1]
	condition = stepLists[0][0][0]['condition']
	profile.setID(user)
	stepListStore = []
	stepList = []

	os.chdir('test_results')
	result = open(user + '_' + condition + '.txt', 'w+')
	profileTimeData = {user:OrderedDict()}

	for group in stepLists:
		for stepListDict in group[0]:
			profile.cleanup()

			if not user == group[1]:
				profile.updateAverage()
				result.write(user+'\'s Profile average:\n')
				result.write(str(profile.average))
				result.write(user+'\'s Profile:\n')
				result.write(str(profile))
				user = group[1]

				profiles.append((copy.deepcopy(profile), stepListDict['timeStamps'][-1], True))
				stepListStore = []
				result.close()
				profile.reset()
				profile.setID(user)
				condition = stepListDict['condition']
				result = open(user + '_' + condition + '.txt', 'w+')

				print(user, condition)
				profileTimeData[user] = OrderedDict()

			# dont look at 540 - it's just a trial
			if not int(stepListDict['problem'].id) == 540:
				if not stepListStore:
					stepList = stepListDict['stepList']
					stepListStore = stepList
				else:
					stepList = stepListStore + stepListDict['stepList']
					# verbose
					# preint('appended', stepListStore, stepListDict['stepList'], '\n to ', stepList)
					StepListStore = stepList
				if not stepListDict['problem'].id in profileTimeData[user]:
					profileTimeData[user][stepListDict['problem'].id] = []

				LearnerProfile.updateTimeStamp(stepListDict['timeStamps'][-1])
				profileTimeData[user][stepListDict['problem'].id].append(stepListDict['timeStamps'])
				profile.setCondition(stepListDict['condition'])
				correct, answer = LearnerProfile.parseAnswer(stepListDict['problem'], stepList)

				if correct is not stepListDict['correct']:
					print('Mismatch! -', user, stepListDict['problem'].id)
					result.write('~~~answer did not match up with log data~~~\n')
					result.write('StepList: ' + str(stepList) + 'Problem: ' + str(stepListDict['problem'])+ ' =?= ' + str(answer) + 'line: ' + str(stepListDict['line']) + '\n')

				if stepListDict['correct']:
					stepListStore = []

				if graphFlag:
					profile.updateAverage()
					profiles.append((copy.deepcopy(profile), stepListDict['timeStamps'][-1], False))

	profiles.append((copy.deepcopy(profile), stepListDict['timeStamps'][-1], True))
	profile.updateAverage()
	profile.cleanup()
	result.write(user+'\'s Profile Average:\n')
	result.write(str(profile.average))
	result.write(user+'\'s Profile:\n')
	result.write(str(profile))
	result.close()


	# perform lateral analysis on Problems

	# get final states of profiles from profile, timestamp, isFinal tuple
	finalProfiles = []
	for profile in profiles:
		if profile[2]:
			finalProfiles.append(profile[0])

	problemAnalysis = {}
	conditionAnalysis = {}
	conditionAnalysis['total'] = {}

	totalConditionAnalysis = {}
	studentCount = {}

	studentCount['total'] = {}

	for profile in finalProfiles:
		for problem in profile.problems:
			if not profile.condition in studentCount:
				studentCount[profile.condition] = {}
				studentCount[profile.condition][problem.problemId] = 1
			elif not problem.problemId in studentCount[profile.condition]:
				studentCount[profile.condition][problem.problemId] = 1
			else:
				studentCount[profile.condition][problem.problemId] += 1
			if not problem.problemId in studentCount['total']:
				studentCount['total'][problem.problemId] = 1
			else:
				studentCount['total'][problem.problemId] += 1

			if problem.problemId in problemAnalysis:
				problemAnalysis[problem.problemId] = problemAnalysis[problem.problemId] + problem
			else:
				problemAnalysis[problem.problemId] = problem

			if profile.condition in conditionAnalysis:
				if problem.problemId in conditionAnalysis[profile.condition]:
					conditionAnalysis[profile.condition][problem.problemId] = conditionAnalysis[profile.condition][problem.problemId] + problem
				else:
					conditionAnalysis[profile.condition][problem.problemId] = problem
			else:
				conditionAnalysis[profile.condition] = {}
				conditionAnalysis[profile.condition][problem.problemId] = problem
			if not problem.problemId in conditionAnalysis['total']:
				conditionAnalysis['total'][problem.problemId] = problem
			else:
				conditionAnalysis['total'][problem.problemId] = conditionAnalysis['total'][problem.problemId] + problem

			if profile.condition in totalConditionAnalysis:
				totalConditionAnalysis[profile.condition] = totalConditionAnalysis[profile.condition] + problem
			else:
				totalConditionAnalysis[profile.condition] = problem

	analysisFile = open('problemAnalysis.txt', 'w+')
	for key in problemAnalysis:
		analysisFile.write(key+ ' analysis\n')
		analysisFile.write(str(problemAnalysis[key])+'\n')
	analysisFile.close()
	analysisFile = open('conditionAnalysis.txt', 'w+')
	for key in conditionAnalysis:
		analysisFile.write(key+' analysis\n')
		analysisFile.write(str(conditionAnalysis[key])+'\n')
	analysisFile.close()
	os.chdir('..')

	if graphFlag:
		Grapher.allGraph(finalProfiles, problemAnalysis, conditionAnalysis, totalConditionAnalysis, studentCount, profiles, profileTimeData)

if __name__ == '__main__':
	options = readCommands(sys.argv)
	print(options)
	global quiet, graphName, graphFlag, clean
	clean = True
	quiet = options.isQuiet
	graphFlag = False

	if options.graphName:
		graphName = options.graphName
		graphFlag = True

	if options.logFiles:
		for log in options.logFiles:
			logSim(log,options.testRoot)

	if options.names:
		tester = Tester(len(options.names), options.names)
		failed = tester.runTest(options.testRoot, options.names[0])

		if failed:
			print('\n----- NOT ALL TESTS PASSED -----')
		else:
			print('\n----- ALL TESTS PASSED -----')
