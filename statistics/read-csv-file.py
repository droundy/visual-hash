#!/usr/bin/python

import csv, numpy
import matplotlib.pyplot as plt

datetime = {}
epochtime = {}
time_thinking = {}
f_values = {}
user_says_changed = {}
actually_changed = {}
perceptual_difference = {}

with open('pairs.csv', 'rb') as csvfile:
    spamreader = csv.reader(csvfile, skipinitialspace=True)
    oldtime = 0
    for row in spamreader:
        hashtype = row[2]

        if not hashtype in datetime:
            datetime[hashtype] = []
        datetime[hashtype].append(row[0])

        if not hashtype in epochtime:
            epochtime[hashtype] = []
        epochtime[hashtype].append(float(row[1]))

        if not hashtype in time_thinking:
            time_thinking[hashtype] = []
        time_thinking[hashtype].append(float(row[1]) - oldtime)
        oldtime = float(row[1])

        if not hashtype in f_values:
            f_values[hashtype] = []
        f_values[hashtype].append(float(row[3]))

        if not hashtype in user_says_changed:
            user_says_changed[hashtype] = []
        user_says_changed[hashtype].append(int(row[4]))

        if not hashtype in actually_changed:
            actually_changed[hashtype] = []
        actually_changed[hashtype].append(int(row[5]))

        if not hashtype in perceptual_difference:
            perceptual_difference[hashtype] = []
        perceptual_difference[hashtype].append(float(row[6]))


for hashtype in datetime.keys():
    f_values[hashtype] = numpy.array(f_values[hashtype])
    perceptual_difference[hashtype] = numpy.array(perceptual_difference[hashtype])
    time_thinking[hashtype] = numpy.array(time_thinking[hashtype])

    user_says_changed[hashtype] = numpy.array(user_says_changed[hashtype])
    actually_changed[hashtype] = numpy.array(actually_changed[hashtype])
    #print hashtype, 'datetime', datetime[hashtype]
    #print hashtype, 'perceptual_difference', perceptual_difference[hashtype]
    #print hashtype, 'time_thinking', time_thinking[hashtype]

#plt.plot(f_values['fractal'], user_says_changed['fractal'] - actually_changed['fractal'], 'o')

#plt.show()
