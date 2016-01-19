
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
	def __str__(self):
		string = []
		string.append(str(self.id))
		string.append(', ')
		string.append(str(self.solution))
		return ''.join(string)
	def __repr__(self):
		return str(self)

class Solution:
	def __init__(self, lines = [], points = []):
		self.lines = lines
		self.points = points
	def __str__(self):
		# expects only one point for the answer
		return(str(self.points[0]))

class Point:
	def __init__(self, name, x, y):
		self.name = name
		self.x = x
		self.y = y

	def __str__(self):
		string = []
		string.append(self.name)
		string.append(' (')
		string.append(str(self.x))
		string.append(', ')
		string.append(str(self.y))
		string.append(')')
		return ''.join(string)
	def __repr__(self):
		return(str(self))

class Step:
	def __init__(self,label,name,op,problemId=0,state=None):
		self.label = label
		self.name = name
		# print(op)
		self.op = op
		# to detect a specific bug
		self.problemId = problemId
		self.state = state

	def __str__(self):
		string = []
		string.append(self.label)
		return ''.join(string)

	def __repr__(self):
		return(str(self))

class Op:
	def __init__(self,distance,angle):
		self.distance = distance
		self.angle = angle

	# Note: biased to return distance; the two should not coexist!
	def __str__(self):
		if self.distance:
			return str(self.distance)
		if self.angle:
			return str(self.angle)

class Answer:
	def __init__(self,lines,points):
		self.lines = lines,
		self.points = points
	def __str__(self):
		return str(self.points)
	def __repr__(self):
		return str(self)
