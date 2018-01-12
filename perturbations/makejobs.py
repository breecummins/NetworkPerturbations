import networkperturbations as perturb
import fileparsers
import subprocess, os, json, shutil, ast, importlib,sys
sys.path.append("../queries")
# call function from within inputfiles/

class Job():

    def __init__(self,paramfile):
        self.paramfile = paramfile
        self.params = json.load(open(paramfile))
        # use datetime as unique identifier to avoid overwriting
        datetime = subprocess.check_output(['date +%Y_%m_%d_%H_%M_%S'],shell=True).strip()
        computationsdir_datetime = os.path.join(os.path.expanduser(self.params["computationsdir"]),"computations"+datetime)
        os.makedirs(computationsdir_datetime)
        self.inputfilesdir = os.path.join(computationsdir_datetime,"inputfiles")
        os.makedirs(self.inputfilesdir)
        # save parameter file to computations folder
        shutil.copy(self.paramfile,self.inputfilesdir)
        #TODO: Record versions/git number of DSGRN and NetworkPerturbations
        self.resultsdir =os.path.join(computationsdir_datetime,"results")
        os.makedirs(self.resultsdir)

    def _parsefile(self,eorn,parsefunc):
        f = eorn+"file"
        l = eorn+"list"
        if f in self.params and self.params[f].strip():
            try:
                self.params[l] = parsefunc(self.params[f])
                shutil.copy(self.params[f], self.inputfilesdir)
            except:
                raise ValueError("Invalid " + eorn + " file.")
        else:
            self.params[l] = None

    def run(self):
        # read network file
        networks = open(self.params["networkfile"]).read()
        if networks[0] == "[":
            networks = ast.literal_eval(networks)
        else:
            while networks[-1] == '\n':
                networks = networks[:-1]
            networks = [networks]
        # perform perturbations if needed
        if self.params['makeperturbations']:
            # do perturbations if not already done
            self._parsefile('edge',fileparsers.parseEdgeFile)
            self._parsefile('node',fileparsers.parseNodeFile)
            perturbed_networks = []
            for network_spec in networks:
                perturbed_networks.extend(perturb.perturbNetwork(self.params,network_spec))
            networks=list(set(perturbed_networks))
            print("\nPerturbations complete; queries beginning.\n")
            sys.stdout.flush()
        query = importlib.import_module(self.params["querymodule"])
        query.query(networks,self.resultsdir,self.params)



