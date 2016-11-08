from pythonmodules.makejobs import Job
import json, subprocess

def makeWavePoolDatabases(location="local",netdir='/Users/bcummins/ProjectSimulationResults/wavepool4patternmatch_paper/networks/'):
    params = {}
    params['dsgrn'] = '../DSGRN'
    params['networkfolder'] = netdir
    params['queryfile'] = 'shellscripts/stableFCqueryscript.sh'
    params['removeDB'] = 'y'
    params['removeNF'] = 'n'
    params['timeseriesfile'] = 'pythonmodules/datafiles/haase-fpkm-p1_yeast_s29.txt'
    params['ts_type'] = 'row'
    params['ts_truncation'] = 60
    params['scaling_factors'] = [0.0]
    job = Job(location,params)
    job.prep()
    job.run()

if __name__ == "__main__":
    # makeWavePoolDatabases("qsub","wavepoolnetworks")
    makeWavePoolDatabases()
