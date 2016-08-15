from pythonmodules.makejobs import Job 
import sys

try:
    comp = sys.argv[1]
except IndexError:
    print "Input argument must be 1 (run on conley3) or 0 (run on hpc)."
    sys.exit()

if comp not in ['0','1']:
    print "Input argument must be 1 (run on conley3) or 0 (run on hpc)."
    sys.exit()
else:
    job=Job(int(sys.argv[1]))
    job.prep()
    job.run()	
