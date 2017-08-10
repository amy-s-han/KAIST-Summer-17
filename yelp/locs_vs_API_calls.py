#!/usr/bin/python

# Amy Han - Summer 2017 - KIXLAB

import matplotlib.pyplot as plt
from matplotlib import cm
from numpy import linspace

city = "seattleData/"


# for color in ['red', 'green', 'blue']:
#     n = 750
#     x, y = rand(2, n)
#     scale = 200.0 * rand(n)
#     ax.scatter(x, y, c=color, s=scale, label=color,
#                alpha=0.3, edgecolors='none')

# ax.legend()
# ax.grid(True)

# plt.show()

def main():

	statsFile = city + "stats.txt"
	fh = open(statsFile, 'r')

	fig, ax = plt.subplots()

	locs = []
	calls = []

	for line in fh:
		print line
		line = line.split()
		locs.append(line[1])
		calls.append(line[2])
	
	fh.close()

	start = 0.0
	stop = 1.0
	number_of_lines= len(locs)
	cm_subsection = linspace(start, stop, number_of_lines) 

	colors = [ cm.jet(x) for x in cm_subsection ]

	for i, color in enumerate(colors):
		ax.scatter(locs[i], calls[i], alpha=0.3, edgecolors='none', color=color)	

	
	ax.grid(True)

	plt.show()


if __name__ == "__main__":
    main()