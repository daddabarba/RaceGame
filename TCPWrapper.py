import socket
import fcntl, os

MAX_PORT = 65536

class AiInterfaceServer:

	def __init__(self, port=5000, size=1024, block=True, host="127.0.0.1", medium=socket.AF_INET, mode=socket.SOCK_STREAM):

		self.__socket = socket.socket(medium, mode)

		foundPort = False
		while not foundPort and port<MAX_PORT:

			try:
				self.__socket.bind((host, port))
				foundPort = True
			except:
				port += 1


		if not foundPort:
			raise Exception("cannot find any available port") 

		self.__port = port
		self.__socket.listen(1)

		self.__connection = self.__address = None
		self.__block = block

		self.__size = size

	def get(self):

		try:
			return self.__connection.recv(1024).decode()
		except:
			return None

	def send(self, data):
		self.__connection.send(data.encode())
		return self

	def __call__(self, data):
		return self.send(data)

	def start(self):
		self.__connection, self.__address = self.__socket.accept()
		self.__connection.setblocking(self.__block)

		return self

	def getPort(self):
		return self.__port

	def __del__(self):
		
		if self.__connection:
			self.__connection.close()
		self.__socket.close()

class AiInterfaceClient:

	def __init__(self, port, size = 1024, block=True, host="127.0.0.1", medium=socket.AF_INET, mode=socket.SOCK_STREAM):

		self.__socket = socket.socket(medium, mode)
		self.__socket.connect((host, port))

		self.__port = port
		self.__socket.setblocking(block)

		self.__size = size

	def get(self):

		try:
			return self.__socket.recv(self.__size).decode()
		except:
			return None

	def send(self, data):
		self.__socket.send(data.encode())
		return self

	def __call__(self, data):
		return self.send(data)

	def getPort(self):
		return self.__port

	def __del__(self):
		self.__socket.close()
