#!/bin/bash

DIR=$1
if [[ -z "$1" ]] then
	DIR=input.csv
fi

ovsmap/bin/python csv2pronto -s ./input/$DIR -A -d ./output/out.ttl -f ttl -o ./ontology/pronto.owl
