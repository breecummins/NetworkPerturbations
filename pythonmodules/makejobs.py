import networkperturbations as perturb
import fileparsers
import subprocess, os, json, shutil, ast, importlib


class Job():

    def __init__(self,paramfile):
        self.paramfile = paramfile
        self.params = json.load(open(paramfile))
        if ('networkfolder' in self.params and self.params['networkfolder'].strip()) and
            ('networkfile' in self.params and self.params['networkfile'].strip()):
            raise ValueError("Exactly one of networkfolder and networkfile must be specified.")
        # use datetime as unique identifier to avoid overwriting
        datetime = subprocess.check_output(['date +%Y_%m_%d_%H_%M_%S'],shell=True).strip()
        computationsdir_datetime = os.path.join(os.path.expanduser(self.params["computationsdir"]),"computations"+datetime)
        # save parameter and query files to computations folder
        shutil.copyfile(self.paramfile,computationsdir_datetime)
        shutil.copyfile(self.params["queryfile"],computationsdir_datetime)
        #TODO: Record versions/git number of DSGRN and NetworkPerturbations
        self.params["computationsdir_datetime"] = computationsdir_datetime
        self.params['resultsdir'] =os.path.join(computationsdir_datetime,"results")
        os.makedirs(self.params['resultsdir'])

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
            json.dump(perturbed_networks,open(os.path.join(self.params["computationsdir_datetime"],"networklist.json")))
        else:
            # copy networks to computations folder
            shutil.copyfile(self.paramfile["networkfile"],os.path.join(self.params["computationsdir_datetime"],"networklist.json"))
        query = self.params["queryfile"]
        importlib.import_module(query)
        query.query(self.params,networks)

    def _parsefilesforperturbation(self):
        if 'edgefile' in self.params and self.params["edgefile"].strip():
            try:
                self.params['edgelist'] = fileparsers.parseEdgeFile(self.params['edgefile'])
            except:
                raise ValueError("Invalid edge file.")
        else:
            self.params['edgelist'] = None
        if 'nodefile' in self.params and self.params["nodefile"].strip():
            try:
                self.params['nodelist'] = fileparsers.parseNodeFile(self.params['nodefile'])
            except:
                raise ValueError("Invalid node file.")
        else:
            self.params['nodelist'] = None

