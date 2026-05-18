#!/bin/bash

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
python3 main.py
sleep 1
node server.js &
sleep 0.1
xdg-open http://localhost:3000/ & # open the browser (on Linux), on windows is "start [browser (opt)] [link]"
wait

