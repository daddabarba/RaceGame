import pygame as pg
import numpy as np

import copy

WALL_DEF_COL = (255,0,0)
TRACK_DEF_COL = (0, 150, 0)
TRACK_ON_COl = (0,150,80)
CAR_DEF_COL = (0,0,0)

class EnvObj:

	def __init__(self, color):

		self.__color = color
		self.__win = None

		self.__rec = None

	def setRec(self, rec):
		self.__rec = rec

	def getRec(self):
		return self.__rec

	def setWindow(self, window):
		self.__win = window

	def getWindow(self):
		return self.__win

	def setColor(self, color):
		self.__color = color

	def getColor(self):
		return self.__color

	def draw(self):
		if self.__win and self.__rec:
			pg.draw.rect(
					self.getWindow(), 
					self.__color, 
					self.getRec())

class Wall(EnvObj):

	def __init__(self, start, length, direction, color = WALL_DEF_COL):

		super(Wall, self).__init__(color)

		self.__start = start

		self.__direction = direction

		self.__end = copy.deepcopy(self.__start)
		self.__end += np.array([length, 0]) if direction == 0 else np.array([0, length])

		if direction:
			self.setRec(pg.Rect(start[0], start[1], 20, length))
		else:
			self.setRec(pg.Rect(start[0], start[1], length, 20))

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

class Plate(EnvObj):

	def __init__(self, start, width, height, color = TRACK_DEF_COL):

		super(Plate, self).__init__(color)

		self.setRec(pg.Rect(start[0],start[1],width,height))
		self.cars_on = []

	def draw(self, cars):

		self.cars_on = []

		if any(self.carsOn(cars)):
			self.setColor(TRACK_ON_COl)
		else:
			self.setColor(TRACK_DEF_COL)

		super(Plate, self).draw()

	def carsOn(self, cars):
		return [self.carOn(car) for car in cars]

	def carOn(self, car):
		if car.getRec()!=None and self.getRec().colliderect(car.getRec()):
			self.cars_on.append(car)
			return True
		return False

class Car(EnvObj):

	def __init__(self, radius, initial_position, initial_direction = (0, 1), color = CAR_DEF_COL):

		super(Car,self).__init__(color)

		self.__radius = radius
		self.__position = np.array(initial_position)

		self.__direction = np.array(initial_direction)
		self.__direction = self.__direction/np.linalg.norm(self.__direction)

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

	def setWindow(self, window):
		super(Car, self).setWindow(window)

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

		if self.getWindow():
			self.setRec(pg.draw.circle(
				self.getWindow(), 
				self.getColor(), 
				self.__position.astype(int), 
				self.__radius))
			pg.draw.line(
				self.getWindow(), 
				self.getColor(), 
				self.__position.astype(int), 
				(self.__position - 1.2*self.__radius*self.__direction).astype(int), 
				int(self.__radius/2))

	def getPosition(self):
		return self.__position

	def getRadius(self):
		return self.__radius