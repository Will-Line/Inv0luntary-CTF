#! /bin/bash

number=$(netstat -ano | grep 0.0.0.0:$1 | wc -l)

echo $number
if [[ $number -lt 3 ]]; then
    ncat -l -p $1 -c ~/Documents/a.out &
    echo "restarted";
else
    echo "still running"
fi


