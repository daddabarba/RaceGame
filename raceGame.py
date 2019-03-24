import pygame as pg
import numpy as np

import copy
import sys

import generatePath as gen
import environmentObjects as eo

BG_DEF_COL = (150, 150, 150)
DEF_SIZE = 5

class Game:

	def __init__(self):

		pg.init()

		self.__win = pg.display.set_mode((1000,1000))
		pg.display.set_caption("Racing Game")



	def run(self, delay=100):

		run = True
		while(run):

			pg.time.delay(delay)

			for event in pg.event.get():
				if event.type == pg.QUIT:
					run = False
					continue

			self.__win.fill(BG_DEF_COL)
			self.render()

			pg.display.update()

	def render(self):
		pass

	def getWin(self):
		return self.__win

	def __del__(self):
		pg.quit()


class RaceGame(Game):

	def __init__(self, map):
		super(RaceGame, self).__init__()

		self.__cars = []
		self.__walls = []
		self.__plates = []

		square_size = int(self.getWin().get_width()/map["size"][0])
		self.__start_position = (np.array([square_size*(map["trajectory"][0][0]+1), square_size*(map["trajectory"][0][1]+1)]) - square_size/2).astype(int)

		trajectory = map["trajectory"]

		for i in range(len(trajectory)):
			
			cp = trajectory[i]

			pred = trajectory[i-1]
			succ = trajectory[np.mod(i+1,len(trajectory))]

			ul = np.array([square_size*cp[0], square_size*cp[1]])
			dr = np.array([square_size*(cp[0]+1), square_size*(cp[1]+1)])

			self.__plates.append(eo.Plate(ul,square_size,square_size))

			if not (cp[1]==pred[1] and pred[0]<cp[0]) and not(cp[1]==succ[1] and succ[0]<cp[0]):
				self.__walls.append(eo.Wall(ul, square_size, 1))

			if not (cp[1]==pred[1] and pred[0]>cp[0]) and not(cp[1]==succ[1] and succ[0]>cp[0]):
				self.__walls.append(eo.Wall(dr, -square_size, 1))

			if not (cp[0]==pred[0] and pred[1]<cp[1]) and not(cp[0]==succ[0] and succ[1]<cp[1]):
				self.__walls.append(eo.Wall(ul, square_size, 0))

			if not (cp[0]==pred[0] and pred[1]>cp[1]) and not(cp[0]==succ[0] and succ[1]>cp[1]):
				self.__walls.append(eo.Wall(dr, -square_size, 0))
				

		for wall in self.__walls:
			wall.setWindow(self.getWin())

		for i in range(len(self.__plates)):
			self.__plates[i].setID(i)
			self.__plates[i].setWindow(self.getWin())

	def getPlate(self, car):

		for plate in self.__plates:
			if plate.carOn(car):
				return plate

		return None

	def render(self):

		for plate in self.__plates:
			plate.draw(self.__cars)

		if self.__cars:
			for car in self.__cars:
				car.draw(self.__walls)

		for wall in self.__walls:
			wall.draw()

	def addCars(self, cars):
		for car in cars:
			self.__cars.append(car)
			car.setWindow(self.getWin())
			car.setPosition(self.__start_position)
			car.setNumStates(len(self.__plates))
			car.setEnv(self)
			car.start()



def main(argv):

	if len(argv)<3:
		size = DEF_SIZE
	else:
		size = int(argv[2])

	map = {}
	map["size"] = (size,size)
	map["trajectory"] = gen.generateTrack(size)

	game = RaceGame(map)

	car = eo.Car(1, argv[1], 50, (500,500))

	game.addCars([car])

	game.run()

if __name__ == '__main__':
	main(sys.argv)