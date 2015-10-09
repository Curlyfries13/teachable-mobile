# Testing apparatus
# Written by Jonathan Yocky

# right now this will only test the LearnerProfile.
# later on it may become more generalized

import argparse
import sys
import json
import os
import LearnerProfile

def readCommands(argv):
	parser =  argparse.ArgumentParser(description='Prepare testing apparatus')
	parser.add_argument('--test-names', '-n',
						metavar='xyz.test',
						dest = 'names',
						nargs='+',
						action = 'store',
						help='run particular tests'
						)
	parser.add_argument('--quiet', '--shh', '--silent' , '-q',
						dest = 'isQuiet',
						action = 'store_false',
						help = 'Tester will run without input (quietly)'
						)
	parser.add_argument('--test_directory', '-dir',
						default = 'tests',
						dest = 'testRoot',
						action = 'store')
	options = parser.parse_args()
	return options

def readTest(testFile):
	test = json.load(testFile)
	return test

class Tester:
	def __init__(self, numTests = 0, testNames = [], testRoot = '/tests'):
		print('---------Initializing Tester---------')
		self.numTests = numTests
		self.passedTests = 0
		self.testNames = testNames
		self.profile = LearnerProfile.getProfile()

	def run():
		failed = False
		for test in testNames:
			failed = runTest or failed

		if failed:
			print('----- NOT ALL TESTS PASSED -----')

	def runTest(self, testRoot='/tests', testName=""):
		print('\n---> running test ' + testName)
		testFile = open(os.path.join(testRoot,testName), 'r')
		test = readTest(testFile)
		testFile.close()
		failed = False

		# print('loaded JSON: ' + test)
		print(test['test']['module'])
		if test['test']['module'] == 'LearnerProfile':

			print(test['test']['function'])
			if test['test']['function'] == 'parseError':
				testSolution = test['problem']['solution']
				testAnswer = test['answer']

				solutionPoint = Point(testSolution['points'][0]['name'], testSolution['points'][0]['x'], testSolution['points'][0]['y'])

				answerPoint = Solution([], [Point(testAnswer['points'][0]['name'], testAnswer['points'][0]['x'], testAnswer['points'][0]['y'])])

				parsedSolution = Solution([], [solutionPoint])

				testProblem = Problem(test['problem']['id'], test['problem']['lines'], test['problem']['name'], test['problem']['points'], test['problem']['prompts'], test['problem']['text'], parsedSolution, test['problem']['text'])

				testAnswer = answerPoint
				self.profile.reset()
				print('Engaging module...')
				LearnerProfile.parseError(testProblem, testAnswer)

		if 'flippingError' in test['test-expected']:
			if test['test-expected']['flippingError'] == self.profile.flippingError:
				print('Flipping Error Passed!')
			else:
				failed = True
				print('Flipping Error Failed!')
		elif 'sumError' in test['test-expected']:
			if test['test-expected']['sumError'] == self.profile.sumError:
				print('Sum Error Passed!')
			else:
				failed = True
				print('Sum Error Failed')
				print (self.profile.sumError)

		# jsonFile = open(os.path.join('profile_end_states','profile'+testName+'.json'), 'w')
		# json.dump(self.profile, jsonFile)
		# jsonFile.close()
		return failed

class Problem:
	def __init__(self, probId, lines = [], name = 'test', points = [], problemType = 'plot', prompts = [], solution = None, text = '', probType = 'Default'):
		self.id = probId
		self.lines = lines
		self.name = name
		self.points = points
		self.prompts = prompts
		self.solution = solution
		self.text = text
		self.type= probType

class Solution:
	def __init__(self, lines = [], points = []):
		self.lines = lines
		self.points = points

class Point:
	def __init__(self, name, x, y):
		self.name = name
		self.x = x
		self.y = y

if __name__ == '__main__':
	options = readCommands(sys.argv)
	print(options)
	tester = Tester(len(options.names), options.names)
	tester.runTest(options.testRoot, options.names[0])
