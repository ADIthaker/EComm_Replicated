import sys
import copy
import os
from dotenv import load_dotenv
load_dotenv(override=True)
sys.path.append(os.environ.get("DIR"))

from collections import defaultdict
import socket
import pickle
from utils.database import CustomerDatabase
import queue
from apis.buyer_api import BuyerAPIs
from apis.seller_api import SellerAPIs
import logging



class Member():
    def __init__(self, id, addr, cust_db, n, mem_ls):
        self.mem_ls = mem_ls
        self.recvd_consensus = []
        self.reached_consensus = []
        self.consensus_round = 0
        self.id = id        
        self.n = n
        self.cust_db = cust_db
        self.IP = addr[0]
        self.PORT = addr[1]
        self.addr = addr
        self.local_no = 0
        self.consensus = [0 for _ in range(self.n)]
        self.unassgn_global = []
        self.buyer_api = BuyerAPIs(cust_db, None)
        self.seller_api = SellerAPIs(cust_db, None)
        self.func_to_ptr = {
            "create_buyer": self.buyer_api.create_buyer
        }

        self.requests = {}
        self.sequences = {}
        self.req_func = {}


        self.original_sender = None
        #dict that stores the latest local no of each process from the request messages I recv or send

        self.local_state = defaultdict(lambda: -1) # stores the latest local seq no from s_id, when I recv a request message from some process.
        self.global_state = dict() # stores the req_id for a given global seq number, this is only stored when a seq message is recvd and all req messges upto this ones req_id are recvd.
        self.local_global = defaultdict(lambda: -1)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.IP, self.PORT)) # open a UDP socket

        #how do I detect if a request message is omitted? Need to agree on global no before hand use global variable here and send it as lock to each member
        # what was the global seq no of the last message you delivered/assigned a global seq number to?
        self.last_delivered = -1
        self.last_global_recvd = 0

    def recv(self):
        while True:
            #recv request message and check if its k mod n, if yes then send sequence message else listen for sequence message
            packet = self.sock.recvfrom(10000)
            ser_msg, sender_addr = packet
            msg = pickle.loads(ser_msg)
            if msg['msg_type'] == "submit_request":
                self.original_sender = sender_addr
                self.send_req(msg)
            elif msg['msg_type'] == "request":
                self.recv_req(sender_addr, msg)
            elif msg['msg_type'] == "sequence":
                self.recv_seq(sender_addr, msg)
            elif msg['msg_type'] == 'retransmit':
                self.recv_retransmit_req(sender_addr, msg)

            # check request message for retransmit and also check sequence message for retransmit
# to check condition 2:
# I need to store what was the latest I recv
    def send_req(self, msg):
        print("got a request", self.id)
        if len(self.unassgn_global) == 0:
            func, args = msg["request"]
            req_msg = {
                "msg_type": 'request',
                "request_id": (self.id, self.local_no),
                "id": self.id,
                "local_k": self.local_global[self.id],
                "request": (func, args),
            }
            self.local_no += 1
            self.requests[req_msg["request_id"]] = req_msg
            ser_request = pickle.dumps(req_msg)
            for mem in self.mem_ls:
                if (self.IP, self.PORT) != mem:
                    try:
                        self.sock.sendto(ser_request, mem)
                    except Exception as e:
                        print(e)

            self.unassgn_global.append(req_msg["request_id"])
        else:
            print("Unassigned is not empty", self.unassgn_global)
            pass
        '''
        If unassgn_global is not empty, ask to retransmit its sequence number. This ensures that no request message is sent if previous request is not assigned a number yet.
        Problem: If assigner node has crashed, nothing will work
        
        add this message to unassgn_global
        '''
    def recv_req(self, sender_addr, msg):
        print("got a request message", self.id, msg["request_id"], msg)
        self.local_state[msg["request_id"][0]] = msg["request_id"][1]
        self.local_global[msg["request_id"][0]] = msg["local_k"]
        if self.id == (self.local_global[self.id])%self.n:
            self.send_seq(msg)
        else:
            print("Got a receive messsage but dont have to send a sequence message")
    
    def recv_seq(self, sender_addr, msg):
        req_id = msg["request_id"]
        print("got a sequence message", self.id, req_id)
        if self.local_state[req_id[0]] < req_id[1] - 1:
            print("WANTS", (req_id[0], self.local_state[req_id[0]]))
            self.send_retransmit_req((req_id[0], self.local_state[req_id[0]]), True)
            # im missing request messages, and the range is from the value in the dict to this value.
        elif self.local_state[req_id[0]] == req_id[1] - 1:
            print("GOT APT SEQ MESSAGE", self.id, msg)
            self.last_global_recvd = msg["sequence_id"]
            print(self.local_global[self.id], msg["sequence_id"] - 1)
            if self.local_global[self.id] == msg["sequence_id"] - 1:
                self.local_global[self.id] = msg["sequence_id"]
                self.global_state[msg["sequence_id"]] = req_id
                self.local_global[msg["request_id"][0]] = msg["sequence_id"]
                self.req_func[msg["sequence_id"]] = msg["request"]
                self.sequences[msg["sequence_id"]] = msg 
                
                print(self.last_delivered, msg["sequence_id"]-1)
                self.try_deliver(msg["sequence_id"], req_id)
            else: # ask to retransmit the seq messages i dont have
                print("WANTS", self.local_global[self.id]+1)
                self.send_retransmit_req(self.local_global[self.id]+1, False)
            # add logic to deliver according to the local_global dict. 
                #update necessary things for a normal seq message recv

    def try_deliver(self, seq_no, req_id):
        if self.last_delivered == seq_no-1:
            print("GLOBAL STATE", self.global_state)
            if req_id in self.global_state.values(): # request message has been assigned global no, this means I recieved this request message
                print("LOCAL GLOBAL", self.local_global)
                self.deliver_req(seq_no) #check if I should update
            else: # request message with this req_id is not recvd.
                print("WANTS", (req_id[0], self.local_state[req_id[0]]), "yet to deliver but dont have req msg")
                self.send_retransmit_req((req_id[0], self.local_state[req_id[0]]), True)
        else: # i did not deliver a few messages -> if I have the req and seq message for it deliver them, else retransmission request
            for i in range(self.last_delivered, seq_no+1):
                if i in self.global_state.keys():  # i have the seq msg for it, and it has been assigned a seq no, means i have seq message for this.
                    if self.global_state[i][1] < self.local_state[self.global_state[i][0]]: # i have the req message for this
                        self.deliver_req(i)
                    else: # gets the req message for some previous global sequence number. If I have the seq message and not the request message.
                        print("WANTS", (self.global_state[i][1], self.global_state[i][1]+1), "yet to deliver but dont have request of some old deliver message")
                        self.send_retransmit_req((self.global_state[i][1], self.global_state[i][1]+1), True)

    def recv_retransmit_req(self, addr, msg):
        msg_id = msg['request_id']
        flag = msg['flag']
        if flag: #request msg
            req_msg = self.requests[msg_id]
            ser_request = pickle.dumps(req_msg)
            try:
                self.sock.sendto(ser_request, addr)
            except Exception as e:
                print(e)
        else: #seq msg
            msg_id = self.global_state[msg_id]
            seq_msg = self.sequences[msg_id]
            ser_request = pickle.dumps(seq_msg)
            try:
                self.sock.sendto(ser_request, addr)
            except Exception as e:
                print(e)

    def send_retransmit_req(self, request_id, flag):

        if flag: #request msg
            retransmit_req = {
            "msg_type": "retransmit",
            "request_id": request_id,
            "flag": 1,
            "local_k": self.local_global[self.id]
        }
            ser_request = pickle.dumps(retransmit_req)
            addr = self.mem_ls[request_id[0]]
            try:
                self.sock.sendto(ser_request, addr)
            except Exception as e:
                print(e)
        else: #sequence msg
            retransmit_req = {
            "msg_type": "retransmit",
            "request_id": request_id,
            "flag": 0,
            "local_k": self.local_global[self.id]
            }
            ser_request = pickle.dumps(retransmit_req)
            addr = self.mem_ls[request_id%n]
            try:
                self.sock.sendto(ser_request, addr)
            except Exception as e:
                print(e)

    def deliver_req(self, no):
        func, args = self.req_func[no]
        cnt = defaultdict(lambda: 0)
        for i, k in self.local_global.items():
            cnt[k] += 1
        for k in cnt.keys():
            print(args)
            print("Delivering")
            func_ptr = self.func_to_ptr[func]
            res = func_ptr(*args)
            print(res)
    
    def send_seq(self, msg):
        print("sending seq no", self.id)
    
        func, args = msg['request']
        seq_msg = {
            "msg_type": 'sequence',
            "request_id": (self.id, self.local_no),
            "sequence_id": self.local_global[self.id]+1,
            "local_k": self.local_global[self.id],
            "request": (func, args),
        }
        self.local_global[self.id] += 1
        self.sequences[seq_msg["sequence_id"]] = seq_msg
        self.req_func[seq_msg["sequence_id"]] = seq_msg["request"]
        ser_request = pickle.dumps(seq_msg)
        for mem in self.mem_ls:
            if (self.IP, self.PORT) != mem:
                try:
                    self.sock.sendto(ser_request, mem)
                except Exception as e:
                    print(e)
                    print("ERROR IN", self.addr, "->", mem)
                    print("Sending", seq_msg)
        self.deliver_req(seq_msg["sequence_id"])

        '''
        check if my self.last_global_recvd is equal to global, else ask for request message retransmission
        how do I know that I also have the corresponding request messages for the lastglobalrecv?
        dont have a sequence of it so cant store a number, but for every request message I recv I can check if the corresponding seq arrived?
        but what If i recv a sequence w/o a request.

        for every req message store it in a list, and pop from it when a seq message is recvd for it.
        if when you have all seq messages, but this list is not empty, you dont have all request messages and can ask for it again from the sender.
        
        pop from unassign_global if req_id matches.
        '''

n = 5
t_ls = []
IPs = [('localhost', 7003), ('localhost', 7004), ('localhost', 7005), ('localhost', 7006), ('localhost', 7007)]

if __name__ == "__main__":
    args = sys.argv
    i = int(args[2])
    IP = args[1]
    n = 5
    cust_db = CustomerDatabase("customer"+str(i+1))
    mem = Member(i, (IP, 7003+i), cust_db, n, IPs)
    mem.recv()
