import TCPWrapper as tcp
import socket
import struct

import sys

print("opening log handler at ", sys.argv[1])

serv = tcp.Server(port=sys.argv[1], size=8, block=True, medium=socket.AF_UNIX)
serv.start()

R = []
i = 0

store = (sys.argv[2]=="True" or sys.argv[2]=="true")

while True:
	try:
		r = struct.unpack('d', serv.get())[0]
		if not store:
			print("%d) reward: "%i + str(r))
		i+=1

		R.append(r)
	except:
		break

if len(sys.argv)==3 and store:
	with open(sys.argv[1].split("/")[-1]+".txt", "w") as f:
		f.write(str(R))
