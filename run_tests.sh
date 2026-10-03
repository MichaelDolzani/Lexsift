#!/bin/bash
export LEXSIFT_DEBUG=__tests
source env/bin/activate
pip install .
rm -rf testdir
python -m pytest tests
deactivate
unset LEXSIFT_DEBUG
