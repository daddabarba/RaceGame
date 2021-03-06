import pygame as pg
import numpy as np

import copy
import sys

import generatePath as gen
import environmentObjects as eo

import pars

class Game:

	def __init__(self):

		pg.init()

		self.__win = pg.display.set_mode((1000,1000))
		pg.display.set_caption("Racing Game")



	def run(self, nLoops=None, delay=pars.DEF_DELAY):

		loop = 0
		while(nLoops == None or loop<nLoops):

			pg.time.delay(delay)

			for event in pg.event.get():
				if event.type == pg.QUIT:
					run = False
					continue

			self.__win.fill(pars.BG_DEF_COL)
			self.render()

			pg.display.update()
			loop += 1

	def render(self):
		pass

	def getWin(self):
		return self.__win

	def __del__(self):
		pg.quit()


class RaceGame(Game):

	def __init__(self, map, precision=pars.DEF_PRECISION, step=pars.DEF_STEP):
		super(RaceGame, self).__init__()

		self.__step = step

		self.__cars = []
		self.__walls = []
		self.__plates = []

		self.initialDirection = [0,1]

		square_size = int(self.getWin().get_width()/map["size"][0])
		self.__start_position = (np.array([square_size*(map["trajectory"][0][0]+1), square_size*(map["trajectory"][0][1]+1)]) - square_size/2).astype(int)

		trajectory = map["trajectory"]

		if trajectory[1][0]==trajectory[0][0]:
			self.initialDirection = np.array([0,1])
		else:
			self.initialDirection = np.array([1,0])
		
		if trajectory[1][0]>trajectory[0][0] or trajectory[1][1]>trajectory[0][1]:
			self.initialDirection = -1*self.initialDirection

		shift = np.array([square_size/precision, square_size/precision])

		for i in range(len(trajectory)):
			
			cp = trajectory[i]

			pred = trajectory[i-1]
			succ = trajectory[np.mod(i+1,len(trajectory))]

			ul = np.array([square_size*cp[0], square_size*cp[1]])
			dr = np.array([square_size*(cp[0]+1), square_size*(cp[1]+1)])

			if succ[0]==cp[0] and succ[1]<cp[1]:
				bestMove = 3
			elif succ[0]==cp[0] and succ[1]>cp[1]:
				bestMove = 1
			elif succ[1]==cp[1] and succ[0]<cp[0]:
				bestMove = 2
			else:
				bestMove = 0

			inner_count = 0
			self.__plates.append([])
			for r in range(precision):
				for c in range(precision):
					self.__plates[-1].append(eo.Plate(ul+np.array([c,r])*shift, square_size/precision, square_size/precision, bestMove = bestMove))
					self.__plates[-1][-1].setID(i*precision*precision+inner_count, i)
					self.__plates[-1][-1].setWindow(self.getWin())
					self.__plates[-1][-1].setEnv(self)

			# self.__plates.append(eo.Plate(ul,square_size,square_size))

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

		# for i in range(len(self.__plates)):
		#	self.__plates[i].setID(i)
		#	self.__plates[i].setWindow(self.getWin())
		#	self.__plates[i].setEnv(self)


	def getPlate(self, car):

		for trail in self.__plates:
			for plate in trail:
				if plate.carOn(car):
					return plate

		return None

	def getWalls(self):
		return self.__walls

	def moveReward(self, trail, car):
		
		if not car.loopDirection:
			car.loopDirection = 1 if trail==self.__step else -1
			for plate in self.__plates[self.__step*car.loopDirection*-1]:
				plate.setReward(car, pars.BASE_R)
			for plate in self.__plates[self.__step*car.loopDirection]:
				plate.setReward(car, pars.R_BACK)

		# for plate in self.__plates[(trail+car.loopDirection*self.__step)%len(self.__plates)]:
		#	plate.setReward(car, pars.R_CHPT)
		# for plate in self.__plates[trail]:
		#	plate.setReward(car,pars.BASE_R)
			
		# for plate in self.__plates[(trail+car.loopDirection*self.__step*-1)%len(self.__plates)]:
		#	plate.setReward(car, pars.R_BACK)
		# for plate in self.__plates[(trail-2*self.__step*car.loopDirection)%len(self.__plates)]:
		#	plate.setReward(car, pars.BASE_R)
		# for plate in self.__plates[(trail+2*self.__step*car.loopDirection)%len(self.__plates)]:
		#	plate.setReward(car, pars.BASE_R)

		for group in self.__plates:
			for plate in group:
				plate.setReward(car, pars.BASE_R)

		for plate in self.__plates[(trail+car.loopDirection*self.__step)%len(self.__plates)]:
			plate.setReward(car, pars.R_BACK)
		for plate in self.__plates[(trail+car.loopDirection*self.__step*-1)%len(self.__plates)]:
			plate.setReward(car, pars.R_CHPT)


	def render(self):

		for trail in self.__plates:
			for plate in trail:
				plate.draw(self.__cars)

		if self.__cars:
			for car in self.__cars:
				car.draw(self.__walls)

		for wall in self.__walls:
			wall.draw()

	def addCars(self, cars):

		numStates = 0
		for trail in self.__plates:
			numStates += len(trail)

		for car in cars:
			self.__cars.append(car)
			car.setWindow(self.getWin())
			car.setPosition(self.__start_position)
			car.setDirection(self.initialDirection)
			car.setNumStates(numStates)
			car.setEnv(self)
			car.start()
			for plate in self.__plates[self.__step]:
				plate.setReward(car, pars.R_CHPT)
			for plate in self.__plates[self.__step*-1]:
				plate.setReward(car, pars.R_CHPT)



def main(argv):

	size = pars.DEF_SIZE
	num_cars = pars.DEF_CARS
	delay = pars.DEF_DELAY
	absStates = {}
	cheat = False
	nLoops = None
	nTracks = 1

	if len(argv)>2:
		i = 2
		while i<len(argv): 
			if argv[i] == "--size":
				size = int(argv[i+1])
				i+=2
			elif argv[i] == "--n-cars":
				num_cars = int(argv[i+1])
				i+=2
			elif argv[i] == "--delay":
				delay = int(argv[i+1])
				i+=2
			elif argv[i] == "--abs-state":
				car = int(argv[i+1])
				n_angles = int(argv[i+2])
				n_pieces = int(argv[i+3])
				l_pieces = float(argv[i+4])
				absStates[car] = (n_angles, n_pieces, l_pieces)
				i+=5
			elif argv[i] == "--cheat":
				cheat = True
				i+=1
			elif argv[i] == "--n-loops":
				nLoops = int(argv[i+1])
				i+=2
			elif argv[i] == "--n-tracks":
				nTracks = int(argv[i+1])
				i+=2
			else:
				print("option " + argv[i] +	 " not recognized")
				exit(-1)


	cars = []

	Car = eo.Car

	if cheat:
		Car = eo.CheatCar

	for i in range(num_cars):
		if not i in absStates.keys():
			cars.append(Car(i, argv[1], 50, (500,500)))
		else:
			cars.append(Car(i, argv[1], 50, (500,500), n_angles=absStates[i][0], n_pieces=absStates[i][1], l_pieces=absStates[i][2]))

	for i in range(nTracks):
		map = {}
		map["size"] = (size,size)
		map["trajectory"] = gen.generateTrack(size)

		game = RaceGame(map)
		game.addCars(cars)

		game.run(delay=delay, nLoops = nLoops)

if __name__ == '__main__':
	main(sys.argv)
