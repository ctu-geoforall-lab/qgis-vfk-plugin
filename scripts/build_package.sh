#!/bin/bash -e

VENV=/tmp/qgis-vfk-plugin
python3 -m venv $VENV
source $VENV/bin/activate

pip3 install -r scripts/requirements.txt 

LIB=$VENV/lib/python3.11/site-packages/
cp -r $LIB/pywsdp $LIB/zeep $LIB/isodate $LIB/platformdirs $LIB/requests_toolbelt $LIB/requests_file.py .
find pywsdp zeep isodate platformdirs requests_toolbelt \
     -name __pycache__ | xargs rm -rf

pb_tool zip

deactivate
rm -rf $VENV

exit 0
 
