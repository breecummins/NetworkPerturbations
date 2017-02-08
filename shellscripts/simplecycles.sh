#!/bin/bash

#Active comments for SGE
#$ -V
#$ -cwd
#$ -j y
#$ -S /bin/bash
#$ -pe orte 1

time python pythonmodules/simplecycles.py "1" > repressilator1.txt
time python pythonmodules/simplecycles.py "2" > repressilator2.txt
time python pythonmodules/simplecycles.py "3" > repressilator3.txt