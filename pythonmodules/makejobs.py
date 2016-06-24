from callandanswer import getinfo
import networkperturbations as perturb
import fileparsers, intervalgraph, ExtremaPO
import subprocess, time, random, os, json, itertools


class Job():

    def __init__(self,time_to_wait=300,qsub=True):
        # how long to compute network perturbations before giving up (in seconds)
        self.time_to_wait=time_to_wait

        # how many itertations are allowed when trying to add something during a single perturbation
        # note: it's unknown how many failures there could be, number set high
        # purpose is to avoid the (vanishingly small) chance that a single perturbation will block the program
        self.maxiterations = 10**4

        # use qsub or sbatch
        if qsub:
            self.scheduler = self.scheduler_qsub
        else:
            self.scheduler = self.scheduler_sbatch

        # begin
        self.start_job()


    def start_job(self):
        # get parameters and files for the perturbations
        self.params = getinfo()
        # set up folders for calculations
        self.makedirectories()
        # do perturbations if not already done
        if 'numperturbations' in self.params:
            networks = self.makenetworks()
        else:
            networks = None
        # make patterns if desired and not already done
        if 'timeseriesfile' in self.params:
            # must return network uid for each pattern
            uids,patterns = self.makepatterns(networks)
        else:
            uids,patterns = None,None
        # save networks and patterns, if any
        self.savefiles(networks,patterns,uids)
        # shell call to scheduler
        self.scheduler()

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
        return self.perturbNetwork()

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

    def makepatterns(self,networks=None):
        if networks is None:
            networklabels, uids = self.makenetworklabelsfromfiles()
        else:
            networklabels, uids = self.makenetworklabelsfromspecs(networks)
        uniqnetlab = list(set(networklabels))
        masterlabels, masterdata = self.parsetimeseries(set(itertools.chain.from_iterable(uniqnetlab)))
        uniqpatterns =[]
        for nl in uniqnetlab:
            ts_data = [masterdata[masterlabels.index(n)] for n in nl]
            uniqpatterns.append([ ExtremaPO.makeJSONstring(ts_data,nl,n=1,scalingFactor=scfc,step=0.01) for scfc in self.params['scaling_factors'] ])
        patterns = [ uniqpatterns[uniqnetlab.index(nl)] for nl in networklabels ]
        return uids, patterns

    def makenetworklabelsfromspecs(self,networks):
        networklabels = []
        for network_spec in networks:
            ns = network_spec.split('\n')
            networklabels.append(tuple([n.replace(':',' ').split()[0] for n in ns]))
        return networklabels, None

    def makenetworklabelsfromfiles(self):
        networklabels=[]
        uids=[]
        for fname in os.listdir(self.params['networkfolder']):
            uids.append(''.join([c for c in fname if c.isdigit()]))
            with open(fname,'r') as f:
                networklabels.append(tuple([l.replace(':',' ').split()[0] for l in f]))
        return networklabels, uids

    def parsetimeseries(self,desiredlabels):
        if self.params['ts_type'] == 'col':
            TSList,TSLabels,timeStepList = fileparsers.parseTimeSeriesFileCol(self.params['timeseriesfile'])
        elif self.params['ts_type'] == 'row':
            TSList,TSLabels,timeStepList = fileparsers.parseTimeSeriesFileRow(self.params['timeseriesfile'])
        if self.params['ts_truncation'] != float(-1):
            ind = timeStepList.index(self.params['ts_truncation'])
        else:
            ind = len(timeStepList)
        labels,data = zip(*[(node,TSList[TSLabels.index(node)][:ind]) for node in TSLabels if node in desiredlabels])
        return labels,data

    def savefiles(self,networks=None,patterns=None,networkuids=None):

        def savenetwork(uid,network_spec):
            nfile = os.path.join(self.NETWORKDIR, "network"+uid+".txt")
            with open(nfile,'w') as nf:
                nf.write(network_spec)

        def savepatterns(uid,pats):
            subdir = os.path.join(self.PATTERNDIR,uid)
            subprocess.call(['mkdir -p ' + subdir])
            for (pat,scfc) in zip(pats,self.scaling_factors):
                puid = '{:.{prec}f}'.format(scfc, prec=scfc_padding).replace('.','_')
                pfile = os.path.join(subdir, "pattern"+puid+".txt")
                with open(pfile,'w') as pf:
                    json.dump(pattern,pf)

        if patterns is not None:
            scfc_padding = max([len(str(s)) for s in self.scaling_factors])-2
            if networks is not None:
                N=len(str(len(networks)))
                for k,(network_spec,pats) in enumerate(zip(networks,patterns)):
                    # zero pad integer for unique id
                    uid = str(k).zfill(N)
                    savenetwork(uid,network_spec)
                    savepatterns(uid,pats)
            elif networkuids is not None:
                for (uid,pats) in zip(networkuids,patterns):
                    savepatterns(uid,pats)
            else:
                raise RuntimeError("Should not get here. Debug.")
        elif networks is not None:
            N=len(str(len(networks)))
            for k,network_spec in enumerate(networks):
                # zero pad integer for unique id
                uid = str(k).zfill(N)
                savenetwork(uid,network_spec)

    def scheduler_qsub(self):
        pass

    def scheduler_sbatch(self):
        pass

if __name__=="__main__":
    job=Job(10)