from callandanswer import getinfo
import networkperturbations as perturb
import fileparsers, intervalgraph
import subprocess, time, random, os


class Job():

    def __init__(self,time_to_wait=300):
        # how long to compute network perturbations before giving up (in seconds)
        self.time_to_wait=time_to_wait

        # how many itertations are allowed when trying to add something during a single perturbation
        # note: it's unknown how many failures there could be, number set high
        # purpose is to avoid the (vanishingly small) chance that a single perturbation will block the program
        self.maxiterations = 10**4

        # get parameters and files for the perturbations
        self.params = getinfo()

        for (k,v) in self.params.iteritems():
            print k+ ' : ' + str(v)

        # set up folders for calculations
        self.makedirectories()

        # do perturbations
        if 'numperturbations' in self.params:
            self.makenetworks()

        # make patterns
        if self.PATTERNDIR is not None:
            pass
            # parse time series files
            # make patterns

        # shell call to scheduler

    def makedirectories(self):
        # use datetime as unique identifier to avoid overwriting
        DATETIME = subprocess.check_output(['date +%Y_%m_%d_%H_%M_%S'],shell=True).strip()

        if 'networkfolder' in self.params:
            self.NETWORKDIR=self.params['networkfolder']
            if 'patternfolder' in self.params:
                self.PATTERNDIR=self.params['patternfolder']
            folders = self.NETWORKDIR.split('/')
            uid =  '_' + folders[-1] + '_' + DATETIME
        else:
            uid = DATETIME
            self.NETWORKDIR ="./computations"+uid+"/networks"
            subprocess.call(['mkdir -p ' + self.NETWORKDIR],shell=True)

        if 'timeseriesfile' in self.params:
            self.PATTERNDIR ="./computations"+uid+"/patterns"
            subprocess.call(['mkdir -p ' + self.PATTERNDIR],shell=True)
        else:
            self.PATTERNDIR = None

        self.DATABASEDIR="./computations"+uid+"/databases"
        self.RESULTSDIR ="./computations"+uid+"/results"
        subprocess.call(['mkdir -p ' + self.DATABASEDIR],shell=True)
        subprocess.call(['mkdir -p ' + self.RESULTSDIR],shell=True)

    def makenetworks(self):
        self.parsefilesforperturbation()
        networks = self.perturbNetwork()
        N=len(str(len(networks)))
        for k,network_spec in enumerate(networks):
            # zero pad integer for unique id
            uid = str(k).zfill(N)
            nfile = os.path.join(self.NETWORKDIR, "network"+uid+".txt")
            with open(nfile,'w') as nf:
                nf.write(network_spec)

    def parsefilesforperturbation(self):
            with open(self.params['networkfile'],'r') as f:
                self.network_spec = f.read()
            if 'edgefile' in self.params:
                self.edgelist = fileparsers.parseEdgeFile(self.params['edgefile'])
            else:
                self.edgelist = None
            if 'nodefile' in self.params:
                self.nodelist = fileparsers.parseNodeFile(self.params['nodefile'])
            else:
                self.nodelist = None

    def makepatterns(self):
        pass

    def perturbNetwork(self):

        # reset random seed for every run
        random.seed()

        # make starting graph, make sure network_spec is essential, and add network_spec to list of networks
        starting_graph = intervalgraph.getGraphFromNetworkSpec(self.network_spec)
        network_spec = intervalgraph.createEssentialNetworkSpecFromGraph(starting_graph)
        networks = [network_spec]

        # Set a timer for the while loop, which can be infinite if numperturbations is too large for maxparams
        start_time = time.time()
        current_time = time.time()-start_time
        # now make perturbations
        while (len(networks) < self.params['numperturbations']+1) and (current_time < self.time_to_wait): 
            # explicitly copy so that original graph is unchanged
            graph = starting_graph.clone()
            # add nodes and edges or just add edges based on the self
            # this can fail, in which case None is returned
            if self.nodelist or (not self.edgelist and self.params['add_madeup_nodes'] == 'y'):
                graph = perturb.perturbNetworkWithNodesAndEdges(graph,self.edgelist,self.nodelist,self.maxiterations)
            else:
                graph = perturb.perturbNetworkWithEdgesOnly(graph,self.edgelist,self.maxiterations) 
            if graph is not None:
                # get the perturbed network spec
                network_spec = intervalgraph.createEssentialNetworkSpecFromGraph(graph)

                # TODO: check for graph isomorphisms in added nodes (only have string matching below). 
                # Can get nodes added in different orders with same edges. Should be rare in general, so not high priority.
                # BUT it might be more common than you'd think, since we filter given a maximum number of parameters.

                # check that network spec is all of unique (in string match, not isomorphism), small enough, and computable, then add to list
                if (network_spec not in networks) and perturb.checkComputability(network_spec,self.params['maxparams']):
                    networks.append(network_spec)
            current_time = time.time()-start_time
        if current_time > self.time_to_wait:
            print "Network perturbation timed out. Proceeding with fewer than requested perturbations."
        # Return however many networks were made
        return networks

if __name__=="__main__":
    job=Job(10)