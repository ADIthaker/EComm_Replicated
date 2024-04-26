import socket
import pickle
import queue

IP = 'localhost'
PORT = 7010
IPs = [('localhost', 7003), ('localhost', 7004), ('localhost', 7005), ('localhost', 7006), ('localhost', 7007)]

def talk_group(func, args):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP, PORT))
    send_msg = {
        "msg_type": "submit_request",
        "request": (func, args),
    }
    ser_req = pickle.dumps(send_msg)
    sock.sendto(ser_req, IPs[0])

print(talk_group("create_buyer", ({ 
            "name": 'ds',
            "password": 'ds',
            "items": 0,
        },)))