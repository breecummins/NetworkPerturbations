# NetworkPerturbations

## Installation

### Dependencies

* Python 2.7
* DSGRN and dependencies
* NetworkPerturbations

## Experiment 1

### Overview

This is timing experiment for the following network with approximately 1.2 billion parameters, given in DSGRN network specification format.

```json
S : S  
Myc : E2F + S : E
CycD : Myc + E2F : E 
CycE : E2F : E
E2F : (Myc + E2F)(~E2F_Rb) : E
E2F_Rb : (E2F)(~CycD)(~CycE) : E
```
A factor graph was created over the variable ```S```, resulting in 212,103,360 reduced parameters. We randomly sampled 10,000 reduced parameters 1000 times in order to estimate the total computational cost of the procedure.

### Procedure

The experiment was run as follows on conley3.rutgers.edu as a single-threaded process:

```bash
cd NetworkPerturbations
qsub analysis/hysteresis_qsub.py
```
The file hysteresis_qsub.py has the following content:

```bash
#!/bin/bash

#Active comments for SGE
#$ -V
#$ -cwd
#$ -j y
#$ -S /bin/bash
#$ -pe orte 1

time python analysis/hysteresis.py
```
The file hysteresis.py contains several query functions and is currently unversioned. The following line is (currently) required for the experiment to process correctly:

```python
if __name__ == "__main__":
	E2F_net1_analysis()
```
where the default arguments for ```E2F_net1_analysis()``` are

```python
E2F_net1_analysis(dbfile = "/share/data/CHomP/Projects/DSGRN/DB/data/6D_2016_08_26_cancerE2Fnetwork1.db",savefilename="6D_2016_08_26_cancerE2F_hysteresis_resetbistab_net1_subset.json",call=hysteresis_counts_only_subset)
```

The number of reduced parameters to query (10,000) and the number of repetitions (1000) of sampling are function defaults.

### Results

Output was saved to hysteresis_qsub.sh.o*********, where the stars indicate a long integer dependent on the process id. The first line of the output file gives the time in hours for the preprocessing step of searching the database and creating the factor graph. The next 1000 lines each contain a time in seconds for 10,000 reduced parameter queries. The last line records the average of those times.

* Preprocessing step: 4.91 hours
* Average time for 10,000 hysteresis and resettable bistability queries: 32.03 seconds

