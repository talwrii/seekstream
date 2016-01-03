#!/bin/bash
here=$(dirname ${BASH_SOURCE[0]})
cd $here
nosetests --with-coverage --cover-min-percent 100
