import sys
import os
from dotenv import load_dotenv
load_dotenv(override=True)

sys.path.append(os.environ.get("DIR"))
import grpc_pb2.seller_pb2_grpc as seller_pb2_grpc
import grpc_pb2.seller_pb2 as seller_pb2
import time
import grpc

class SellerRoutes:
    def __init__(self, connection="localhost:5051"):
        self.channel = grpc.insecure_channel(connection)
        self.stub = seller_pb2_grpc.SellStub(self.channel)

    def create_seller(self, seller): #create account checked
        create_seller_request = seller_pb2.Seller(
            username = seller['name'], 
            pwd = seller['password'],
            id = "",
            items = seller["items"],
            posFb = seller["PosFb"],
            negFb = seller["NegFb"]
            )
        reply = self.stub.CreateAccount(create_seller_request)
        return reply

    def get_seller_id(self, seller):
        getId_request = seller_pb2.Login(name=seller['name'], password=seller['pwd'])
        reply = self.stub.GetUserID(getId_request)
        return reply

    def get_seller_rating(self, Id): #checked
        getId_request = seller_pb2.UserID(id=Id)
        reply = self.stub.GetSellerRating(getId_request)
        #grpc does not send values with 0, so reduce the count of both feedback by 1
        return reply
    
    def put_item_for_sale(self, item): #checked
        create_item_request = seller_pb2.Item(
            name = item['name'],
            category = item['category'],
            price = item['price'],
            id = "",
            keywords = item['keywords'],
            cond = item['cond'],
            quantity = item['quantity'],
            sellerId = item['sellerId']
        )
        reply = self.stub.ItemForSale(create_item_request)
        return reply
    
    def change_sale_price(self, item): #checked
        change_price_req = seller_pb2.PriceIDPack(
            price = item['price'],
            itemId = item['id'],
            sellerId = item['sellerId']
        )
        reply = self.stub.ChangeSalePrice(change_price_req)
        return reply
    
    def remove_item(self, item): #checked
        remove_item_req = seller_pb2.QuantityIDPack(
        sellerId = item['sellerId'],
        itemId = item['id'],
        quantity = item['quantity']
        )
        reply = self.stub.RemoveItem(remove_item_req)
        return reply
        
    def display_items(self, Id): #checked
        display_items_request = seller_pb2.UserID(id = Id)
        reply = self.stub.DisplayItems(display_items_request)
        return reply
 
if __name__ == '__main__':
    routes = SellerRoutes()
    seller = {
        "name": "grpc_Adi",
        "password":"212",
        "items": 0,
        "posFb": 0,
        "negFb": 0
    }
    item = {
        "name": "grpc_bat",
        "price": 120,
        "quantity": 35,
        "category": 2,
        "keywords": "cricket",
        "cond": 1,
        "sellerId": "9ed08f75cb5911eeba0ad5a73ad3607d"
    }
    remove_item = {
        'id': "d83cf3aecb5e11eea0e7d5a73ad3607d2",
        'sellerId': "9ed08f75cb5911eeba0ad5a73ad3607d",
        'quantity': 20
    }
    #print(routes.create_seller(seller))
    #print(routes.get_seller_id({"name":"grpc_Adi", "pwd": "212"}))
    #print("Output", routes.get_seller_rating("9ed08f75cb5911eeba0ad5a73ad3607d"))
    #print(routes.put_item_for_sale(item))
    #print(routes.change_sale_price(item))
    #print(routes.remove_item(item))
    #print(routes.display_items("9ed08f75cb5911eeba0ad5a73ad3607d"))

