import matplotlib.pyplot as plt

from os import listdir
from os.path import isfile, join
import sys

import copy


def fToL(filename):

	with open(filename, 'r') as f:
		string = f.readline()

	list = string[1:len(string)-1].split(',')
	return [float(x) for x in list]


def filesInDir(dir):
	return [join(dir,f) for f in listdir(dir) if isfile(join(dir, f))]


def getAllData(dir):

	data = []
	for f in filesInDir(dir):
		data.extend(fToL(f))

	return data


def lToLoops(l):

	loops = [1 if x>=100 else (-1 if x<=-100 else 0) for x in l]

	for i in range(1,len(loops)):
		loops[i] += loops[i-1]
	return loops

def cumReward(l):

	r = copy.deepcopy(l)

	for i in range(1,len(r)):
		r[i] += r[i-1]
	return r


def plotLoops(loop):
	
	plt.plot(list(range(len(loop))), loop) 


if __name__ == '__main__':
	
	data = getAllData(sys.argv[1])
	loops = lToLoops(data)
	cr = cumReward(data)

	plotLoops(cr)
	plt.grid()
	plt.savefig(sys.argv[2]+"_r.png", dpi=900)

	plt.clf()

	plotLoops(loops)
	plt.grid()
	plt.savefig(sys.argv[2]+"_l.png", dpi=900)
