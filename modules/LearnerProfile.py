# This is the class that holds data for the learner profiles
# given data, the model will update
# written by: Jon Yocky

import sys
import json

class LearnerProfile:

	def __init__(self):
		print "Initiating learner profile"
		# these probabilistic factors will be used to model the subject
		# start all measures at 0 (we don't know how the student will behave yet)
		self.xFirst = 0;
		self.yFirst = 0;

		self.inefficientCorrect = 0;
		# these should only work with problems that have negative values should use this
		self.movesReverse = 0;
		self.rotatesReverse = 0;

		self.correctProb = 0;

	def getValues(self):
		return json.dumps(self)

	def parsecorrect(self, inList):
		self.correctProb += 1

		print "Parsing!"
		# the list has the following format:
		# {name, label, op{}}

		'''
		the inList object is a series of steps, each with the form {name, label, op{}}

		name can have the values: moveDistance, turnAngle, or plotPoint

		label depends on the name
		moveDistance: "Move x" where x is the distance (positive or negative)
		turnAngle: "Turn t" where t is the angle
		plotPoint: "Plot Point"

		op depends on the name again but it contains an object
		moveDistance: 
			distance : x

		turnAngle:
			angle : t

		plotPoint:
			null (there is no object here)

		parsing the list will be the main source of information while parsing

		A list in this section will always have an entry which is plotPoint
		'''

		# we can search for any reverse movement, this should indicate whether the 
		# student uses negative values to move negatively

		# TODO: in the future we will look at the problem to see if a negative is
		# in the problem; if not then we won't use this as a metric
		for step in inList:
			if step.name == "moveDistance":
				if "-" in step.op.distance:
					self.movesReverse -= 1

		# if we have a correct solution with length 2 then it is optimized, this means
		# that the probelm is only on the x axis
		if len(inList) == 2:
			# this may not be a good measure since x would be the only direction
			self.xFirst += 1

		# if the solution has length 3, then the solution can be optimized for moving 
		# in the y direction only, or rotating instead of rotating to move negatively
		# or inefficiently in the x

		else if len(inList) == 3:
			if inList[0].name == "moveDistance":
				# in this case we know that the solution cannot be efficient the 
				# solution can only have moved in the x to be correct. There are not
				# moves in the step list to move away from the x axis, and plot the point 
				self.inefficientCorrect += 1

			else if inList[0].name == "turnAngle":
				# if the rotation is 360, we know the solution cannot be efficient
				# rotating 360 is a null move since it doesn't change state
				if inList[0].op.angle == "360":
					self.inefficientCorrect += 1

				# if the student turns 180, then they indicate that they will rotate
				# the robot around instead of moving backward (in this case the 
				# problem should only be in the x direction)
				if inList[0].op.angle == "180":
					self.rotatesReverse += 1

				# in this case the solution only uses the y direction and the student
				# must use one move to rotate. The next must be used to move in the 
				# y-direction and the last move must be plotting the point
				if inList[0].op.angle == "90" or inList[1].op.angle == "270":
					self.yFirst += 1
					if inList[1].name == "moveDistance":
						if "-" in inList[1].op.distance:
							# we know this movement is in the negative direction

		# This case can only be efficient if the first move is a movement followed
		# by a turn. In the case that we don't move first then we turn first.
		# If the user turns twice that is inefficient since turning twice could be
		# achieved in a single turn. After the first turn the student should move
		# to be efficient, however in this case 2 moves remain. Since we have two
		# moves (one must be plot) either the student moves redundantly or rotates
		# the first is inefficient, and the second doesn't change state
		else if len(inList) == 4:
			if inList[0].name == "turnAngle" and not inList[1].name == "turnAngle":
				# this is inefficient, see the paragraph above we can still get
				# data however we can still get some data on the student
				self.inefficientCorrect += 1

				if inList[0].op.angle == "90" or inList[0].op.angle == "270":
					self.yFirst += 1
				else:
					self.rotatesReverse += 1

			# here we know that the next move is a turnAngle
			else if inList[0].name == "turnAngle":
				self.inefficientCorrect += 1

			else:
				# first is a move, which must be in the x axis
				self.xFirst += 1
				# a second move is redundant (inefficient)
				if inList[1].name = "moveDistance":
					self.inefficientCorrect += 1

		# an efficient path requires rotating first. In the case that we don't
		# rotate first then we move, rotate move and still have two moves, one
		# which will be plotting the point. If we rotate first then move then
		# rotate then move, we can plot a point with x and y dimmensions 
		# efficiently
		else if len(inList) == 5:
			if inList[0].name == "turnAngle" and not inList[1].name == "turnAngle":
				if inList[0].op.angle == "90" or inList[0].op.angle == "270":
					self.yFirst += 1
				if inList[0].op.angle == "180" or inList[0].op.angle == "270":
					self.rotatesReverse += 1
			else:
				self.ineffientCorrect += 1

		# a bit more elaboration is needed here!
		else:
			self.inefficient += 1
