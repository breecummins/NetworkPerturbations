# installer script
rm -rf build
rm -rf dist
git submodule update --init --recursive
pip uninstall -y NetworkPerturbations &> /dev/null || True
pip install . --upgrade --no-deps --force-reinstall --no-cache-dir $@
