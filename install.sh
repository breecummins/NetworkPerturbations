# installer script
git submodule init
git submodule update --merge
pip uninstall -y NetworkPerturbations &> /dev/null || True
pip install -e .
