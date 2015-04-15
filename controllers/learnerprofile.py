# web controller for learner profiles
# written by Jon Yocky

from LearnerProfile import LearnerProfile
import urllib
import json

lp = LearnerProfile()

def init_learnerProfile():
	# TODO Jon don't let the profile get instantiated multiple times!
	lp = LearnerProfile()

def index():
	# print "reached learner profile index"
	return dict(learnerProfile = lp)

def update_profile():

	if(not lp):
		init_learnerProfile()
	# TODO Jon dobule check the profile exists

	# print "update profile!"
	# print "vars: "

	for element in request.vars:
		print element

	# print "all vars done"
	print request.vars['stepList']
	if 'stepList' in request.vars:
		if 'correct' in request.vars and request.vars['correct'] == 'true':
			# print request.vars['data']
			stepList = json.loads(request.vars['stepList'])
			problemObj = json.loads(request.vars['problemObj'])
			# print steplist
			lp.parseCorrect(stepList,problemObj)
		elif 'correct' in request.vars and request.vars['correct'] == 'false':
			stepList = json.loads(request.vars['stepList'])
			problemObj = json.loads(request.vars['problemObj'])
			answerObj = json.loads(request.vars['data'])
			lp.parseIncorrect(stepList, problemObj, answerObj)
	else:
		print "no data sent"

# def return_profile():

# def import_profile():
	# TODO something here

# def save_pofile():
