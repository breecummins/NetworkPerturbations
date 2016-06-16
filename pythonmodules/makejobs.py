from callandanswer import getinfo
from networkperturbations import perturbNetwork
import fileparsers
import subprocess

class Job():

    def __init__(self,time_to_wait=300):
        # how long to compute network perturbations before giving up (in seconds)
        self.time_to_wait=time_to_wait

        # get parameters and files for the perturbations
        self.params = getinfo()

        # set up folders for calculations
        self.makedirectories()

        # do perturbations
        if self.params.has_key['numperturbations']:
            self.parsefilesforperturbation()
            self.makenetworks()

        # make patterns
        if self.params.has_key['timeseriesfile']:
            pass
            # parse time series files
            # make patterns

        # shell call to scheduler

    def makedirectories(self):
        # use datetime as unique identifier to avoid overwriting
        DATETIME=subprocess.check_output(['date +%Y_%m_%d_%H_%M_%S'],shell=True).strip()
        try:
            self.NETWORKDIR=self.params['networkfolder']
            try:
                self.PATTERNDIR=self.params['patternfolder']
            except:
                if self.params.has_key('timeseriesfile'):
                    self.PATTERNDIR ="./computations"+DATETIME+"/patterns"
                    subprocess.call(['mkdir','-p',self.PATTERNDIR],shell=True)
        except:
            self.NETWORKDIR ="./computations"+DATETIME+"/networks"
            subprocess.call(['mkdir','-p',self.NETWORKDIR],shell=True)
            if self.params.has_key('timeseriesfile'):
                self.PATTERNDIR ="./computations"+DATETIME+"/patterns"
                subprocess.call(['mkdir','-p',self.PATTERNDIR],shell=True)

        self.DATABASEDIR="./computations"+DATETIME+"/databases"
        self.RESULTSDIR ="./computations"+DATETIME+"/results"
        subprocess.call(['mkdir','-p',self.DATABASEDIR],shell=True)
        subprocess.call(['mkdir','-p',self.RESULTSDIR],shell=True)

    def makenetworks(self):
        self.parsefilesforperturbation()
        maxparams = self.params['maxparams']
        numperturbations = self.params['numperturbations']
        add_madeup_nodes = self.params['add_madeup_nodes']
        networks = perturbNetwork(self)
        N=len(networks)
        for k,network_spec in enumerate(networks):
            # zero pad integer for unique id
            uid = str(k).zfill(N)
            nfile = "network"+uid+".txt"
            with open(nfile,'w') as nf:
                nf.write(network_spec)

    def parsefilesforperturbation(self):
            with open(self.params['networkfile'],'r') as f:
                self.network_spec = f.read()
            try:
                edgefile = self.params['edgefile']
                self.edgelist = fileparsers.parseEdgeFile(edgefile)
            except:
                self.edgelist = ()
            try:
                nodefile = self.params['nodefile']
                self.nodelist = fileparsers.parseNodeFile(nodefile)
            except:
                self.nodelist = ()

    def makepatterns(self):
        pass



    def makepatterns(self):
        pass
