#!/bin/bash

pip3 install -r scripts/requirements.txt

rm -rf pywsdp zeep requests_file.py isodate platformdirs requests_toolbelt
pip3 install pywsdp zeep requests-file isodate platformdirs requests-toolbelt \
     -t . --no-deps --upgrade
# fix pywsdp (remove when 2.1.1 will be released)
cp ../pywsdp/pywsdp/base/__init__.py pywsdp/base/__init__.py
find pywsdp zeep isodate platformdirs requests_toolbelt \
     -name __pycache__ | xargs rm -rf

pb_tool zip

exit 0
 
