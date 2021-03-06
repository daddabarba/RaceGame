#!/bin/bash

for i in $(seq 1 1 $1)
do
	python3 logHandler.py ~/serv_${i}_0_log true &
	pid_log=$!
	python3 raceGame.py ~/serv_$i --n-loops $2 --delay 20 --abs-state 0 6 2 100 &
	pid_env=$!
	sleep 1
	python3 Agent.py 729 10 7 0.75 0.99 10 ~/serv_${i}_0 pars_ol pars_ol
	pid_car=$!

	wait $pid_env
	wait $pid_car
	wait $pid_log
done
