#!/usr/bin/env bash
set -e

mkdir -p packages

docker build -t package-builder .
docker run -v `pwd`/packages:/packages -it package-builder
