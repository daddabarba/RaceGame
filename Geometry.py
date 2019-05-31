import numpy as np


def norm(x):
	return x/np.linalg.norm(x)


def cosAng(x, y):
	return np.dot(norm(x), norm(y))


def sinAng(x, y):
	return np.linalg.norm(np.cross(norm(x), norm(y)))


def angRad(x, y):
	return np.arctan2(sinAng(x, y), cosAng(x, y))


def angDeg(x,y):
	return angRad(x, y)/np.pi * 180

def angVec(x):
	x = norm(x)
	rad = np.arctan2(x[1],x[0])
	return rad/np.pi*180 + 180
