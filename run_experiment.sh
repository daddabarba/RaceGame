#!/bin/bash

for i in $(seq 1 1 $1)
do
	python3 raceGame.py ~/serv_$i --n-loops $2 --delay 20 --abs-state 0 6 2 100 &
	pid_env=$!
	sleep 1
	python3 Agent.py 729 7 0.75 0.99 100 ~/serv_${i}_0 pars_bl pars_bl
	pid_car=$!

	wait $pid_env
	wait $pid_car
done
