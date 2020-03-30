import subprocess,os,json
from pathlib import Path

Path("results").mkdir(exist_ok=True)


def test_multistability():
    command = ["mpiexec", "-n", "2", "python", "../lib/NetworkPerturbations/queries/MultistabilityExists.py", "mpi_networks_ME.txt", "results", "mpi_params_ME.json"]
    output_file = "results/query_results.json"
    subprocess.check_call(command)
    results = json.load(open(output_file))
    assert(set(results) == set(["inducer1 : (inducer1) : E\ninducer2 : (inducer2) : E\nreporter : (~x3) : E\nx1 : (~inducer1)(~x3) : E\nx2 : (inducer2 + x1)(~x3) : E\nx3 : (x1 + x2) : E\n", "inducer1 : (inducer1) : E\ninducer2 : (inducer2) : E\nreporter : (x3) : E\nx1 : (inducer1 + x3) : E\nx2 : (x1)(~inducer2)(~x3) : E\nx3 : (x2 + x3) : E\n", "inducer1 : (inducer1) : E\ninducer2 : (inducer2) : E\nreporter : (x3) : E\nx1 : (~inducer1)(~x2) : E\nx2 : (x3)(~inducer2) : E\nx3 : (x2) : E\n"]))


def test_patternmatch():
    command = ["mpiexec", "-n", "2", "python", "../lib/NetworkPerturbations/queries/patternmatch.py", "mpi_networks_pm.txt", "results", "mpi_params_pm.json"]
    output_file1 = "results/query_results_PathMatchInDomainGraph_wt1_microarray_coregenes_lifepoints_interpol_trim.json"
    output_file2 = "results/query_results_PathMatchInStableFullCycle_wt1_microarray_coregenes_lifepoints_interpol_trim.json"
    subprocess.check_call(command)
    results1 = json.load(open(output_file1))
    results2 = json.load(open(output_file2))
    assert(results1 == {"SWI4 : (NDD1)(~YOX1) : E\nHCM1 : SWI4 : E\nNDD1 : HCM1 : E\nYOX1 : SWI4 : E": [[0.0, 0, 14], [0.01, 8, 14], [0.05, 5, 14]], "SWI4 : (NDD1)(~YOX1) : E\nHCM1 : SWI4 : E\nNDD1 : HCM1 : E\nYOX1 : NDD1 : E": [[0.0, 0, 4], [0.01, 0, 4], [0.05, 2, 4]]})
    assert(results2 == {"SWI4 : (NDD1)(~YOX1) : E\nHCM1 : SWI4 : E\nNDD1 : HCM1 : E\nYOX1 : SWI4 : E": [[0.0, 0, 2, 14], [0.01, 2, 2, 14], [0.05, 1, 2, 14]], "SWI4 : (NDD1)(~YOX1) : E\nHCM1 : SWI4 : E\nNDD1 : HCM1 : E\nYOX1 : NDD1 : E": [[0.0, 0, 0, 4], [0.01, 0, 0, 4], [0.05, 0, 0, 4]]})


def test_count_stableFCln():
    command = "python ../lib/NetworkPerturbations/queries/CountStableFC_large_networks.py mpi_networks_FCln.txt results mpi_params_FCln.json"
    output_file = "results/query_results.json"
    subprocess.check_call(command,shell=True)
    results = json.load(open(output_file))
    assert(results == {"SWI4 : (NDD1)(~YOX1) : E\nHCM1 : SWI4 : E\nNDD1 : HCM1 : E\nYOX1 : SWI4 : E": [2, 14], "SWI4 : (NDD1)(~YOX1) : E\nHCM1 : SWI4 : E\nNDD1 : HCM1 : E\nYOX1 : NDD1 : E": [0, 4]})


def test_count_stableFC():
    command = ["mpiexec", "-n", "2", "python", "../lib/NetworkPerturbations/queries/CountStableFC.py", "mpi_networks_FCln.txt", "results", ""]
    output_file = "results/query_results.json"
    subprocess.check_call(command)
    results = json.load(open(output_file))
    assert(results == {"SWI4 : (NDD1)(~YOX1) : E\nHCM1 : SWI4 : E\nNDD1 : HCM1 : E\nYOX1 : SWI4 : E": [2, 14], "SWI4 : (NDD1)(~YOX1) : E\nHCM1 : SWI4 : E\nNDD1 : HCM1 : E\nYOX1 : NDD1 : E": [0, 4]})



if __name__ == "__main__":
    test_count_stableFC()