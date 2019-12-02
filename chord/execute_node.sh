#!/bin/bash
port=$2
echo $port

for (( i=0; i<$1; i++ )); do
python start_node.py $i 127.0.0.1 $port$i 0 127.0.0.1 ${port}0 &
done