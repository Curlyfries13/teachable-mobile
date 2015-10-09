# web controller for learner profiles
# written by Jon Yocky

from LearnerProfile import LearnerProfile
import urllib
import json

lp = LearnerProfile()

def init_learnerProfile():
	lp = LearnerProfile()

def index():
	# print "reached learner profile index"
	return dict(learnerProfile = lp)

def update_profile():

	if not lp:
		init_learnerProfile()

	# print "update profile!"
	# print "vars: "

	for element in request.vars:
		print element

	# print "all vars done"
	print request.vars['stepList']
	if 'stepList' in request.vars:
		# DEBUG
		print(stepList, problemObj)
		lp.parseStepList(request.vars['stepList'],request.vars['problemObj'])

		# Seperation of concerns here: OLD CODE
		# if 'correct' in request.vars and request.vars['correct'] == 'true':
		# 	# print request.vars['data']
		# 	stepList = json.loads(request.vars['stepList'])
		# 	problemObj = json.loads(request.vars['problemObj'])
		# 	# print steplist
		# 	lp.parseCorrect(stepList,problemObj)
		# elif 'correct' in request.vars and request.vars['correct'] == 'false':
		# 	stepList = json.loads(request.vars['stepList'])
		# 	problemObj = json.loads(request.vars['problemObj'])
		# 	answerObj = json.loads(request.vars['data'])
		# 	lp.parseIncorrect(stepList, problemObj, answerObj)
	else:
		print "no data sent"

def update_problem_status():
	# not implemented
	if not lp:
		init_learnerProfile()

def update_action_status():
	# not implemented!
	return None


# def return_profile():

# def import_profile():
	# TODO something here

# def save_pofile():
