import pygame as pg
import numpy as np
import math
import threading as thread

import pars

import AiInterface as AII

import Geometry as geom

import copy

WALL_DEF_COL = (255,0,0)
TRACK_DEF_COL = (0, 150, 0)
TRACK_ON_COl = (0,150,80)
TRACK_CHPT_COL = (150,0,0)
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

		self.id = None
		self.trail = None

		self.__r = {}
		self.__env = None

		self.setRec(pg.Rect(start[0],start[1],width,height))
		self.cars_on = []

	def setID(self, id, trail):
		self.id = id
		self.trail = trail

	def setEnv(self, env):
		self.__env = env

	def draw(self, cars):

		self.cars_on = []

		if any(x!=pars.BASE_R for x in list(self.__r.values())):
			self.setColor(TRACK_CHPT_COL)
		elif any(self.carsOn(cars)):
			self.setColor(TRACK_ON_COl)
		else:
			self.setColor(TRACK_DEF_COL)

		super(Plate, self).draw()

	def carsOn(self, cars):
		self.cars_on = []
		return [self.carOn(car) for car in cars]

	def carOn(self, car):
		if car.getRec()!=None and self.getRec().colliderect(car.getRec()):
			self.cars_on.append(car)
			return True
		return False

	def setReward(self, car, r):
		self.__r[car] = r

	def getReward(self, car):

		if not car in self.__r.keys():
				return pars.BASE_R
		return self.__r[car]

	def assignReward(self, car):

		ret = self.getReward(car)

		if ret!=pars.BASE_R:
				self.__env.moveReward(self.trail, car)
		return ret

class Car(EnvObj):

	def __init__(self, id, base, radius, initial_position, fine_rot_sensor=pars.FINE_ROT_SENSOR, initial_direction = (0, 1), color = CAR_DEF_COL):

		super(Car,self).__init__(color)

		self.id = id
		self.base = base

		self.fine_rot_sensor = fine_rot_sensor

		self.loopDirection = None

		self.__radius = radius
		self.__position = np.array(initial_position)

		self.__direction = np.array(initial_direction)
		self.__direction = self.__direction/np.linalg.norm(self.__direction)

		self.a = 0.0
		self.v = 0.0

		self.A_FACTOR = 1.5
		self.A_MAG = 10.0

		self.W_FACTOR = np.deg2rad(10)

		cos_w = np.cos(self.W_FACTOR)
		sin_w = np.sin(self.W_FACTOR)

		self.ROTATE_R = np.array([[cos_w, -sin_w], [sin_w, cos_w]])
		self.ROTATE_L = np.array([[cos_w, sin_w], [-sin_w, cos_w]])

		self.V_FACTOR = 1.5

		self.__actionListener = AII.ActionInterface(self.id, self.base, 9)
		self.__stateSocket = None
		self.__rewardSocket = AII.RewardInterface(self.id, self.base)

	def start(self):
		
		t1 = thread.Thread(target = self.__actionListener.start)
		t2 = thread.Thread(target = self.__stateSocket.start)
		t3 = thread.Thread(target = self.__rewardSocket.start)

		t1.start()
		t2.start()
		t3.start()

		t1.join()
		t2.join()
		t3.join()

	def setWindow(self, window):
		super(Car, self).setWindow(window)

	def setNumStates(self, numStates):
		self.__stateSocket = AII.StateInterface(self.id, self.base, numStates*self.fine_rot_sensor)

	def setEnv(self, env):
		self.__env = env

	def setPosition(self, position):
		self.__position = np.array(position)

	def handle_events(self, walls):

		action = self.__actionListener.getAction()

		if (action==AII.A_ACC or action==AII.A_RIGHT_ACC or action==AII.A_LEFT_ACC) and self.a >=0:
			self.a = -1*self.A_MAG
		elif (action==AII.A_BRK or action==AII.A_RIGHT_BRK or action==AII.A_LEFT_BRK) and self.a<=0:
			self.a = self.A_MAG
		else:
			self.a = 0

		# if (action==AII.A_LEFT or action==AII.A_LEFT_ACC or action==AII.A_LEFT_BRK):
		#	self.__direction = np.dot(self.ROTATE_L, self.__direction)
		# elif (action==AII.A_RIGHT or action==AII.A_RIGHT_ACC or action==AII.A_RIGHT_BRK):
		#	self.__direction = np.dot(self.ROTATE_R, self.__direction)


		bumpWalls = [wall.collides(self) for wall in walls]
		for bumpWall in bumpWalls:
			if bumpWall:
				self.__position = self.__position + bumpWall.getBump(self)*-1*np.abs(self.v)
				self.__rewardSocket.addReward(pars.R_BUMP)

		self.a /= self.A_FACTOR

		if self.a != 0:
			self.v += self.a
		else:
			self.v /= self.V_FACTOR

		if action==AII.A_ACC or action==AII.A_BRK:
			self.__position = np.round_(self.__position + self.__direction*self.v)
		elif action!=AII.A_NONE:
			switch = np.array([1,-1]) * (1 if (action==AII.A_RIGHT_ACC or action==AII.A_RIGHT_BRK) else -1)

			r = self.__direction[::-1]*pars.L_TURN*switch
			P = self.__direction*pars.DT*self.v + r*(-math.sqrt((pars.L_TURN**2)*(pars.L_TURN**2 - (pars.DT*self.v)**2))/(pars.L_TURN**2) + 1)
			D = ((P-r)[::-1])/pars.L_TURN*switch

			self.__position = self.__position + 100*P
			self.__direction = D
		# self.__position = np.round_(self.__position + self.__direction*self.v)

		for bumpWall in bumpWalls:
			if bumpWall:
				self.__position = bumpWall.boundSpace(self, self.__position)

	def __connect(self):

		plate = self.__env.getPlate(self)

		self.__rewardSocket.addReward(plate.assignReward(self))
		self.__rewardSocket.sendReward()
		if self.__stateSocket:

			state = plate.id*self.fine_rot_sensor
			orientation = geom.angVec(self.__direction)
			state += int(orientation/(360/self.fine_rot_sensor))

			self.__stateSocket.setState(state)
			self.__stateSocket.sendState()

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

			self.__connect()

	def getPosition(self):
		return self.__position

	def getRadius(self):
		return self.__radius

	def __del__(self):
		del self.__actionListener
