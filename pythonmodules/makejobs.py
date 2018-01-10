import networkperturbations as perturb
import subprocess, os, json, itertools, shutil


class Job():

    def __init__(self,paramfile):
        self.paramfile = paramfile
        self.params = json.load(open(paramfile))

    def prep(self):
        # set up folders for calculations
        self._makedirectories()
        # do perturbations if not already done
        if 'numperturbations' in self.params:
            self._parsefilesforperturbation()
            networks = perturb.perturbNetwork(self.params)
        else:
            networks = None
        # make patterns if desired and not already done
        if 'timeseriesfile' in self.params:
            # must return network uid for each pattern
            uids,patterns = self._makepatterns(networks)
        else:
            uids,patterns = None,None
        # save networks and patterns, if any
        self._savefiles(networks,patterns,uids)


    def run(self):
        # do perturbations
        # do query
        pass

    def _makedirectories(self):
        # use datetime as unique identifier to avoid overwriting
        DATETIME = subprocess.check_output(['date +%Y_%m_%d_%H_%M_%S'],shell=True).strip()
        path = os.path.join(os.path.expanduser(self.params["computationsdir"]),"computations"+DATETIME)
        # save initial parameter file to computations folder
        shutil.copyfile(self.paramfile,path)
        # make results directory and network directory (if not specified)
        self.params['resultsdir'] =os.path.join(path,"results")
        os.makedirs(self.params['resultsdir'])
        if 'networkfolder' not in self.params:
            self.params['networkfolder']=os.path.join(path, "networks")
            os.makedirs(self.params['networkfolder']

    def _parsefilesforperturbation(self):
        network_spec = open(self.params['networkfile'],'r').read()
        while network_spec[-1]=='\n': network_spec = network_spec[:-1]
        self.params['network_spec'] = network_spec
        if 'edgefile' in self.params:
            self.params['edgelist'] = fileparsers.parseEdgeFile(self.params['edgefile'])
        else:
            self.params['edgelist'] = None
        if 'nodefile' in self.params:
            self.params['nodelist'] = fileparsers.parseNodeFile(self.params['nodefile'])
        else:
            self.params['nodelist'] = None





    def _savefiles(self,networks=None,patterns=None,networkuids=None):

        def savenetwork(uid,network_spec):
            nfile = os.path.join(self.NETWORKDIR, "network"+uid+".txt")
            open(nfile,'w').write(network_spec)

        def savepatterns(uid,pats):
            subdir = os.path.join(self.PATTERNDIR,uid)
            subprocess.call(['mkdir -p ' + subdir],shell=True)
            for (pat,scfc) in zip(pats,self.params['scaling_factors']):
                puid = '{:.{prec}f}'.format(scfc, prec=scfc_padding).replace('.','_')
                pfile = os.path.join(subdir, "pattern"+puid+".txt")
                json.dump(pat,open(pfile,'w'))

        if patterns is not None:
            scfc_padding = max(max([len(str(s)) for s in self.params['scaling_factors']])-2, 0)
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
       
        