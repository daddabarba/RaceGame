import TCPWrapper as tcp
import socket

import math
import random

A_NONE = 0
A_RIGHT = 1
A_ACC = 2
A_LEFT = 3
A_BRK = 4
A_RIGHT_ACC = 5
A_RIGHT_BRK = 6
A_LEFT_ACC = 7
A_LEFT_BRK = 8

BASE = "/home/daddabarba/Desktop/server"

class AiInterface:

	def __init__(self, id, maxNum, file):

		self.id = id

		numBits = int(math.ceil(math.log(maxNum+1,2)))
		numBytes = int(math.ceil(numBits/8.0))

		self.__max = maxNum
		self.__server = tcp.Server(port=file, block=False, size=numBytes, medium=socket.AF_UNIX)

	def getMax(self):
		return self.__max

	def getServer(self):
		return self.__server

	def start(self):
		self.__server.start()

	def __del__(self):
		del self.__server

class ActionInterface(AiInterface):

	def __init__(self, id, numActions):
		super(ActionInterface, self).__init__(id, numActions, BASE+"_a_" + str(id))
		print("started action listener %d at port %s"%(self.id, str(self.getServer().getPort())))

		self.__action = 0

	def start(self):
		super(ActionInterface, self).start()
		self.getServer()(self.getMax())

	def getAction(self):

		action = self.getServer().get()

		if action != None:
			self.__action = int.from_bytes(action, "little")
	
		return self.__action

class RewardInterface(AiInterface):

	def __init__(self, id):
		super(RewardInterface, self).__init__(id, 10000, BASE + "_r_" + str(id))
		print("started reward listener %d at port %s"%(self.id, str(self.getServer().getPort())))

		self.__reward = 0.0

	def sendReward(self):

		reward = self.getServer().get()

		if reward != None:
			self.getServer().send(self.__reward)
			self.__reward = 0.0

	def addReward(self, r):
		self.__reward += r


class StateInterface(AiInterface):

	def __init__(self, id, numStates):
		super(StateInterface, self).__init__(id, numStates, BASE+"_s_"+str(id))
		print("started state listener %d at port %s"%(self.id, str(self.getServer().getPort())))

		self.__state = 0

	def start(self):
		super(StateInterface, self).start()
		self.getServer()(self.getMax())

	def setState(self, state):
		self.__state = state

	def sendState(self):

		state = self.getServer().get()

		if state != None:
			self.getServer().send(self.__state)


