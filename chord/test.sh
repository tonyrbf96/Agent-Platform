#!/bin/bash
# for use xterm execute: sudo apt-get install xterm
# then: ./test.sh create 10 9000

create(){
for (( i=0; i<$1; i++ )); do
new $(($i * 10)) $2 0 $2
done
}

new(){
xterm -e bash -c "source $PWD/test.sh; ./test.sh run_node_from_uri $1 $2 $3 $4; bash" &
}

run_node_from_uri(){
python start_node.py $1 $2 $3 $4
}

run_node(){
port=$(($2 + $1))
python start_node.py $1 127.0.0.1 $port $3 127.0.0.1 $4
}

"$@"