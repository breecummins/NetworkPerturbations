#!/bin/bash

#Active comments for SGE
#$ -V
#$ -cwd
#$ -j y
#$ -S /bin/bash
#$ -pe orte 8

time python analysis/fullinducibility.py
