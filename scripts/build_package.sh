#!/bin/sh

rm -rf pywsdp
pip3 install pywsdp -t . --no-deps --upgrade
rm -rf tests pywsdp-*.dist-info
find pywsdp/ -name __pycache__ -exec rm -rf {} \;

pb_tool zip

exit 0
 
