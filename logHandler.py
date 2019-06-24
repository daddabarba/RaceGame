import TCPWrapper as tcp
import socket
import struct

import sys

serv = tcp.Server(port=sys.argv[1], size=8, block=True, medium=socket.AF_UNIX)
serv.start()

R = []
i = 0

while True:
	try:
		r = struct.unpack('d', serv.get())[0]
		print("%d) reward: "%i + str(r))
		i+=1

		R.append(r)
	except:
		break

if len(sys.argv)==3 and (sys.argv[2]=="True" or sys.argv[2]=="true"):
	with open(sys.argv[1].split("/")[-1]+".txt", "w") as f:
		f.write(str(R))
