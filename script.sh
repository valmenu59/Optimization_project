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
python3 main.py
wait
node server.js &
sleep 0.5
xdg-open http://localhost:3000/ & # open the browser (on Linux), on windows is "start [browser (opt)] [link]"
wait

