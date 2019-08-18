import numpy as np
import random as rand

import dataTools as dt

import TCPWrapper as tcp
import socket
import struct

import time
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
		print("saving in: ", name+"_Q.npy")
		np.save(name+"_Q", self.QMat)

	def load(self, name):
		print("loading: ", name+"_Q.npy")
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

class Remote(SarsaAgent):

	def __init__(self, nStates, nActions, alpha, gamma, T, sock, name):

		super(Remote, self).__init__(nStates, nActions, alpha, gamma, T)

		self.__action = tcp.Client(sock + "_a", medium=socket.AF_UNIX)
		self.__state = tcp.Client(sock + "_s", medium=socket.AF_UNIX)
		self.__reward = tcp.Client(sock + "_r", medium=socket.AF_UNIX)

		self.__log = tcp.Client(sock+"_log", medium=socket.AF_UNIX)

		self.__name = name
		self.getState()

	def start(self):

		run = True

		s1 = self.getState()
		a1 = self.makeAction(s1)
		r = self.getReward()

		while(run):

			try:
				s2 = self.getState() 
				a2 = self.makeAction(s2)
			except:
				self.dump(self.__name)
				break

			if s2<0:
				break

			self.update(s1, a1, r, s2, a2)

			try:
				r = self.getReward()
			except:
				self.dump(self.__name)
				break
				p
			s1 = s2
			a1 = a2

	def getState(self):
		self.__state(1)
		return int.from_bytes(self.__state.get(), "little")

	def getReward(self):
		self.__reward(1)
		r = struct.unpack('d', self.__reward.get())[0]

		self.__log(r)
		return r

	def makeAction(self, state):
		a = self(state)

		self.__action(a)
		return a



if __name__ == '__main__':
	
	if len(sys.argv[1])==7:
		a = ImitationAgent(int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), sys.argv[6])
	else:
		a = Remote(int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), sys.argv[6], sys.argv[7])
		a.load(sys.argv[8])
		a.start()

