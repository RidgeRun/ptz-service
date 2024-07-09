#!/bin/bash

# This script has to be called from the root of the repository

if [[ $# -eq 0 ]] ; then
    echo "Usage: $0 <VERSION_NUMBER>"
    exit 0
fi

VERSION=${1}

# ##  PTZ Microservice 0.0.0
sed -i "s/##  PTZ Microservice [[:digit:]]\+\.[[:digit:]]\+\.[[:digit:]]\+/##  PTZ Microservice ${VERSION}/g" README.md
#version="a.b.c"
sed -i "s/version=\"[[:digit:]]\+\.[[:digit:]]\+\.[[:digit:]]\+\"/version=\"${VERSION}\"/g" setup.py
# release = 'a.b.c'
sed -i "s/release = '[[:digit:]]\+\.[[:digit:]]\+\.[[:digit:]]\+'/release = '${VERSION}'/g" docs/source/conf.py
# version: a.b.c
sed -i "s/version: [[:digit:]]\+\.[[:digit:]]\+\.[[:digit:]]\+/version: ${VERSION}/g" api/openapi.yaml
# Welcome to PTZ Microservice documentation va.b.c
sed -i "s/Welcome to PTZ Microservice documentation v[[:digit:]]\+\.[[:digit:]]\+\.[[:digit:]]\+/Welcome to PTZ Microservice documentation v${VERSION}/g" docs/source/index.rst
