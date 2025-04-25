#
# Simple backend service demo
#

from time import sleep, time
from flask import Flask, render_template, request, jsonify
import socket

app = Flask(__name__)

nodes_status = {}
nodes_ip = {}
last_updates = {}

TIMEOUT_FOR_UPDATE = 10

def check_update_timeouts():
    for node_id in last_updates:
        if time() - last_updates[node_id] > TIMEOUT_FOR_UPDATE:
            del nodes_status[node_id]
            del nodes_ip[node_id]
            del last_updates[node_id]


@app.route('/')
def home():
    check_update_timeouts()
    page = render_template("index.html", nodes=nodes_status, nodes_ip=nodes_ip)
    return page


@app.route("/update", methods=["POST"])
def update_state():
    data = request.json
    node_id = data.get("node_id")
    node_ip = request.remote_addr
    state = data.get("state")

    if node_id and state:
        nodes_status[node_id] = state
        nodes_ip[node_id] = node_ip
        last_updates[node_id] = time()
        return jsonify({"status": "ok"}), 200
    return jsonify({"error": "Missing data"}), 400

if __name__ == '__main__':
    app.run(host="0.0.0.0")

# EOF
