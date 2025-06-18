#! /bin/bash

number=$(ps -ef | grep ncat -c)
if [[ $number -eq 1 ]]; then
    ncat -l -p 1299 -c /var/app/current/challenges/Reverse\ engineering/In\ good\ form/a.out &
    echo "restarted";
else
    echo "still running"
fi


