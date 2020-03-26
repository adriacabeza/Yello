#!/usr/bin/env bash
git clone https://github.com/thtrieu/darkflow.git
cd darkflow
python3 setup.py build_ext --inplace
pip install .
cd ..
rm -rf darkflow
echo "Done!"
