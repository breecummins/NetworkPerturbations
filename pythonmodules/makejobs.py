from callandanswer import getinfo
from networkperturbations import perturbNetwork
import fileparsers
import subprocess

class Job():

    def __init__(self):
        # get parameters and files for the perturbations
        self.params = getinfo()

        # other stuff
        self.scheduler = self.getscheduler()
        self.helper = self.gethelper()
        self.commands = self.constructcommands()

    def makedirectories(self):

        # name directories
        DATETIME=subprocess.check_output(['date +%Y_%m_%d_%H_%M_%S'],shell=True).strip()
        try:
            self.NETWORKDIR=self.params['networkfolder']
            try:
                self.PATTERNDIR=self.params['patternfolder']
            except:
                self.PATTERNDIR ="./computations"+DATETIME+"/patterns"
        except:
            self.NETWORKDIR ="./computations"+DATETIME+"/networks"
            self.PATTERNDIR ="./computations"+DATETIME+"/patterns"

        self.DATABASEDIR="./computations"+DATETIME+"/databases"
        self.RESULTSDIR ="./computations"+DATETIME+"/results"

        # make directories
        subprocess.call(['mkdir','-p',self.NETWORKDIR],shell=True)
        subprocess.call(['mkdir','-p',self.PATTERNDIR],shell=True)
        subprocess.call(['mkdir','-p',self.DATABASEDIR],shell=True)
        subprocess.call(['mkdir','-p',self.RESULTSDIR],shell=True)



    def getperturbationcommand(self):
        pass

    def getscheduler(self):
        pass

    def gethelper(self):
        pass

    def constructshellcommands(self):
        pass

    def parsefiles(self):
        try:
            edgefile = self.params['edgefile']
            edgelist = fileparsers.parseEdgeFile(edgefile)
        except:
            edgelist = ()
        try:
            nodefile = self.params['nodefile']
            nodelist = fileparsers.parseNodeFile(nodefile)
        except:
            nodelist = ()
        return edgelist, nodelist

    def makenetworks(self):
        edgelist, nodelist = self.parsefiles()
        maxparams = self.params['maxparams']
        numperturbations = self.params['numperturbations']
        add_madeup_nodes = self.params['add_madeup_nodes']
        networks = perturbNetwork(network_spec,maxparams,numperturbations,edgelist,nodelist,add_madeup_nodes,time_to_wait=300)


    def makepatterns(self):
        pass
