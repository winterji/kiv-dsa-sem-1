# kiv-dsa-sem-1
Distributed application built using vagrant. App consists of monitor and nodes. Monitor supplies static web page with preview of discovered nodes and their colours. Nodes cooperate, decide their own colour and inform the monitor.

## Getting started
Launch the app using script `run.sh`. Usage:

`./run.sh <nodes_count>`

If nodes count is not supplied, it will default to 6.

## Connected to network
Each node sends "hello" message using UDP broadcast whenever it connects to network. All nodes who receive the message save the new node to their list of known nodes and respond with "nodes" message that contains the list of all the known nodes to them at the time. The new node than receives information about all the nodes already in the network and creates its own list.

## Stay in touch
All nodes periodically check status of the network. They send ping message using UDP broadcast and reply with pong message whenever ping is received. Each node stores time of the last ping for all other known nodes, so they can recognize a node is down when timeout is exceeded.

## Monitor
Monitor has a static IP address that all nodes know. They periodically send information about their state and also send message about every update on them. Monitor displays it on a static web page on port 5000 that is mapped on port 8080 on the host machine.