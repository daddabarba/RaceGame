from ast import literal_eval as make_tuple
import matplotlib.pyplot as plt

import numpy as np

import sys
import os

FOL = os.getcwd()

def getData(fol, i):

	filename = fol+"/im_data_serv_" + str(i) + "_0"
	print("Extracting " + filename + " ...", end="")
	if not os.path.isfile(filename):
		print(" not found")
		return None

	with open(filename) as f:
		string = f.readline()
	print("converting to tuple")
	return make_tuple(string)

def loopify(data):

	loops = [1 if x>=100 else (-1 if x<=-100 else 0) for _,_,x in data]

	for i in range(1,len(loops)):
		loops[i] += loops[i-1]
	return loops

def plotLoops(loop):
	plt.plot(list(range(len(loop))), loop)
	# plt.savefig("plt_" + str(i) + ".png")

def getAllData(fol):

	data = []

	i=1
	single_data = getData(fol, i)
	while single_data != None:
		data.append(single_data)
		i+=1
		single_data = getData(fol, i)

	for i in range(len(data)):
		data[i] = data[i][1:len(data[i])]

	return data

def getAllLoops(data):
	return [loopify(x) for x in data]

if __name__ == '__main__':

	import Expgrad as EG

	if len(sys.argv)>1:
		FOL = sys.argv[1]

	data = getAllData(FOL)

	# loops = getAllLoops(data)

	# loops = [x for x in loops if x[-1]>1]

	# for loop in loops:
		# plotLoops(loop)

	# plt.grid()
	# plt.savefig("all_loops.png", dpi=900)

	model = EG.Model(4096, int(sys.argv[2]), 7)

	for i in range(1):
		model.addData(data[i])

	print("Forward:\n", model.getForward())
	print("Backward:\n", model.getBackward())

	print("\n----------------------------------------------\n")

	print("Occurence:\n", model.getOccurence())
	# print(np.sum(model.gamma, axis=1))
	print("Co-occurence:\n", model.getCoOccurrence())

	# summed = np.sum(model.xi, axis=2)
	# for t in range(len(summed)):
		# print(summed[t])

	print("\n----------------------------------------------\n")

	model.Start()

	while(True):
		b = input("")

		if b=="0":
			break
		print("Likelihood: ", model.Step())


	name = input("save in: ")
	model.dump(name)


