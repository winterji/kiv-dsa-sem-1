#
# Simple backend service demo
#

from time import sleep, time
import threading
import requests
import socket
import math

# TODO - timeout of each node and check it periodically
# TODO - trigger state change - network changed

MONITOR_URL = "http://10.0.1.10:5000/update"
NODE_ID = socket.gethostname()
states = ["red", "green"]
current_state = "red"
known_ids = {}
locked = False
locked_for_write = False
pings = []
LOCK_TIMEOUT = 0.001
PING_PERIOD = 10
PING_TIMEOUT = 2
PING_CHECK_PERIOD = 0.5

def read_known_ids():
    global locked, locked_for_write
    while locked:
        sleep(LOCK_TIMEOUT)
    locked_for_write = True

def read_known_ids_finish():
    global locked_for_write
    locked_for_write = False

def lock_known_ids():
    global locked, locked_for_write
    while locked or locked_for_write:
        sleep(LOCK_TIMEOUT)
    locked = True

def unlock_known_ids():
    global locked
    locked = False

def get_known_nodes():
    read_known_ids()
    msg = b",".join([i.encode('utf-8') + b":" + known_ids[i].encode('utf-8') for i in known_ids])
    read_known_ids_finish()
    return msg

def send_msg(msg, sendTo):
    # send message to the node with ID sendTo
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    if type(msg) == str:
        msg = msg.encode('utf-8')
    sock.sendto(msg, (sendTo, 52000))
    sock.close()

def send_hello():
    # send hello request with my ID to every node in the network
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    hello = b"hello " + NODE_ID.encode('utf-8')
    sock.sendto(hello, ('10.0.1.255', 52000))
    sock.close()

def send_ping():
    while True:
        # send ping to every node in the network via broadcast
        ping_msg = b"ping " + NODE_ID.encode('utf-8')
        send_msg(ping_msg, '10.0.1.255')
        for node_id in known_ids:
            if node_id == NODE_ID:
                continue
            pings.append({"node_id": node_id, "time": time()})
        
        sleep(PING_PERIOD)

def recv_ping(node_id, recvFrom):
    # receive ping from other nodes
    # send pong to the node that sent the ping
    if node_id != NODE_ID:
        node_discovered(node_id, recvFrom[0])
        pong_msg = b"pong " + NODE_ID.encode('utf-8')
        send_msg(pong_msg, recvFrom[0])
        print(f"Received ping from {node_id}, sending pong")
    else:
        print("Received ping from myself")
        return

def recv_pong(node_id, recvFrom):
    if node_id in known_ids:
        for ping in pings:
            if ping["node_id"] == node_id:
                # remove from pings
                print(f"Received pong from {node_id}, removing from pings")
                pings.remove(ping)
                break
    node_discovered(node_id, recvFrom[0])

def recv_hello(node_id, recvFrom):
    read_known_ids()
    if node_id not in known_ids:
        read_known_ids_finish()
        node_discovered(node_id, recvFrom[0])
        # send all known nodes to the newly discovered node
        # 1. send the list of known nodes
        msg = b"nodes " + get_known_nodes()
        send_msg(msg, recvFrom[0])
    else:
        read_known_ids_finish()

def recv_nodes(nodes):
    for node in nodes:
        node_id = node.split(":")[0]
        node_addr = node.split(":")[1]
        read_known_ids()
        if node_id not in known_ids:
            read_known_ids_finish()
            node_discovered(node_id, node_addr)
        else:
            read_known_ids_finish()

def node_discovered(node_id, addr):
    # add the node to the list of known nodes
    read_known_ids()
    if node_id not in known_ids:
        read_known_ids_finish()
        lock_known_ids()
        known_ids[node_id] = addr
        unlock_known_ids()
        print(f"Discovered node: {node_id}")
        print("known nodes:", known_ids)
        determine_color()
    else:
        read_known_ids_finish()

def node_lost(node_id):
    read_known_ids()
    if node_id in known_ids:
        read_known_ids_finish()
        lock_known_ids()
        del known_ids[node_id]
        unlock_known_ids()
        print(f"Lost node: {node_id}")
        print("known nodes:", known_ids)
        determine_color()
    else:
        read_known_ids_finish()

def check_ping_timeouts():
    # check if any pings are older than PING_TIMEOUT
    while True:
        sleep(PING_CHECK_PERIOD)
        for ping in pings:
            if time() - ping["time"] > PING_TIMEOUT:
                print(f"Ping timeout for {ping['node_id']}")
                pings.remove(ping)
                node_lost(ping['node_id'])

def listen():
    # listen for hello requests from other nodes
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', 52000))
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            if data.startswith(b"hello"):
                node_id = data.split()[1].decode()
                recv_hello(node_id, addr)
            elif data.startswith(b"nodes"):
                # receive the list of known nodes
                nodes = data.split()[1].decode().split(",")
                recv_nodes(nodes)
            elif data.startswith(b"ping"):
                node_id = data.split()[1].decode()
                recv_ping(node_id, addr)
            elif data.startswith(b"pong"):
                node_id = data.split()[1].decode()
                recv_pong(node_id, addr)
        except socket.timeout:
            break
    sock.close()

def init_network():
    lock_known_ids()
    known_ids[NODE_ID] = socket.gethostbyname(socket.gethostname())
    unlock_known_ids()

    # listen for incoming messages parallely
    listen_thread = threading.Thread(target=listen)
    listen_thread.daemon = True
    listen_thread.start()

    sleep(5)   # Wait for the monitor to start
    send_hello()  # Send hello to all nodes
    
    # wait for a while to receive hello messages and send hello again to ensure all nodes are discovered
    sleep(2)
    send_hello()

    # ping tests
    listen_thread = threading.Thread(target=send_ping)
    listen_thread.daemon = True
    listen_thread.start()

    # timeouts
    listen_thread = threading.Thread(target=check_ping_timeouts)
    listen_thread.daemon = True
    listen_thread.start()

def determine_color():
    global current_state
    read_known_ids()
    # sort known_ids
    # sorted_ids = sorted(known_ids, key=lambda d: int(d["node_id"].split("-")[1]))
    sorted_ids = sorted(known_ids)
    print(f"Sorted IDs: {sorted_ids}")
    read_known_ids_finish()
    N = len(sorted_ids)
    num_red = math.ceil(N / 3)
    my_index = sorted_ids.index(NODE_ID)
    new_state = 'red' if my_index < num_red else 'green'
    if new_state != current_state:
        current_state = new_state
        send_state(current_state)
        print(f"New state: {current_state}")
    return current_state

def send_state(state):
    try:
        response = requests.post(MONITOR_URL, json={
            "node_id": NODE_ID,
            "state": state
        })
        print(f"Sent state '{state}', got: {response.text}")
    except Exception as e:
        print(f"Failed to send update: {e}")

if __name__ == "__main__":
    init_network()
    current_state = determine_color()
    print(f"Initial state: {current_state}")
    send_state(current_state)
    while True:
        sleep(10)
        print(f"Current state: {current_state}")
        send_state(current_state)


# EOF
