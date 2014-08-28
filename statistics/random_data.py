from __future__ import division
import numpy as np
import random



hash_comparisons = int(500)

fraction_array = np.zeros(hash_comparisons)

for i in range(hash_comparisons):
	fraction_array[i] = random.random()
	
fraction_array=sorted(fraction_array)	



q = float(.5)
N = float(6)
A = float(.05)

def P(f):
	return ((1-f+f*q)**N)*(1-A)


data_array = np.zeros_like(fraction_array)

for i in range(len(data_array)):
	if random.random() >= P(fraction_array[i]):
		data_array[i] = 1
	else:
		data_array[i] = 0

