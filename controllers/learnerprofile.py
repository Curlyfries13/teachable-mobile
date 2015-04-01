# web controller for learner profiles
# written by Jon Yocky

from LearnerProfile import LearnerProfile
import urllib
import json

lp = LearnerProfile()

def index():
	print "reached learner profile index"

def update_profile():
	# TODO dobule check the profile exists	

	# print "update profile!"
	# print "vars: "

	for element in request.vars:
		print element

	# print "all vars done"
	print request.vars['data']
	if 'data' in request.vars:
		if 'correct' in request.vars and request.vars['correct'] == 'true':
			# print request.vars['data']
			stepList = json.loads(request.vars['data'])
			# print steplist
			lp.parseCorrect(stepList)
		elif 'correct' in request.vars and request.vars['correct'] == 'false':
			print "incorrect not implemented yet"
	else:
		print "no data sent"

# def return_profile():