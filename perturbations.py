from pythonmodules.makejobs import Job 
import sys

try:
    comp = sys.argv[1]
except IndexError:
    print "Input argument must be 'qsub' (run on conley3), 'sbatch' (run on hpcc/fen2), or 'local' (run serially locally)."
    sys.exit()

if comp not in ['qsub','sbatch','local']:
    print "Input argument must be 'qsub' (run on conley3), 'sbatch' (run on hpcc/fen2), or 'local' (run serially locally)."
    sys.exit()
else:
    job=Job(sys.argv[1])
    job.prep()
    job.run()	
