import numpy as np
import random
import copy

actions = ["d","u","l","r"]

def generateTrack(size, min_len=2):

	map = np.zeros((size,size))

	start = (np.random.randint(0,size), np.random.randint(0,size))
	map[start[0]][start[1]] = 2
	
	path = generateTrackAux(start, map, size)
	actualPath = []

	if len(path)<=min_len:
		return generateTrack(size, min_len)

	for pos in path:
		actualPath.append((pos[1],pos[0]))

	return actualPath

def actionAllowed(a, pos, map):

	if a=="d":
		return pos[0] < (len(map)-1) and map[pos[0]+1][pos[1]]!=1
	if a=="u":
		return pos[0] > 0 and map[pos[0]-1][pos[1]]!=1
	if a=="r":
		return pos[1] < (len(map)-1) and map[pos[0]][pos[1]+1]!=1
	if a=="l":
		return pos[1] > 0 and map[pos[0]][pos[1]-1]!=1

	return False

def performAction(a, pos):

	if a=="d":
		return (pos[0]+1, pos[1])
	elif a=="u":
		return (pos[0]-1, pos[1])
	elif a=="r":
		return (pos[0], pos[1]+1)
	elif a=="l":
		return (pos[0], pos[1]-1)

def generateTrackAux(position, map, size):

	if map[position[0]][position[1]]==0:
		map[position[0]][position[1]] = 1

	possibleActions = copy.copy(actions)
	random.shuffle(possibleActions)

	#print("at (%d,%d), map:\n%s"%(position[0], position[1], str(map)))
	#input()

	for action in possibleActions:

		#print("(%d,%d) tring %s"%(position[0], position[1], action))

		if actionAllowed(action, position, map):

			nextPosition = performAction(action, position)
			#print("action allowed, next position: (%d,%d)"%(nextPosition[0], nextPosition[1]))
			#input()
			nextTrack = generateTrackAux(nextPosition, map, size)

			if map[nextPosition[0]][nextPosition[1]] > 1:
				#print("got to goal")
				return [position]

			if len(nextTrack) > 0:
				#print("back tracking")
				return [position] + nextTrack
		#input()

	if map[position[0]][position[1]]==1:
		map[position[0]][position[1]] = 0
	#print("can't go here")
	return []

def main():
	print(generateTrack(5))


if __name__ == '__main__':
	main()