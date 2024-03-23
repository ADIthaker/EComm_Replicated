from collections import defaultdict
import socket
import pickle
import queue

class CustomerMember():
    def __init__(self, id, addr, mem_addr, cust_db, n):
        self.n = n
        self.id = id
        self.cust_db = cust_db
        self.IP = addr[0]
        self.PORT = addr[1]
        self.local_number = 0
        self.global_number = 0
        self.mem_local = [0 for _ in range(n)]
        self.mem_global = [0 for _ in range(n)] #keeps track of which message of a given member has been assigned a global number

        self.max_global = 0
        self.mem_addr = mem_addr
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.IP, self.PORT))
        self.req_send_buffer = queue.Queue()
        self.req_nack_buffer = [-1 for _ in range(20)]
        self.seq_send_buffer = queue.Queue()
        self.seq_nack_buffer = [-1 for _ in range(20)]
        self.MAXLEN = 20
    
    def listen(self):
        while True:
            #recv request message and check if its k mod n, if yes then send sequence message else listen for sequence message
            packet = self.sock.recvfrom(10000)
            ser_msg, sender_addr = packet
            msg = pickle.loads(ser_msg)
            if msg['msg_type'] == "request":
                self.recv_request(msg, sender_addr)
            elif msg['msg_type'] == "sequence":
                self.recv_sequence(msg, sender_addr)
            elif msg['msg_type'] == "retransmit":
                self.send_retransmit(msg)
            # check request message for retransmit and also check sequence message for retransmit
            break

    def deliver(self, msg):
        #read message and then call it on the cust_db
        pass

    def recv_sequence(self, msg, sender_addr):
        if msg['global'] - self.global_number > 1 and msg['global'] < self.seq_nack_buffer.front()['global']:
            sender_id = msg['request_id'][0]
            # this means that the sender has recvd more sequence messages than me
            # find set of seq messages not yet received
            # ask for sequence messages from the respective members
            self.seq_nack_buffer.append(msg)
            # instead of asking for all messages in between this might lead to overflooding the sender with NACK, ask for retransmit 
            # and upon every recv check not only the difference in number but also which message has been received already.
            for i in range(self.mem_local[sender_id], msg['request_id'][1]):
                self.ask_retransmit(sender_addr, i, "sequence")

    def send_sequence(self, msg):
        request = {
            'msg_type': "sequence",
            'request_id': (self.id, self.local_number),
            'msg_global': self.global_number,
            'func': msg['func'],
            'args': msg['args'],
        }
        ser_request = pickle.dumps(request)
        for mem in self.mem_addr:
            self.sock.sendto(ser_request, mem)
    
    def send_request(self, msg):
        #increment local message number 
        self.local_number += 1
        # make Request message
        request = {
            'msg_type': 'request',
            'request_id': (self.id, self.local_number), #s_id is its addr
            'func': msg['func'],
            'args': msg['args'],
            'global': self.global_number,
        }
        ser_request = pickle.dumps(request)
        # buffer message for nack retransmission
        self.req_send_buffer.append(ser_request)
        if len(self.msg_buffer) > self.MAXLEN:
            self.req_send_buffer.pop()
        #multicast
        for mem in self.mem_addr:
            self.sock.sendto(ser_request, mem)
    
    def recv_request(self, msg, sender_addr):
        sender_id = msg['request_id'][0]
        #NACK if message isn't the next one
        #Problem: what if NACK is flooding sender while it is sending other messages, just message order is jumbled?.
        if msg['request_id'][1] - self.mem_local[sender_id] > 1:
            self.req_nack_buffer.append(msg)
            for i in range(self.mem_local[sender_id], msg['request_id'][1]):
                self.ask_retransmit(sender_addr, i, "request")
        
        # check if sequence can be sent or not
        if self.id == (self.global_number+1)%self.n:
            if (self.max_global == self.global_number) and () and (): 
                #all sequence msg upto here are chosen
            
    def send_retransmit(self, msg):
        

    def ask_retransmit(self, member, msg_id, msg_type):
        if msg_type == "request":
            request = {
                'msg_type': 'retransmit',
                'request_id': ((self.IP, self.PORT), self.local_number), #s_id is its addr
                'msg_id': msg_id,
                
            }
            self.
        elif msg_type == "sequence":
            request = {
                'msg_type': 'retransmit',
                'request_id': ((self.IP, self.PORT), self.max_global), #s_id is its addr
            }
