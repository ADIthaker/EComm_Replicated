import sys
import os
from dotenv import load_dotenv
load_dotenv(override=True)

sys.path.append(os.environ.get("DIR"))
#sys.path.append('H:/MS/Sem 2/DS/CSCI5673_Distributed_Systems/AssignmentTwo')
from concurrent import futures
import time
import random
import grpc
import grpc_pb2.seller_pb2_grpc as seller_pb2_grpc
import grpc_pb2.seller_pb2 as seller_pb2
from apis.seller_api import SellerAPIs
from utils.database import ProductDatabase, CustomerDatabase

class SellServicer(seller_pb2_grpc.SellServicer):
    def __init__(self, port, partners) -> None:
        self.api = SellerAPIs(CustomerDatabase(), ProductDatabase('localhost:%d' % port, partners))
    def CreateAccount(self, request, context):
        print("Got a CreateAccount Request", request)
        user = {
            "name": request.username,
            "password": request.pwd,
            "items": request.items,
            "PosFb": request.posFb,
            "NegFb": request.negFb
        }
        api_handler = self.api
        response = api_handler.create_seller(user)
        create_user_reply = seller_pb2.UpdateResponse()
        if response is None:
            create_user_reply.error = True
            create_user_reply.msg = "Error creating user"
        create_user_reply.error = False
        create_user_reply.msg = "Seller created successfully"
        del api_handler
        return create_user_reply

    def GetUserID(self, request, context):
        print("Got a GetUserID Request", request)
        seller = {
            "name": request.name,
            "password": request.password
        }
        api_handler = self.api
        result = api_handler.get_seller_id(seller)
        seller_reply = seller_pb2.UpdateResponse()
        print(result)
        if type(result) is tuple:
            seller_reply.error = False
            seller_reply.msg = f'{result[0]}'
        else:
            seller_reply.error = True
            seller_reply.msg = "Invalid username or password"
        del api_handler
        return seller_reply
    
    def GetSellerRating(self, request, context):
        print("Got a GetSellerRating Request")
        userId = request.id
        api_handler = self.api
        result = api_handler.get_seller_rating(userId)
        print("result", result)
        seller_rating_reply = seller_pb2.SellerRating()
        if result is not None:
            # no need to add 1 here as all the new accounts do not contain 0 in them
            seller_rating_reply.posFb = result[0]
            seller_rating_reply.negFb = result[1]
        del api_handler
        return seller_rating_reply

    def ItemForSale(self, request, context):
        print("Got ItemForSale request")
        item = {
        "name": request.name,
        "price": request.price,
        "quantity": request.quantity,
        "category": request.category,
        "keywords": request.keywords,
        "cond": request.cond,
        "sellerId": request.sellerId
        }
        print(item)
        api_handler = self.api
        result = api_handler.put_item_for_sale(item)
        print(result)
        reply = seller_pb2.UpdateResponse()
        if result is not None:
            reply.error = False
            reply.msg = "Item Created"
        else:
            reply.error = True
            reply.msg = "Error creating item"
        del api_handler
        return reply
    
    def ChangeSalePrice(self, request, context):
        print("Got a ChangeSalePrice Request")
        api_handler = self.api
        result = api_handler.change_sale_price(request.itemId, request.sellerId , request.price)
        reply = seller_pb2.UpdateResponse()
        print(result)
        if result is not None:
            reply.error = False
            reply.msg = "Item Price Updated"
        else:
            reply.error = True
            reply.msg = "Error updating item price"
        del api_handler
        return reply

    def RemoveItem(self, request, context):
        print("Got a RemoveItem Request")
        api_handler = self.api
        result = api_handler.remove_item(request.itemId, request.sellerId , request.quantity)
        reply = seller_pb2.UpdateResponse()
        print(result)
        if result is not None:
            reply.error = False
            reply.msg = "Item Removed"
        else:
            reply.error = True
            reply.msg = "Error removing item"
        del api_handler
        return reply

    def DisplayItems(self, request, context):
        sellerId = request.id
        print(f"Got DisplayItems request from {sellerId}")
        api_handler = self.api
        result = api_handler.display_items(sellerId)
        print(result)
        reply = seller_pb2.DisplayItemsReply()
        if result is not None:
            for i in result:
                print("one item", i)
                ret_item = seller_pb2.Item(
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
    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    partners = ['localhost:10002', 'localhost:10003', 'localhost:10004', 'localhost:10005']
    seller_pb2_grpc.add_SellServicer_to_server(SellServicer(10001, partners), server)
    server.add_insecure_port("localhost:5051")
    server.start()
    print("Server Started")
    print('RAFT READY')
    server.wait_for_termination()


if __name__ == "__main__":
    serve()