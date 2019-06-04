import TCPWrapper as tcp
import socket
import threading as thread

import math
import random

A_NONE = 0
# A_RIGHT = 1
A_ACC = 1
# A_LEFT = 3
A_BRK = 2
A_RIGHT_ACC = 3
A_RIGHT_BRK = 4
A_LEFT_ACC = 5
A_LEFT_BRK = 6

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

	def __init__(self, id, base, numActions):
		super(ActionInterface, self).__init__(id, numActions, base+"_" + str(id) + "_a")
		print("started action listener %d at port %s"%(self.id, str(self.getServer().getPort())))

		self.__action = 0

	def start(self):
		super(ActionInterface, self).start()
		self.getServer()(self.getMax())
   
	def getAction(self):

		action = self.getServer().get(4)

		if action != None:
			self.__action = int.from_bytes(action, "little")
		return self.__action

class RewardInterface(AiInterface):

	def __init__(self, id, base):
		super(RewardInterface, self).__init__(id, 10000, base + "_" + str(id) + "_r")
		print("started reward listener %d at port %s"%(self.id, str(self.getServer().getPort())))

		self.__reward = 0.0

	def sendReward(self):

		sig = self.getServer().get(4)

		if sig != None:
			self.getServer().send(self.__reward)
			self.__reward = 0.0

	def addReward(self, r):
		self.__reward += r


class StateInterface(AiInterface):

	def __init__(self, id, base, numStates):
		super(StateInterface, self).__init__(id, numStates, base+"_"+str(id) + "_s")
		print("started state listener %d at port %s"%(self.id, str(self.getServer().getPort())))

		self.__state = 0

	def start(self):
		super(StateInterface, self).start()

		self.getServer()(self.getMax())

	def setState(self, state):
		self.__state = state

	def sendState(self):

		sig = self.getServer().get(4)

		if sig != None:
			sent = self.getServer().send(int(self.__state))



