#!/bin/bash

#Active comments for SGE
#$ -V
#$ -cwd
#$ -j y
#$ -S /bin/bash
#$ -pe orte 16

time python analysis/hysteresis.py
