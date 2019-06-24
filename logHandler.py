import TCPWrapper as tcp
import socket
import struct

import sys

serv = tcp.Server(port=sys.argv[1], size=8, block=True, medium=socket.AF_UNIX)
serv.start()

R = []

while True:
	try:
		r = struct.unpack('d', serv.get())[0]
		print("reward: " + str(r))

		R.append(r)
	except:
		break

with open(sys.argv[1].split("/")[-1]+".txt", "w") as f:
	f.write(str(R))
