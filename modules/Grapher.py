import matplotlib.pyplot as plt
#import matplotlib.patches as mpatches
import numpy as np
import datetime
import os
from collections import OrderedDict
import LearnerProfile

def Graph(data, number, name='graph', title=''):

	MAX_RANGE = 10
	MIN_RANGE = -5
	# displaces chunks for the histogram based on width of individual
	# bars
	CHUNK_DISPLACE = 3
	BAR_RANGE = 100
	tableau20 = [(31,119,180), (174,199,232), (255,127,14), (255,187,120),
				 (44,160,44), (152,223,138), (214,39,40), (255,152,150),
				 (148,103,189), (197,176,213), (140,86,75), (196,156,148),
				 (227,119,194), (247, 182, 210), (127, 127, 127), (199,199,199),
				 (188,189,34), (219,219,141), (23,190,207), (158,218,229)]

	for i in range(len(tableau20)):
		r, g, b = tableau20[i]
		tableau20[i] = (r / 255., g / 255., b/255.)

	plt.figure(figsize=(12,9))

	start = data[0][1]
	end = data[-1][1]
	timeLength = (end - start).total_seconds()

	plt.ylim(MIN_RANGE,MAX_RANGE)
	plt.xlim(0, timeLength)

	plt.text(timeLength/2, MAX_RANGE+1, title, fontsize=24, color='k')

	profileData = []
	for metric in data[0][0].average.errorTracking:
		x = []
		y = []
		for profile in data:
			# print(profile[0].errorTracking)
			x.append((profile[1] - start).total_seconds())
			y.append(profile[0].average.errorTracking[metric])
		profileData.append([x,y,metric])
			# print('x = ', str((profile[1] - start).total_seconds()), '; y = ', str(profile[0].errorTracking[metric]) + '\n')
	for i, metric in enumerate(profileData):
		plt.plot(profileData[i][0],profileData[i][1], lw=1.0, color=tableau20[i])
		plt.text(timeLength + timeLength*.05, 10 - i, metric[2], fontsize=14, color=tableau20[i])

	plt.savefig(''.join(['graphs/',name,'_',str(number)]), bbox_inches = 'tight')
	plt.clf()

	# plot the problem statistics
	problemCount = len(data[-1][0].problems) + 0.0
	metricCount = len(data[-1][0].problems[0].errorTracking) + 0.0
	barWidth = BAR_RANGE / ((metricCount + CHUNK_DISPLACE) * problemCount * 1.0)
	groupWidth = (barWidth*metricCount + barWidth*CHUNK_DISPLACE)

	# print(problemCount,metricCount)
	plt.figure(figsize=(12,9))
	plt.ylim(MIN_RANGE, MAX_RANGE)
	plt.xlim(0, BAR_RANGE)

	plt.text(timeLength/2, MAX_RANGE+1, title, fontsize=24, color='k')
	problemStats = []

	for i, metric in enumerate(data[-1][0].problems[0].errorTracking):
		x = []
		y = []
		for j, problem in enumerate(data[-1][0].problems):
			x.append((j*groupWidth + i*barWidth))
			y.append(problem.errorTracking[metric])

		problemStats.append([x,y,problem.problemId])

	for i in range(0, int(problemCount)):
		# print('generating text',  problemCount)
		plt.text((groupWidth * i) + (groupWidth / 2), MIN_RANGE - 1, data[-1][0].problems[i].problemId)

	ax = plt.subplot(111)
	ax.set_xticklabels([])
	col = 0

	# print('creating graph')
	for stat in problemStats:
		ax.bar(stat[0], stat[1], width=barWidth, color=tableau20[col], align='center')
		col += 1
		if col > metricCount:
			col = 0

	# create legend
	for i, metric in enumerate(data[-1][0].problems[0].errorTracking):
		ax.text(BAR_RANGE + 2, MAX_RANGE - (i * .5), metric, color = tableau20[i], fontsize = 14)

	plt.savefig(''.join(['graphs/',name,'_bar']))
	plt.clf()
	plt.close()
	return

# graph data from all profiles: we'll need to be smart
def allGraph(profiles, problemAnalysis, conditionAnalysis, totalConditionAnalysis, studentCount, rawProfiles, timeData):
	print('Graphing all')
	MAX_RANGE_OFF = 10
	MIN_RANGE_OFF = -5
	MAX_RANGE_OTHER = 10
	MIN_RANGE_OTHER = -5
	WIGGLE = .05

	PRB_MIN_RANGE = 0
	PRB_MAX_RANGE = 16
	barWidth = 2
	# displaces chunks for the histogram based on width of individual
	# bars
	CHUNK_DISPLACE = 3
	BAR_RANGE = 100
	tableau20 = [(31,119,180), (174,199,232), (255,127,14), (255,187,120),
				 (44,160,44), (152,223,138), (214,39,40), (255,152,150),
				 (148,103,189), (197,176,213), (140,86,75), (196,156,148),
				 (227,119,194), (247, 182, 210), (127, 127, 127), (199,199,199),
				 (188,189,34), (219,219,141), (23,190,207), (158,218,229)]

	PLOT_ORDER = ['offByNx', 'offByNy', 'offByNxMag', 'offByNyMag', 'offByNxChir', 'offByNyChir', 'offByCount']
	OTHER_ORDER = ['attempts', 'correctProb','sumError', 'ignoreX', 'ignoreY', 'flippingError', 'noPlot', 'offByCount', 'invertX', 'invertY']
	LATERAL_ANALYSIS = ['correctProb', 'sumError', 'ignoreX', 'ignoreY', 'flippingError', 'noPlot', 'offByCount', 'invertX', 'invertY','deleteMoves']

	for i in range(len(tableau20)):
		r, g, b = tableau20[i]
		tableau20[i] = (r / 255., g / 255., b/255.)

	# create lateral problem analysis graphs
	if not os.path.exists('graphs'):
		os.makedirs('graphs')
	if not os.path.exists('graphs/problemAnalysis'):
		os.makedirs('graphs/problemAnalysis')
	if not os.path.exists('graphs/conditionAnalysis'):
		os.makedirs('graphs/conditionAnalysis')
	os.chdir('graphs/problemAnalysis')

	for problemId, problem in problemAnalysis.items():
		plt.figure(figsize=(12,9))
		plt.xlim(PRB_MIN_RANGE, len(problem.errorTracking)+2)
		problemSum = 0

		for condition in studentCount:
			if problemId in studentCount[condition]:
				problemSum += studentCount[condition][problemId]

		# print(problemSum)
		ax = plt.subplot(111)
		ax.spines["top"].set_visible(False)
		ax.spines["right"].set_visible(False)

		ax.get_yaxis().tick_left()

		plt.xticks(visible=False)
		plt.yticks(fontsize=14)

		legend = OrderedDict()
		attempts = problem.errorTracking['attempts']
		correct = problem.errorTracking['correctProb']
		incorrect = attempts - correct

		if attempts == correct:
			attempts += 1
		for index, error in enumerate(problem.errorTracking.items()):
			if error[0] == 'correctProb':
				legend[('incorrect', incorrect)] = ax.bar(index + 1, incorrect/problemSum, 1, color = tableau20[index])
			elif error[0] in LATERAL_ANALYSIS:
				legend[error] = ax.bar(index + 1, error[1]/problemSum, 1, color=tableau20[index])
		plt.title( problemId +' lateral Analysis', fontsize=24, color='k')

		# create legend
		# for i, metric in enumerate(problem.errorTracking):
		# 	ax.text(len(problem.errorTracking)+2, float((ymax)-(ymax-ymin)*.03*i), metric, color=tableau20[i], fontsize = 14)

		plt.legend(list(legend.values()), list(legend.keys()))
		plt.savefig(''.join(['error_analysis/',problemId,'analysis.png']))
		plt.close()

		# create behavior graph
		plt.figure(figsize=(12,9))
		ax = plt.subplot(111)

		ax.spines['top'].set_visible(False)
		ax.spines['right'].set_visible(False)

		ax.get_yaxis().tick_left()

		plt.yticks(fontsize=14)
		plt.xticks(visible=False)

		ydata = problem.behaviors.values()
		bars = ax.bar(range(0,len(ydata)), ydata, color=tableau20, width=barWidth)
		plt.title( problemId + ' behavior Analysis', fontsize=24, color='k')

		x_range = plt.axis()[1] - plt.axis()[0]
		x_max = plt.axis()[1]
		plt.xlim(xmax = x_max + x_range*.3)

		plt.legend(bars, list(problem.behaviors.keys()))
		ax.set_ylabel('Count/sessions')

		plt.savefig(''.join(['behaviors/' ,problemId, 'behaviors.png']))
		plt.clf()
		plt.close()

		print('Problem ', problemId, ' analysis completed')
	os.chdir('..')


	# create lateral condition/Problem analysis Graphs
	conditionStats = {}
	conditionStats['total'] = {}
	legendColor = {}
	for condition, problems in conditionAnalysis.items():
		conditionStats[condition] = {}
		keys = sorted(problems.keys())
		for index, error in enumerate(problems[keys[0]].errorTracking.items()):
			conditionStats[condition][error[0]] = []
			legendColor[error[0]] = index
			if not error[0] in conditionStats[condition]:
				conditionStats[condition][error[0]] = [0.0]*len(keys)

			for index, key in enumerate(keys):
				conditionStats[condition][error[0]].append((problems[key].errorTracking[error[0]] * 1.0)/studentCount[condition][key])


		for problemId, problem in problems.items():
			if condition in studentCount and problemId in studentCount[condition]:
				userCount = studentCount[condition][problemId]
			else:
				continue
			plt.figure(figsize=(12,9))
			ax = plt.subplot(111)
			legend = OrderedDict()

			ax.spines["top"].set_visible(False)
			ax.spines["right"].set_visible(False)
			ax.get_yaxis().tick_left()

			plt.xticks(visible=False)
			plt.yticks(fontsize=14)
			attempts = problem.errorTracking['attempts']
			correct = problem.errorTracking['correctProb']
			incorrect = attempts - correct
			# avoid divide by 0
			if attempts == correct:
				attempts += 1
			for index, error in enumerate(problem.errorTracking.items()):
				if error[0] == 'correctProb':
					legend[('incorrect', incorrect)] = ax.bar(index + 1, incorrect/userCount, 1, color = tableau20[index])
				elif error[0] in LATERAL_ANALYSIS:
					legend[error] = ax.bar(index + 1, error[1]/userCount, 1, color=tableau20[index])
			plt.title(condition + problemId +' condition Analysis', fontsize=24, color='k')

			plt.legend(list(legend.values()), list(legend.keys()))
			plt.ylabel('Count/User Session')
			plt.xlabel('Problem')
			if(condition is ''):
				condition = 'None'
			plt.savefig(''.join(['conditionAnalysis/all/', problemId, '_', condition, '.png']))
			plt.savefig(''.join(['conditionAnalysis/', condition, '/', problemId, '_', condition, '.png']))
			plt.savefig(''.join(['conditionAnalysis/Problems/', problemId, '/', problemId, '_', condition, '.png']))
			print(problemId, '/', condition, 'analysis complete')
			plt.close()

	# check conditions over all sessions
	for condition, stats in conditionStats.items():
		plt.figure(figsize=(12,9))
		ax = plt.subplot(111)
		legend = OrderedDict()

		ax.spines["top"].set_visible(False)
		ax.spines["right"].set_visible(False)
		ax.get_yaxis().tick_left()


		plt.yticks(fontsize=14)
		for error, data in stats.items():
			if error in LATERAL_ANALYSIS:
				if error == 'correctProb':
					incorrect = [attempts - correct for attempts, correct in zip(stats['attempts'], data)]
					legend['incorrect'] = plt.plot(range(1, 1+len(incorrect)), incorrect, marker='.', color=tableau20[int(legendColor[error])], label='incorrect')
				else:
					plt.plot(range(1, 1+len(data)), data, marker='.', color=tableau20[int(legendColor[error])], label=str(error))

		plt.title(condition + ' Session Analysis', fontsize=24, color='k')

		plt.ylabel('Count/User Session')
		plt.legend()
		plt.show()
		# plt.legend(list(legend.values()), list(legend.keys()))

		if(condition is ''):
			condition = 'None'
		plt.savefig(''.join(['conditionAnalysis/Session/', condition, '_scatter', '.png']))
		plt.close()
		print(condition, 'session analysis complete')



	# Create overall condition graphs - i.e. errors in all problems for all sessinos in a condition
	for condition, data in totalConditionAnalysis.items():
		sessionCount = studentCount[condition]['541']
		plt.figure(figsize=(12,9))
		ax = plt.subplot(111)
		legend = OrderedDict()

		ax.spines["top"].set_visible(False)
		ax.spines["right"].set_visible(False)
		ax.get_yaxis().tick_left()
		print(data)
		plt.xticks(visible=False)
		plt.yticks(fontsize=14)
		attempts = data.errorTracking['attempts']
		correct = data.errorTracking['correctProb']
		incorrect = attempts - correct
		print(incorrect)
		# avoid divide by 0
		if attempts == correct:
			attempts += 1
		for index, error in enumerate(data.errorTracking.items()):
			if error[0] == 'correctProb':
				legend[('incorrect', incorrect)] = ax.bar(index + 1, incorrect/sessionCount, 1, color = tableau20[index])
			elif error[0] in LATERAL_ANALYSIS:
				legend[error] = ax.bar(index + 1, error[1]/sessionCount, 1, color=tableau20[index])
		plt.title(condition + ' Total condition Analysis', fontsize=24, color='k')

		plt.legend(list(legend.values()), list(legend.keys()))
		plt.ylabel('Count')
		if(condition is ''):
			condition = 'None'
		plt.savefig(''.join(['conditionAnalysis/Session/', condition, '_bar', '.png']))
		plt.close()
		print(condition, 'error graphs created')
	# now create profile graphs

	# print(profiles[0][0].problems[-1])
	print('Problem Analysis Graphs Complete.')

	# Profile analysis graphs
	for profile in profiles:
		if(len(profile.problems) == 0):
			continue

		profileOffByData = {}
		profileOtherData = {}
		# dictionary storage for easy access
		profileCorrectnessData = {}
		profileAttemptData = {}
		# get all the data into useful groups
		for i, metric in enumerate(profile.problems[-1].errorTracking):
			for problem in profile.problems:
				if metric in PLOT_ORDER:
					if metric in profileOffByData:
						profileOffByData[metric].append((problem.problemId, problem.errorTracking[metric]))
					else:
						profileOffByData[metric] = [(problem.problemId, problem.errorTracking[metric])]
				if metric in OTHER_ORDER:
					if metric in profileOtherData:
						profileOtherData[metric].append((problem.problemId, problem.errorTracking[metric]))
					else:
						profileOtherData[metric] = [(problem.problemId, problem.errorTracking[metric])]

				if metric == 'correct':
					profileCorrectnessData[problem.problemId] = problem.errorTracking[metric]
				elif metric == 'attempts':
					profileCorrectnessData[problem.problemId] = problem.errorTracking[metric]

		sortedOffBy = OrderedDict()
		sortedOther = OrderedDict()

		for metric in OTHER_ORDER:
			sortedOther[metric] = OrderedDict(sorted(profileOtherData[metric], key=lambda id: int(id[0])))
		for metric in PLOT_ORDER:
			sortedOffBy[metric] = OrderedDict(sorted(profileOffByData[metric], key=lambda id: int(id[0])))

		problemCount = len(profile.problems)
		# groupSize = len(PLOT_ORDER)*barWidth + CHUNK_DISPLACE
		# tickPlacement = np.arange(CHUNK_DISPLACE + groupSize *.5, CHUNK_DISPLACE + groupSize*.5 + groupSize*problemCount, groupSize)
		tickLabels = map(lambda x: str(int(x.problemId)-540), profile.problems)

		plt.figure(figsize=(12,9))
		plt.autoscale(enable=True, axis='y', tight=False)

		ax = plt.subplot(211)
		stat_legend = OrderedDict()
		index = np.arange(0, len(OTHER_ORDER)*barWidth*len(profile.problems) + CHUNK_DISPLACE*len(profile.problems), len(OTHER_ORDER)*barWidth + CHUNK_DISPLACE)
		labelLoc = np.arange(len(OTHER_ORDER)*barWidth/2.0, len(OTHER_ORDER)*barWidth*len(profile.problems) + CHUNK_DISPLACE*len(profile.problems), len(OTHER_ORDER)*barWidth + CHUNK_DISPLACE )

		for i, statTup in enumerate(sortedOther.items()):
			stat_legend[statTup[0]] = ax.bar(index + (barWidth * i), statTup[1].values(), barWidth, color=tableau20[i])

		x_range = plt.axis()[1] - plt.axis()[0]
		x_max = plt.axis()[1]
		ax.set_xticks(labelLoc)
		ax.set_xticklabels(tickLabels)
		plt.xlim(xmax = x_max + x_range*.25)

		# create legend
		plt.legend(list(stat_legend.values()), list(stat_legend.keys()))
		plt.xlabel('Problem', labelpad=25)
		plt.ylabel('Count')
		plt.title(''.join(['subject ', profile.subjectID, ' ', profile.condition , ' Errors']))

		plt.savefig(''.join(['profileAnalysis/other/', str(profile.subjectID), '_', profile.condition, '_other']), bbox_inches='tight')
		plt.clf()
		plt.close()

		# off By plot
		plt.figure(figsize=(12,9))
		plt.autoscale(enable=True, axis='y', tight=False)

		ax = plt.subplot(211)

		stat_legend = OrderedDict()
		index = np.arange(0, len(PLOT_ORDER)*barWidth*len(profile.problems) + CHUNK_DISPLACE*len(profile.problems), len(PLOT_ORDER)*barWidth + CHUNK_DISPLACE)
		labelLoc = np.arange(len(PLOT_ORDER)*barWidth/2.0, len(PLOT_ORDER)*barWidth*len(profile.problems) + CHUNK_DISPLACE*len(profile.problems), len(OTHER_ORDER)*barWidth + CHUNK_DISPLACE)

		for i, statTup in enumerate(sortedOffBy.items()):
			stat_legend[statTup[0]] = ax.bar(index + (barWidth * i), statTup[1].values(), barWidth, color=tableau20[i])

		x_range = plt.axis()[1] - plt.axis()[0]
		x_max = plt.axis()[1]
		ax.set_xticks(labelLoc)
		ax.set_xticklabels(tickLabels)
		plt.xlim(xmax = x_max + x_range*.25)
		# plt.xticks(index + barWidth, tickLabels)
		# create legend
		plt.legend(list(stat_legend.values()), list(stat_legend.keys()))
		plt.xlabel('Problem', labelpad=25)
		plt.ylabel('Count')
		plt.title(''.join(['subject', profile.subjectID, ' ', profile.condition , ' Off-By errors']))

		plt.savefig(''.join(['profileAnalysis/offBy/', str(profile.subjectID), '_', profile.condition, '_offBy']), bbox_inches='tight')
		plt.clf()
		plt.close()

		# time analysis
		timeData[profile.subjectID]
		print('Profile ', profile.subjectID, ' completed')
		plt.clf()
		plt.close()
	print ('All graph complete')
	return
