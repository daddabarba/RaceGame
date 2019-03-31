import AiInterface as AII 
import threading as thread

import sys

state = AII.StateInterface(1, sys.argv[1], int(sys.argv[2]))
action = AII.ActionInterface(1, sys.argv[1], int(sys.argv[3]))
reward = AII.RewardInterface(1, sys.argv[1])

t1 = thread.Thread(target=state.start)
t2 = thread.Thread(target=action.start)
t3 = thread.Thread(target=reward.start)

t1.start()
t2.start()
t3.start()

t1.join()
t2.join()
t3.join()