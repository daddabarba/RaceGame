import pygame as pg
import copy

import numpy as np

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

			self.__win.fill((150, 150, 150))
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
		#self.__walls = [
			#Wall(np.array([0,0]), self.getWin().get_width(), 0),
			#Wall(np.array([0,0]), self.getWin().get_height(), 1),
			#Wall(np.array([self.getWin().get_width(), self.getWin().get_height()]), -self.getWin().get_width(), 0),
			#Wall(np.array([self.getWin().get_width(), self.getWin().get_height()]), -self.getWin().get_height(), 1),
		#]

		square_size = int(self.getWin().get_width()/map["size"][0])
		self.__last = None

		for x in range(map["size"][0]):
			for y in range(map["size"][1]):
				if map["grid"][y][x]:

					ul = np.array([square_size*x, square_size*y])
					dr = np.array([square_size*(x+1), square_size*(y+1)])

					self.__last = (dr - square_size/2).astype(int)

					if x==0 or not map["grid"][y][x-1]:
						self.__walls.append(Wall(ul, square_size, 1))

					if x==(map["size"][0]-1) or not map["grid"][y][x+1]:
						self.__walls.append(Wall(dr, -square_size, 1))

					if y==0 or not map["grid"][y-1][x]:
						self.__walls.append(Wall(ul, square_size, 0))

					if y==(map["size"][1]-1) or not map["grid"][y+1][x]:
						self.__walls.append(Wall(dr, -square_size, 0))
						

		for wall in self.__walls:
			wall.setWindow(self.getWin())

	def render(self):
		if self.__cars:
			for car in self.__cars:
				car.draw(self.__walls)

		for wall in self.__walls:
			wall.draw()

	def addCars(self, cars):
		for car in cars:
			self.__cars.append(car)
			car.setWindow(self.getWin())
			car.setPosition(self.__last)


class Car:

	def __init__(self, radius, initial_position, initial_direction = (0, 1), color = (0,0,0)):

		self.__radius = radius
		self.__position = np.array(initial_position)

		self.__direction = np.array(initial_direction)
		self.__direction = self.__direction/np.linalg.norm(self.__direction)

		self.__color = color

		self.a = 0.0
		self.v = 0.0

		self.A_FACTOR = 1.5
		self.A_MAG = 20.0

		self.W_FACTOR = np.deg2rad(10)

		cos_w = np.cos(self.W_FACTOR)
		sin_w = np.sin(self.W_FACTOR)

		self.ROTATE_R = np.array([[cos_w, -sin_w], [sin_w, cos_w]])
		self.ROTATE_L = np.array([[cos_w, sin_w], [-sin_w, cos_w]])

		self.V_FACTOR = 1.5

		self.__win = None

	def setWindow(self, window):
		self.__win = window

	def setPosition(self, position):
		self.__position = np.array(position)

	def handle_events(self, walls):

		keys = pg.key.get_pressed()

		if keys[pg.K_UP] and self.a >=0:
			self.a = -1*self.A_MAG
		elif keys[pg.K_DOWN] and self.a<=0:
			self.a = self.A_MAG
		else:
			self.a = 0

		if keys[pg.K_LEFT]:
			self.__direction = np.dot(self.ROTATE_L, self.__direction)
		elif keys[pg.K_RIGHT]:
			self.__direction = np.dot(self.ROTATE_R, self.__direction)


		bumpWalls = [wall.collides(self) for wall in walls]
		for bumpWall in bumpWalls:
			if bumpWall:
				self.__position = self.__position + bumpWall.getBump(self)*self.v

		self.a /= self.A_FACTOR

		if self.a != 0:
			self.v += self.a
		else:
			self.v /= self.V_FACTOR

		self.__position = np.round_(self.__position + self.__direction*self.v)

		for bumpWall in bumpWalls:
			if bumpWall:
				self.__position = bumpWall.boundSpace(self, self.__position)

	def draw(self, walls):

		self.handle_events(walls)

		if self.__win:
			pg.draw.circle(
				self.__win, 
				self.__color, 
				self.__position.astype(int), 
				self.__radius)
			pg.draw.line(
				self.__win, 
				self.__color, 
				self.__position.astype(int), 
				(self.__position - 1.2*self.__radius*self.__direction).astype(int), 
				int(self.__radius/2))

	def getPosition(self):
		return self.__position

	def getRadius(self):
		return self.__radius


class Wall:

	def __init__(self, start, length, direction, color = (255,0,0)):

		self.__color = color
		self.__start = np.array(start)

		self.__direction = direction
		self.__end = copy.deepcopy(self.__start)
		self.__end += np.array([length, 0]) if direction == 0 else np.array([0, length])

		self.__win = None

	def setWindow(self, window):
		self.__win = window

	def collides(self, car):

		if self.__direction:
			in_x = np.abs(self.__start[0] - car.getPosition()[0])<=car.getRadius()
			in_y = car.getPosition()[1] <= max(self.__start[1], self.__end[1]) and car.getPosition()[1] >= min(self.__start[1], self.__end[1])
		else:
			in_x = car.getPosition()[0] <= max(self.__start[0], self.__end[0]) and car.getPosition()[0] >= min(self.__start[0], self.__end[0])
			in_y = np.abs(self.__start[1] - car.getPosition()[1])<=car.getRadius()
			
		if in_x and in_y:
			return self

		return None

	def getBump(self, car):

		if self.__direction:
			if (self.__start[0] - car.getPosition()[0]) > 0:
				return np.array([1,0])
			else:
				return -1*np.array([1,0])
		else:
			if (self.__start[1] - car.getPosition()[1]) > 0:
				return np.array([0,1])
			else:
				return -1*np.array([0,1])

	def boundSpace(self, car, newS):

		if self.__direction and (car.getPosition()[0]-self.__start[0])*(newS[0]-self.__start[0]) <= 0 and np.abs(newS[0]-self.__start[0])<car.getRadius():
			newS[0] = self.__start[0] + (car.getRadius() if (car.getPosition()[0]-self.__start[0])>=0 else -car.getRadius())
		elif not self.__direction and (car.getPosition()[1]-self.__start[1])*(newS[1]-self.__start[1]) <= 0 and np.abs(newS[1]-self.__start[1])<car.getRadius():
			newS[1] = self.__start[1] + (car.getRadius() if (car.getPosition()[1]-self.__start[1])>=0 else -car.getRadius())

		return newS

	def draw(self):
		if self.__win:
			pg.draw.line(
					self.__win, 
					self.__color, 
					self.__start.astype(int), 
					self.__end.astype(int), 
					20)


def main():

	map = {}

	map["size"] = (5,5)
	map["grid"] = [[True, True, True, False, False], [True, False, True, False, False], [True, False, True, True, True], [True, False, False, False, True], [True, True, True, True, True]]

	game = RaceGame(map)

	car = Car(50, (500,500))

	game.addCars([car])

	game.run()

if __name__ == '__main__':
	main()