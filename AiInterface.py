import TCPWrapper as tcp
import socket

import math

A_NONE = 0
A_RIGHT = 1
A_ACC = 2
A_LEFT = 3
A_BRK = 4
A_RIGHT_ACC = 5
A_RIGHT_BRK = 6
A_LEFT_ACC = 7
A_LEFT_BRK = 8

class ActionInterface:

	def __init__(self, numActions):

		numBits = int(math.ceil(math.log(numActions+1,2)))
		numBytes = int(math.ceil(numBits/8.0))

		self.__server = tcp.Server(port="/home/daddabarba/Desktop/server", block=True, size=numBytes, medium=socket.AF_UNIX)
		print("started action listener at port %s"%str(self.__server.getPort()))

		self.__action = 0

	def start(self):
		self.__server.start()

	def getAction(self):

		action = self.__server.get()

		if action != None:
			self.__action = int.from_bytes(action, "little")

		return self.__action

	def __del__(self):
		del self.__server