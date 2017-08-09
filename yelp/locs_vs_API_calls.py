#!/usr/bin/python

# Amy Han - Summer 2017 - KIXLAB

import matplotlib.pyplot as plt

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

	for line in fh:
		print line
		line = line.split()
		x = line[1]
		y = line[2]

		ax.scatter(x, y, alpha=0.3, edgecolors='none')	

	fh.close()
	
	ax.grid(True)

	plt.show()


if __name__ == "__main__":
    main()