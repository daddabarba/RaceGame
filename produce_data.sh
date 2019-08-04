#!/bin/bash

for i in $(seq 1 1 $1)
do
	python3 raceGame.py ~/serv_$i --cheat --n-loops $2 --delay 20 --abs-state 0 6 3 50 &
	pid_env=$!
	sleep 1
	python3 solver.py ~/serv_${i}_0
	pid_car=$!

	wait $pid_env
	wait $pid_car
done
