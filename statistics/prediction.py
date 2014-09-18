from __future__ import division
import numpy as np
import numpy.random as random

"""The goal of this program is to create a function that can predict
H, N, and A from data set. The next goal would be to use the H, N, and
A information to select the next reasonable f value."""

"""The data set would include the f value and the corresponidng 1 or 0,
which is derived from the P(f) function."""

#insert data consisiting of (f,1 or 0)
#
import random_data

data_set = random_data.combined_data

"""options:
1. pick reasonable guesses for H,N,A and run the P(f) program with the 
same f as in data and see how close the resulting data is. Change H,N, A
to get closer results. Pros: easy to start. Cons: hard to finish.

The random numbers bieng used each time to generate the data make it
very difficult to see any patterns correlating to H,N, or A. Feels like 
a catch 22.
 """
