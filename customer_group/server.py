from CustomerMember import CustomerMember
from CustomerMember import FOLLOWER, LEADER
from flask import Flask, request, jsonify
import sys
import logging

app = Flask(__name__)


# value_get is the flask handle
@app.route("/request", methods=['GET'])
def value_get():
    payload = request.json["payload"]
    print(payload)
    reply = {"code": 'fail', 'payload': payload}
    if n.status == LEADER:
        # request handle, reply is a dictionary
        result = n.handle_get(payload)
        if result:
            reply = {"code": "success", "payload": result}
    elif n.status == FOLLOWER:
        # redirect request
        reply["payload"]["message"] = n.leader
    # return jsonify(reply)
    return result


@app.route("/request", methods=['PUT'])
def value_put():
    payload = request.json["payload"]
    reply = {"code": 'fail'}

    if n.status == LEADER:
        # request handle, reply is a dictionary
        result = n.handle_put(payload)
        print(result)
        if result:
            reply = {'result': result}
    elif n.status == FOLLOWER:
        # redirect request
        payload["message"] = n.leader
        reply["payload"] = payload
    print("From the group member cluster")
    print(reply)
    return jsonify(reply)


# we reply to vote request
@app.route("/vote_req", methods=['POST'])
def vote_req():
    # also need to let me know whether up-to-date or not
    term = request.json["term"]
    commitIdx = request.json["commitIdx"]
    staged = request.json["staged"]
    sender_id = request.json["id"]
    choice, term = n.decide_vote(term, commitIdx, staged, sender_id)
    message = {"choice": choice, "term": term}
    return jsonify(message)


@app.route("/heartbeat", methods=['POST'])
def heartbeat():
    term, commitIdx, id = n.heartbeat_follower(request.json)
    # return anyway, if nothing received by leader, we are dead
    message = {"term": term, "commitIdx": commitIdx, "id": id}
    return jsonify(message)


# disable flask logging
log = logging.getLogger('werkzeug')
log.disabled = False

if __name__ == "__main__":
    # python server.py index ip_list
    if len(sys.argv) == 3:
        index = int(sys.argv[1])
        ip_list_file = sys.argv[2]
        ip_list = []
        # open ip list file and parse all the ips
        with open(ip_list_file) as f:
            for ip in f:
                ip_list.append(ip.strip())
        my_ip = ip_list.pop(index)

        http, host, port = my_ip.split(':')
        # initialize node with ip list and its own ip
        n = CustomerMember(ip_list, my_ip, index)
        app.run(host="localhost", port=int(port), debug=False)
    else:
        print("usage: python server.py <index> <ip_list_file>")
