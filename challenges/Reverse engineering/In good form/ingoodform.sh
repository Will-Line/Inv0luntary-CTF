#! /bin/bash

number=$(ps -ef | grep ncat -c)
if [[ $number -lt 500 ]]; then
    ncat -l -p $1 -c ~/Documents/a.out &
    echo "restarted";
else
    echo "still running"
fi


