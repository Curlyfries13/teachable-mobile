# Testing apparatus
# Written by Jonathan Yocky

# right now this will only test the LearnerProfile.
# later on it may become more generalized

import argparse
import sys
import json
import os
from abc import ABCMeta
import LearnerProfile
import SimulationObjects as Sim
import LogReader

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
						action = 'store')
	parser.add_argument('--log', '-l',
						dest = 'logFiles',
						nargs = '+')
	options = parser.parse_args()
	return options

quiet = False

class Tester:
	def __init__(self, numTests = 0, testNames = [], testRoot = '/tests'):
		global quiet
		if not quiet:
			print('---------Initializing Tester---------')
		self.numTests = numTests
		self.passedTests = 0
		self.testNames = testNames
		self.profile = LearnerProfile.getProfile()
		self.profile.setQuiet(quiet)

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
				if test['test-expected'][expected] == self.profile.ErrorTracking[expected]:
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
	stepLists = LogReader.readLog(logName,fileDirectory)
	profile = LearnerProfile.getProfile()
	profile.reset()
	user = ''
	stepListStore = []
	stepList = []
	# stepList pair is a tuple containing
	# {problem, stepList, user, correct, line}

	for stepListPair in stepLists:
		# print('stepListPair:', stepListPair[1])
		# print('ID -- ',stepListPair[0].id)
		if not user == stepListPair[2]:
			print(user+'\'s Profile:')
			# new session detected
			user = stepListPair[2]
			print(profile)
			profile.reset()
			stepListStore = []
		elif not int(stepListPair[0].id) == 540:
			# construct the new steplist with the old(only if we haven't)
			if not stepListStore:
				stepList = stepListPair[1]
				stepListStore = stepList
			else:
				# we've stored the stepList, we should just append the list
				stepList = stepListStore + stepListPair[1]
				# verbose
				# print('apended', stepListStore, stepListPair[1], '\n to ', stepList)
				stepListStore = stepList

			correct = LearnerProfile.parseAnswer(stepListPair[0], stepList)
			if correct is not stepListPair[3]:
				print('~~~answer did not match up with log data~~~')
				print('StepList: ', stepList, 'Problem: ', stepListPair[0], 'line: ', stepListPair[4])

			if stepListPair[3]:
				# empty the stepLsit to match the log state
				stepListStore = []

	print(user+'\'s Profile:')
	print(profile)

if __name__ == '__main__':
	options = readCommands(sys.argv)
	print(options)
	global quiet
	quiet = options.isQuiet
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