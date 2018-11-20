# installer script
git submodule update --init --recursive --remote --merge
pip uninstall -y NetworkPerturbations &> /dev/null || True
pip install -e .
