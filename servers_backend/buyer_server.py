import sys
import os
from dotenv import load_dotenv
load_dotenv(override=True)

sys.path.append(os.environ.get("DIR"))
from concurrent import futures
import time
import grpc
import grpc_pb2.buyer_pb2_grpc as buyer_pb2_grpc
import grpc_pb2.buyer_pb2 as buyer_pb2
from apis.buyer_api import BuyerAPIs
from utils.database import ProductDatabase, CustomerDatabase

'''
Earlier:
Server Interface -> Server Backend
Now:
Server Interface -> Group Member -> Goes to other group members to find which one will assign global id k -> Checks if all messages with gid less than k have been delivered -> Sends message and global id to all members -> Then each of them call the db.

NACK Conditions:
Each group member has a table of member id: local seq no recvd.
if any number missed send NACK of that sequence number to member

Global seq number: When a number is missed send NACK to kmodn member id.

'''

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

    #recving part
    ser_msg = None
    while True:
        ser_msg, _ = sock.recvfrom(10000)
        if ser_msg is not None:
            break
    msg = pickle.loads(ser_msg)
    return msg
    
    
class BuyServicer(buyer_pb2_grpc.BuyServicer):
    def CreateAccount(self, request, context):
        print("Got a CreateAccount Request", request)
        user = {
            "name": request.username,
            "password": request.pwd,
            "items": request.items,
        }
        # api_handler = BuyerAPIs(CustomerDatabase(), ProductDatabase())
        # response = api_handler.create_buyer(user)
        response = talk_group("create_buyer", (user))
        create_user_reply = buyer_pb2.UpdateResponse()
        if response is None:
            create_user_reply.error = True
            create_user_reply.msg = "Error creating user"
        else:
            create_user_reply.error = False
            create_user_reply.msg = "Buyer created successfully"
        del api_handler
        return create_user_reply

    def GetUserID(self, request, context):
        print("Got a GetUserID Request", request)
        seller = {
            "name": request.name,
            "password": request.password
        }
        api_handler = BuyerAPIs(CustomerDatabase(), ProductDatabase())
        result = api_handler.get_buyer_id(seller)
        seller_reply = buyer_pb2.UpdateResponse()
        print(result)
        if type(result) is tuple:
            seller_reply.error = False
            seller_reply.msg = f'{result[0]}'
        else:
            seller_reply.error = True
            seller_reply.msg = "User can't be logged in"
        del api_handler
        return seller_reply
    
    def GetSellerRating(self, request, context):
        print("Got a GetSellerRating Request")
        userId = request.id
        api_handler = BuyerAPIs(CustomerDatabase(), ProductDatabase())
        result = api_handler.get_seller_rating(userId)
        print("result", result)
        seller_rating_reply = buyer_pb2.SellerRating()
        if result is not None:
            # no need to add 1 here as all the new accounts do not contain 0 in them
            seller_rating_reply.posFb = result[0]
            seller_rating_reply.negFb = result[1]
        del api_handler
        return seller_rating_reply

    def GetAvailableItems(self, request, context):
        print("Got GetAvailableItems request")
        search =  {
            "category": request.category,
            "keywords": request.keywords,
        }
        api_handler = BuyerAPIs(CustomerDatabase(), ProductDatabase())
        result = api_handler.get_available_items(search)
        print(result)
        reply = buyer_pb2.Items()
        if result is not None:
            for i in result:
                print("one item", i)
                ret_item = buyer_pb2.Item(
                    name=i[0],
                    price=i[5],
                    quantity=i[7],
                    category=i[1],
                    id=i[2],
                    keywords=i[3],
                    cond=i[4],
                    sellerId=i[6])
                reply.items.append(ret_item)
        del api_handler
        return reply
    
    def AddItems(self, request, context):
        print("Got AddItems request")
        buyer_id = request.buyerId
        cart = {}
        api_handler = BuyerAPIs(CustomerDatabase(), ProductDatabase())
        for i, q in zip(request.ids, request.quantities):
            cart[i.id] = q.q
        result = api_handler.add_items_cart(cart, buyer_id)
        reply = buyer_pb2.UpdateResponse()
        if result is not None:
            reply.error = False
            reply.msg = "Cart Updated with new Items"
        else:
            reply.error = True
            reply.msg = "Error updating cart"
        del api_handler
        return reply

    def RemoveItems(self, request, context):
        print("Got RemoveItems request")
        buyer_id = request.buyerId
        cart = {}
        api_handler = BuyerAPIs(CustomerDatabase(), ProductDatabase())
        for i, q in zip(request.ids, request.quantities):
            cart[i.id] = q.q
        result = api_handler.remove_items_cart(cart, buyer_id)
        reply = buyer_pb2.UpdateResponse()
        if result is not None:
            reply.error = False
            reply.msg = "Cart Updated with new Items"
        else:
            reply.error = True
            reply.msg = "Error updating cart"
        del api_handler
        return reply
    
    def GetCart(self, request, context):
        print("Got a GetCart Request")
        buyer_id = request.id
        api_handler = BuyerAPIs(CustomerDatabase(), ProductDatabase())
        result = api_handler.get_cart(buyer_id)
        reply = buyer_pb2.Cart()
        if result is not None:
            reply.buyerId = result['buyer_id']
            del result['buyer_id']
            del result['id']
            for i in result.keys():
                reply.ids.append(buyer_pb2.ItemId(id=i))
            for i in result.values():
                reply.quantities.append(buyer_pb2.Quantity(q=i))
        del api_handler
        return reply

    def DeleteCart(self, request, context):
        print("Got a DeleteCart Request")
        buyer_id = request.id
        api_handler = BuyerAPIs(CustomerDatabase(), ProductDatabase())
        result = api_handler.delete_cart(buyer_id)
        reply = buyer_pb2.UpdateResponse()
        if result is not None:
            reply.error = False
            reply.msg = "Cart deleted"
        else:
            reply.error = True
            reply.msg = "Error deleting cart"
        del api_handler
        return reply

    def SaveCart(self, request, context):
        print("Got a SaveCart Request")
        buyer_id = request.buyerId
        cart = {}
        api_handler = BuyerAPIs(CustomerDatabase(), ProductDatabase())
        for i, q in zip(request.ids, request.quantities):
            cart[i.id] = q.q
        result = api_handler.save_cart(cart, buyer_id)
        reply = buyer_pb2.UpdateResponse()
        if result:
            reply.error = False
            reply.msg = "Cart saved"
        else:
            reply.error = True
            reply.msg = "Error saving cart"
        del api_handler
        return reply

    def ProvideFeedback(self, request, context):
        print("Got a ProvideFeedback Request")
        items = []
        for f in request.fb:
            items.append({
                "feedback": f.feedback,
                "seller_id": f.sellerId
            })
        api_handler = BuyerAPIs(CustomerDatabase(), ProductDatabase())
        
        result = api_handler.provide_feedback(items)
        reply = buyer_pb2.UpdateResponse()
        if result:
            reply.error = False
            reply.msg = "Feedback sent"
        else:
            reply.error = True
            reply.msg = "Error sending feedback"
        del api_handler
        return reply
    
    def MakePurchaseCart(self, request, context):
        print("Got a MakePurchaseCart Request")
        buyer_id = request.cart.buyerId
        cart = {}
        for i, q in zip(request.cart.ids, request.cart.quantities):
            cart[i.id] = q.q
        api_handler = BuyerAPIs(CustomerDatabase(), ProductDatabase())
        card_details = {
            "expiry": request.expiry,
            "cardno": request.cardNo,
            "name": request.name
        }
        result = api_handler.make_purchase_from_cart(cart, buyer_id, card_details)
        reply = buyer_pb2.UpdateResponse()
        if result:
            reply.error = False
            reply.msg = "Cart Bought"
        else:
            reply.error = True
            reply.msg = "Error buying cart"
        del api_handler
        return reply
    
    def MakePurchaseDB(self, request, context):
        print("Got a MakePurchaseDB Request")
        buyer_id = request.buyerId
        card_details = {
            "expiry": request.expiry,
            "cardno": request.cardNo,
            "name": request.name
        }
        api_handler = BuyerAPIs(CustomerDatabase(), ProductDatabase())
        result = api_handler.make_purchase_from_db(buyer_id, card_details)
        reply = buyer_pb2.UpdateResponse()
        if result:
            reply.error = False
            reply.msg = "Cart Bought from DB"
        else:
            reply.error = True
            reply.msg = "Error buying cart from DB"
        del api_handler
        return reply

    def GetHistory(self, request, context):
        print("Got a GetHistory Request")
        buyerId = request.id
        api_handler = BuyerAPIs(CustomerDatabase(), ProductDatabase())
        result = api_handler.get_history(buyerId)
        reply = buyer_pb2.History()
        if result is not None:
            for i in result:
                ret_item = buyer_pb2.Cart()
                ret_item.buyerId = buyerId
                ret_item.ids.extend([buyer_pb2.ItemId(id=x) for x in i.keys()])
                ret_item.quantities.extend([buyer_pb2.Quantity(q=x) for x in i.values()])
                reply.purchases.append(ret_item)
        del api_handler
        return reply


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    buyer_pb2_grpc.add_BuyServicer_to_server(BuyServicer(), server)
    server.add_insecure_port("localhost:5053")
    server.start()
    print("Server Started")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()