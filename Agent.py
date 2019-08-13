import numpy as np
import random as rand

import dataTools as dt

import sys

class SarsaAgent:

	def __init__(self, nStates, nActions, alpha, gamma, T):

		self.QMat = np.random.rand(nStates, nActions)

		self.nStates = nStates
		self.nActions = nActions

		self.alpha = alpha
		self.gamma = gamma
		self.T = T

	def update(self, s1, a1, r, s2, a2):

		update = r + self.gamma*self.QMat[s2][a2]
		memory = self.QMat[s1][a1]

		self.QMat[s1][a1] = (1-self.alpha)*memory + self.alpha*update

	def __call__(self, s):
		p = self.softmax(s)
		p /= p.sum()
		return 	np.random.choice(self.nActions, p=p)	

	def softmax(self, s):

		x = self.QMat[s]

		e_x = np.exp((x - np.max(x))/self.T)
		return e_x / e_x.sum()

	def dump(self, name):
		np.save(name+"_Q", self.QMat)

	def load(self, name):
		self.QMat = np.load(name+"_Q.npy")


class ImitationAgent(SarsaAgent):

	def __init__(self, nStates, nActions, alpha, gamma, T, source):

		super(ImitationAgent, self).__init__(nStates, nActions, alpha, gamma, T)

		self.transitions = []

		dataL = dt.getAllData(source)

		for data in dataL:

			s1 = data[0][0]
			a1 = data[0][1]
			r = data[0][2]

			for t in range(1, len(data)):
				s2 = data[t][0]
				a2 = data[t][1]

				self.transitions.append((s1, a1, r, s2, a2))

				s1 = s2
				a1 = a2
				r = data[t][2]

		for e in self.transitions:
			self.update(*e)

	def train(self, nSteps):

		for i in range(nSteps):

			e = rand.choice(self.transitions)
			self.update(*e)



if __name__ == '__main__':
	
	a = ImitationAgent(int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), sys.argv[6])
