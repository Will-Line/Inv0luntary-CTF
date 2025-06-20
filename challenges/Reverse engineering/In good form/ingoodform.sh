#! /bin/bash

number=$(netstat -ano | grep 0.0.0.0:$1 | wc -l)

echo $number
if [[ $number -lt 3 ]]; then
    ncat -l involuntaryctf.net -p $1 -c '/var/app/current/challenges/Reverse\ engineering/In\ good\ form/a.out' &
    echo "restarted";
else
    echo "still running"
fi

