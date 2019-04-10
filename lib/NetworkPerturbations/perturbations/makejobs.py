import NetworkPerturbations.perturbations.networkperturbations as perturb
import NetworkPerturbations.perturbations.fileparsers as fileparsers
import subprocess, os, json, shutil, ast, importlib,sys

class Job():

    def __init__(self,paramfile):
        self.paramfile = paramfile
        self.params = json.load(open(paramfile))
        # use datetime as unique identifier to avoid overwriting
        if "datetime" not in self.params:
            datetime = subprocess.check_output(['date +%Y_%m_%d_%H_%M_%S'],shell=True).decode(sys.stdout.encoding).strip()
        else:
            datetime = self.params["datetime"]
        if "computationsdir" not in self.params:
            self.params["computationsdir"] = ""
        if self.params['numperturbations']:
            self.perturbationsdir = os.path.join(os.path.expanduser(self.params["computationsdir"]),
                                                    "perturbations"+datetime)
            os.makedirs(self.perturbationsdir)
        if"querymodule" in self.params and "querymodule_args" in self.params and self.params["querymodule"]:
            self.queriesdir = os.path.join(os.path.expanduser(self.params["computationsdir"]),
                                                    "queries"+datetime)
            os.makedirs(self.queriesdir)
        self.inputfilesdir = os.path.join(os.path.expanduser(self.params["computationsdir"]),
                                                "inputs"+datetime)
        os.makedirs(self.inputfilesdir)
        # save parameter file to computations folder
        shutil.copy(self.paramfile,self.inputfilesdir)
        shutil.copy(self.params["networkfile"], self.inputfilesdir)
        #TODO: Record versions/git number of DSGRN and NetworkPerturbations

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
        # perform perturbations if requested
        if self.params['numperturbations']:
            print("\nPerturbations beginning.\n")
            sys.stdout.flush()
            # do perturbations if not already done
            self._parsefile('edge',fileparsers.parseEdgeFile)
            self._parsefile('node',fileparsers.parseNodeFile)
            perturbed_networks = []
            for network_spec in networks:
                perturbed_networks.extend(perturb.perturbNetwork(self.params,network_spec))
            networks=list(set(perturbed_networks))
            with open(os.path.join(self.perturbationsdir,"networks.txt"),"w") as f:
                f.write(str(networks))
            print("\nPerturbations complete.\n")
            sys.stdout.flush()
        # perform queries if requested
        if "querymodule" in self.params and "querymodule_args" in self.params and self.params["querymodule"]:
            print("\nQueries beginning.\n")
            sys.stdout.flush()
            query = importlib.import_module("..queries."+self.params["querymodule"],"NetworkPerturbations.perturbations")
            query.query(networks,self.queriesdir,self.params["querymodule_args"])
            print("\nQueries complete.\n")
            sys.stdout.flush()



