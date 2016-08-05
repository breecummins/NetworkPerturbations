from pythonmodules.makejobs import Job 
import sys

if sys.argv[1] not in ['0','1']:
    print "Input argument must be 1 (run on conley3) or 0 (run on hpc)."
    sys.exit()
else:
    job=Job(int(sys.argv[1]))
    job.prep()
    job.run()	
