import numpy
import random
import math
fs = numpy.array([0, 0.5, 1])

fs = numpy.append(fs, float(.45))
fs = numpy.append(fs, float(.35))
for i in range(100):

	sort_fs = sorted(fs)

	largest_gap = 0
	track = 0
	gap = numpy.zeros(len(fs)+1)

	for i in range(len(fs)+1):
		if i == 0:
			gap[i] = sort_fs[i]
			if sort_fs[i] <= .5001 :
				largest_gap = 1-gap[i]
				
			else:
				largest_gap = gap[i]
		elif i == len(fs):
			gap[i] = 1-sort_fs[i-1]
			if gap[i] >= gap[i-1]:
				largest_gap = gap[i]
				track = i
			else: 
				largest_gap = largest_gap
			
		else:
			gap[i] = sort_fs[i] - sort_fs[i-1]
			if gap[i] >= gap[i-1]:
				largest_gap = gap[i]
				track = i
			else:
				largest_gap = largest_gap
	print largest_gap,"lg"
	print track, "track"
	print sort_fs[track], sort_fs[track-1]

		
	window = sort_fs[track] - sort_fs[track-1]
	mu = sort_fs[track-1] + window/2
	sigma = .25
	scale = .3

	while True:
		r1 = random.random()

		def new_f(r1):
			return scale*(1/(sigma*((2*math.pi)**.5)))*(math.exp((-(r1-mu)**2)/(2*sigma**2)))
			
		r2 = random.random()

		if r2 <= new_f(r1):
			new_fs = r1
			break
		else:
			"do nothing"

	#print new_fs, "new fs"
	#print sort_fs
	fs = numpy.append(fs, new_fs)
