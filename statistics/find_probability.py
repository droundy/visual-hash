from __future__ import division
import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib as mlab

import random_data

new_random_array = np.zeros_like(random_data.data_array)
new_f_array = np.zeros_like(random_data.data_array)
new_prob = np.zeros_like(random_data.data_array)

'''
for i in range(len(random_data.data_array)):
	if random.random() >= random.random():
		new_random_array[i] = 1
	else:
		new_random_array[i] = 0
	new_f_array[i] = random.random()
	
print(new_random_array)
'''

new_random_array = random_data.data_array
new_f_array = random_data.fraction_array

q = .5
N = 6
A = .05

for i in range(len(random_data.data_array)):
	if new_random_array[i] == 1:
		new_prob[i] = random_data.P(new_f_array[i])
	else:
		new_prob[i] = 1-random_data.P(new_f_array[i])
		
print(new_prob)
total_prob = 1
for i in range(len(new_prob)):
	total_prob = total_prob*new_prob[i]
	
print(total_prob)		
