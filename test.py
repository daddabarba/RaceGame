import AiInterface as AII
import sys
import random
import time

server = AII.ActionInterface(1, sys.argv[1], int(sys.argv[2]))
server.start()

num = 1
for i in range(int(sys.argv[3])):
            val = server.getAction()

            if val != None:
                print(val, end=", ")

            time.sleep(0.002)
exit()
