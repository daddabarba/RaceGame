import TCPWrapper as tcp
import socket
import struct

import sys

serv = tcp.Server(port=sys.argv[1], size=8, block=True, medium=socket.AF_UNIX)
serv.start()

while True:
	print("reward: " + str(struct.unpack('d', serv.get())))