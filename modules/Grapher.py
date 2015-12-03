import matplotlib.pyplot as plt
import datetime

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
	return
