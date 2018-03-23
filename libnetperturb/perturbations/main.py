from libnetperturb.perturbations.makejobs import Job
import sys

paramfile = sys.argv[1]
job = Job(paramfile)
job.run()

