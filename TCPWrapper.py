import socket
import fcntl, os

import struct

MAX_PORT = 65536

class Server:

	def __init__(self, port=5000, size=1024, block=True, host="127.0.0.1", medium=socket.AF_INET, mode=socket.SOCK_STREAM):

		self.__socket = socket.socket(medium, mode)

		if medium == socket.AF_INET:
			foundPort = False
			while not foundPort and port<MAX_PORT:

				try:
					self.__socket.bind((host, port))
					foundPort = True
				except:
					port += 1

			if not foundPort:
				raise Exception("cannot find any available port") 
				
		elif medium == socket.AF_UNIX:

			if os.path.exists(port):
				os.remove(port)
				
			self.__socket.bind(port)


		self.__port = port
		self.__socket.listen(1)

		self.__connection = self.__address = None
		self.__block = block

		self.__size = size

	def get(self, size=None):

		try:
			return self.__connection.recv(self.__size if not size else size)
		except:
			return None

	def send(self, data):

		if isinstance(data, str):
			data = data.encode()
			size = len(data)
		elif isinstance(data, int):
			data = data.to_bytes(4, 'little')
			size = 4
		elif isinstance(data, float):
			data = bytearray(struct.pack("<d", data))
			size = 8

		try:
			self.__connection.send(data, size)
		except:
			print ("resource unavailable")
			return None

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

class Client:

	def __init__(self, port, size = 1024, block=True, host="127.0.0.1", medium=socket.AF_INET, mode=socket.SOCK_STREAM):

		self.__socket = socket.socket(medium, mode)
			
		if medium == socket.AF_INET:
			self.__socket.connect((host, port))
		elif medium == socket.AF_UNIX:
			self.__socket.connect(port)

		self.__port = port
		self.__socket.setblocking(block)

		self.__size = size

	def get(self, size=None):

		try:
			return self.__socket.recv(self.__size if not size else size)
		except:
			return None

	def send(self, data):

		if isinstance(data, str):
			data = data.encode()
		elif isinstance(data, int):
			data = data.to_bytes(4,'little')
		elif isinstance(data, float):
			data = bytearray(struct.pack("<d", data))

		self.__socket.send(data)
		return self

	def __call__(self, data):
		return self.send(data)

	def getPort(self):
		return self.__port

	def __del__(self):
		self.__socket.close()
