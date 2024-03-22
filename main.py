from AssignmentOne.utils.database import *
from Seller import *
from Buyer import *

p_db = ProductDatabase()
c_db = CustomerDatabase()

s_api = SellerAPIs(c_db, p_db)
b_api = BuyerAPIs(c_db, p_db)

seller ={
    'name' : "Adi",
    'password': "Adi",
    'items': 0,
    'PosFb': 0,
    'NegFb': 0
}
item = {
    'name':'book',
    'quantity':10,
    'cat':1,
    'price': 100,
    'keywords':'adansfonoi',
    'condition': 1,
    'seller_id': '7e031651bf1311eeb6e1d5a73ad3607d'
}
items = [
    {
        "seller_id":"3516e53ebf1411eea4fed5a73ad3607d",
        "feedback": 1,
    },
    {
        "seller_id":"3937c480bf1411eea1bed5a73ad3607d",
        "feedback": 1,
    },
    {
        "seller_id":"469ac2e2bf1411ee903fd5a73ad3607d",
        "feedback": 1,
    },
    {
        "seller_id":"7e031651bf1311eeb6e1d5a73ad3607d",
        "feedback": 1,
    },
    {
        "seller_id":"9ed8b5a4bf1311ee9791d5a73ad3607d",
        "feedback": 1,
    },
    {
        "seller_id":"3516e53ebf1411eea4fed5a73ad3607d",
        "feedback": 1,
    },
    {
        "seller_id":"3937c480bf1411eea1bed5a73ad3607d",
        "feedback": 1,
    },
    {
        "seller_id":"469ac2e2bf1411ee903fd5a73ad3607d",
        "feedback": 0,
    },
    {
        "seller_id":"7e031651bf1311eeb6e1d5a73ad3607d",
        "feedback": 0,
    },
    {
        "seller_id":"9ed8b5a4bf1311ee9791d5a73ad3607d",
        "feedback": 1,
    },
]
buyer = {
    'name' : "Aditya",
    'password': "Aditya",
    'items': 0,
}

items = {
    "83f2e9f6bf1911ee8d09d5a73ad3607d1":2,
    "9cd7ae8bbf1911ee8637d5a73ad3607d1":3,
    "a21775f6bf1911eebdb4d5a73ad3607d1": 3
}
b_api.remove_items_cart(items,"1e7ef260bf1a11ee8cbdd5a73ad3607d")
#b_api.provide_feedback(items)
#b_api.create_buyer(buyer)
# print(b_api.is_buyer('ddd44bbfbf1911ee8eedd5a73ad3607d'))
# print(b_api.get_seller_rating("2ad5eccfbf1311ee8958d5a73ad3607d"))
# search = {
#     'keywords': 'ada',
#     'cat': 1
# }
#print(b_api.get_available_items(search))
#cart = {"83f2e9f6bf1911ee8d09d5a73ad3607d1": 2, "9cd7ae8bbf1911ee8637d5a73ad3607d1":2}
#b_api.save_cart(cart, "1e7ef260bf1a11ee8cbdd5a73ad3607d")
#print(b_api.get_cart("88c74551bf1f11eeb9a0d5a73ad3607d"))
#print(b_api.get_history("19d15dc9bf1a11ee8ef4d5a73ad3607d"))
# s_api.create_seller(seller)
# ans = s_api.is_seller('7e031651bf1311eeb6e1d5a73ad3607d')
# print(s_api.get_seller_rating('7e031651bf1311eeb6e1d5a73ad3607d'))
# s_api.put_item_for_sale(item)
# s_api.put_item_for_sale(item)
# s_api.put_item_for_sale(item)
#s_api.change_sale_price("5599d3febf1411eea1acd5a73ad3607d1", 200, item['seller_id'])
#s_api.remove_item("5599d3febf1411eea1acd5a73ad3607d1", item['seller_id'], 5)
#print(s_api.display_items('7e031651bf1311eeb6e1d5a73ad3607d'))

