from __future__ import division
import numpy as np
import random



hash_comparisons = int(50)

fraction_array = np.zeros(hash_comparisons)

for i in range(hash_comparisons):
	fraction_array[i] = random.random()
	
fraction_array=sorted(fraction_array)	



H = float(20)
N = float(3)
A = float(.1)

def P(f):
	return ((1-f+f*(2**(-H/N)))**N)*(1-A)


data_array = np.zeros_like(fraction_array)

for i in range(len(data_array)):
	if random.random() >= P(fraction_array[i]):
		data_array[i] = 1
	else:
		data_array[i] = 0

#print data_array

combined_data  = np.zeros((hash_comparisons, 2))

for i in range(len(combined_data)):
	combined_data[i,0] = fraction_array[i]
	combined_data[i,1] = data_array[i]
	
print combined_data
