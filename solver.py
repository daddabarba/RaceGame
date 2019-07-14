import TCPWrapper as tcp
import time
import socket
import struct

import sys
import time

EPSILON = 1

class Remote:

	def __init__(self, port):
		# pg.init()
		# pg.display.set_mode((100,100))
		# pg.display.set_caption("controller")

		self.__action = tcp.Client(port + "_a", medium=socket.AF_UNIX)
		self.__state = tcp.Client(port + "_s", medium=socket.AF_UNIX)
		self.__reward = tcp.Client(port + "_r", medium=socket.AF_UNIX)
		self.__direction = tcp.Client(port + "_d", medium=socket.AF_UNIX)
		self.__move = tcp.Client(port + "_m", medium=socket.AF_UNIX)

	def start(self):

		run = True
		while(run):

			# for event in pg.event.get():
			#	if event.type == pg.QUIT:
			#		run = False
			#		continue
			
			self.action()
			time.sleep(0.05)

	def action(self):
		# pg.event.get()
		# keys = pg.key.get_pressed()

		direction = int.from_bytes(self.__direction.get(), "little")
		move = int.from_bytes(self.__move.get(), "little")*90

		toDo = (direction - move)

		while(toDo<0):
			toDo += 360
		toDo %= 360

		if toDo>360-EPSILON or toDo<EPSILON:
			self.__action(1)
		if toDo<180:
			self.__action(5)
		else:
			self.__action(3)

		# if keys[pg.K_RIGHT] and keys[pg.K_UP]:
		#	self.__action(3)
		# elif keys[pg.K_RIGHT] and keys[pg.K_DOWN]:
		#	self.__action(4)
		# elif keys[pg.K_LEFT] and keys[pg.K_UP]:
		#	self.__action(5)
		# elif keys[pg.K_LEFT] and keys[pg.K_DOWN]:
		#	self.__action(6)
		# elif keys[pg.K_UP]:
		#	self.__action(1)
		# elif keys[pg.K_DOWN]:
		#	self.__action(2)
		# else:
		#	self.__action(0)

		self.__state(1)
		self.__reward(1)
		self.__direction(1)
		self.__move(1)

		print("s: " + str(int.from_bytes(self.__state.get(), "little")) + " d: " + str(direction) + "\t r: " + str(struct.unpack('d', self.__reward.get())), "\t best move: ", move, "\t to do: ", toDo)


def main(argv):
	controller = Remote(argv[1])
	controller.start()

if __name__ == '__main__':
	main(sys.argv)
