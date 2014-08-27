from __future__ import division
import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib as mlab


import random_data


for i in range(len(random_data.data_array)):
	x = random_data.fraction_array[i]
	y = random_data.data_array[i]
	colors = 0.1
	area = np.pi*(5)**2
	plt.scatter(x,y, s=area, c=colors, alpha = 0.5)

plt.show()

