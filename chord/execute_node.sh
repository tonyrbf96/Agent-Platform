#!/bin/bash

create(){
for (( i=0; i<$1; i++ )); do
new $i $2
done
}

new(){
xterm -e bash -c "source $PWD/execute_node.sh; ./execute_node.sh run_node $1 $2; bash" &
}


run_node(){
port=$(($2 + $1))
echo $port
python start_node.py $1 127.0.0.1 $port 0 127.0.0.1 $2
}
"$@"