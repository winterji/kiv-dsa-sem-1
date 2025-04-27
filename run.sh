#!/bin/bash

if [ -z "$1" ]; then
  export NODES=6
  echo "No nodes specified, defaulting to 6"
else
    export NODES=$1
    echo "Running with $NODES nodes"
fi

vagrant up