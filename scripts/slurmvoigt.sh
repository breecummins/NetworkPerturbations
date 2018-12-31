#!/bin/bash
#SBATCH -p gpu               # partition (queue)
#SBATCH -n 1                # number cores
#SBATCH -N 1                 # Minimum one node
#SBATCH -t 0-10:00           # Runtime in D-HH:MM

time python voigtdesign.py
