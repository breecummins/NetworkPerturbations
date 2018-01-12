import networkperturbations as perturb
import fileparsers
import subprocess, os, json, shutil, ast, importlib,sys
sys.path.append(".")

class Job():

    def __init__(self,paramfile):
        self.paramfile = paramfile
        self.params = json.load(open(paramfile))
        # if ('networkfolder' in self.params and self.params['networkfolder'].strip()) and
        #     ('networkfile' in self.params and self.params['networkfile'].strip()):
        #     raise ValueError("Exactly one of networkfolder and networkfile must be specified.")
        # use datetime as unique identifier to avoid overwriting
        datetime = subprocess.check_output(['date +%Y_%m_%d_%H_%M_%S'],shell=True).strip()
        computationsdir_datetime = os.path.join(os.path.expanduser(self.params["computationsdir"]),"computations"+datetime)
        os.makedirs(computationsdir_datetime)
        self.inputfilesdir = os.path.join(computationsdir_datetime,"inputfiles")
        os.makedirs(self.inputfilesdir)
        # save parameter and query files to computations folder
        shutil.copy(self.paramfile,self.inputfilesdir)
        shutil.copy(self.params["queryfile"],self.inputfilesdir)
        #TODO: Record versions/git number of DSGRN and NetworkPerturbations
        self.resultsdir =os.path.join(computationsdir_datetime,"results")
        os.makedirs(self.resultsdir)

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
            self._parsefilesforperturbation()
            perturbed_networks = []
            for network_spec in networks:
                perturbed_networks.extend(perturb.perturbNetwork(self.params,network_spec))
            perturbed_networks=list(set(perturbed_networks))
            # json.dump(perturbed_networks,open(os.path.join(self.computationsdir_datetime,"networklist.json")))
        # else:
            # copy networks to computations folder
            # shutil.copyfile(self.paramfile["networkfile"],os.path.join(self.computationsdir_datetime,"networklist.json"))

        query = self.params["queryfile"][:-3]
        query = importlib.import_module(query)
        query.query(networks,self.resultsdir)

    def _parsefilesforperturbation(self):

        def parse(eorn,parsefunc):
            f = eorn+"file"
            l = eorn+"list"
            if f in self.params and self.params[f].strip():
                try:
                    self.params[l] = parsefunc(self.params[f])
                    shutil.copy(self.params[f], self.inputfilesdir)
                except:
                    raise ValueError("Invalid" + eorn + "file.")
            else:
                self.params[l] = None

        parse('edge',fileparsers.parseEdgeFile)
        parse('node',fileparsers.parseNodeFile)

