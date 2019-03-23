import pygame as pg
import TCPWrapper as tcp
import socket

import sys
import time

class Remote:

	def __init__(self, port):
		pg.init()
		pg.display.set_mode((500,500))
		pg.display.set_caption("controller")
		self.__client = tcp.Client(port, medium=socket.AF_UNIX)

	def start(self):

		run = True
		while(run):

			for event in pg.event.get():
				if event.type == pg.QUIT:
					run = False
					continue
			
			self.action()
			pg.time.delay(100)
			pg.display.update()

	def action(self):
		pg.event.get()
		keys = pg.key.get_pressed()

		if keys[pg.K_RIGHT] and keys[pg.K_UP]:
			self.__client(5)
		elif keys[pg.K_RIGHT] and keys[pg.K_DOWN]:
			self.__client(6)
		elif keys[pg.K_LEFT] and keys[pg.K_UP]:
			self.__client(7)
		elif keys[pg.K_LEFT] and keys[pg.K_DOWN]:
			self.__client(8)
		elif keys[pg.K_RIGHT]:
			self.__client(1)
		elif keys[pg.K_UP]:
			self.__client(2)
		elif keys[pg.K_LEFT]:
			self.__client(3)
		elif keys[pg.K_DOWN]:
			self.__client(4)


def main(argv):
	controller = Remote(argv[1])
	controller.start()

if __name__ == '__main__':
	main(sys.argv)