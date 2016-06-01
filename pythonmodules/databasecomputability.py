#FIXME -- import dsgrn

import subprocess

def checkComputability(network_spec,maxparams):
    try:
        sentence = subprocess.check_output(['dsgrn','network', network_spec,'parameter'],shell=False)
        numparams = [int(s) for s in sentence.split() if s.isdigit()][0]
        return (numparams <= int(maxparams))
    except:
        return False
