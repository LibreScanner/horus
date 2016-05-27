#!/bin/bash

make clean -e SPHINXOPTS="-D language='$1'" html
