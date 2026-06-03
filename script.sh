#!/bin/bash

# Initialisation
mkdir results

# Installation
printf "\n### Installation ###\n\n\n"
pip install cplex
pip install docplex
npm install

# Configuration docplex
# Replace the PATH by your one
# docplex config --upgrade /home/valmenu59/ibm2/cplex/

# Execution
printf "\n\n### Execution ###\n\n\n"
# arguments can be added like --start 3 --end 8 or -s 3 -e 8 to read instances from 3 to 8 (included)
# without arguments values are 1 to 10
python3 main.py # --start 3 --end 8
wait
node server.js &
sleep 0.5
xdg-open http://localhost:3000/ & # open the browser (on Linux), on windows is "start [browser (opt)] [link]"
wait

