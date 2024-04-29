import requests

# To the server, send a dict payload with the following keys: 'key', 'value'

class SellerAPIs:
    def __init__(self, rotating_seq_ip, raft_ip):
        self.rotating_seq = rotating_seq_ip
        self.raft = raft_ip

    def create_seller(self, seller): #create account checked
        # self.cust_db.create_seller(seller)
        payload = {'key': 'create_seller' ,'value': seller}
        requests.put(self.rotating_seq, json={'payload': payload})

    def get_seller_id(self, seller):
        # idDB = self.cust_db.get_seller_id(seller)
        payload = {'key': 'get_seller_id' ,'value': seller}
        idDB = requests.put(self.rotating_seq, json={'payload': payload})
        if idDB:
            return idDB
        else:
            return False
        
    def is_seller(self, Id): #login checked
        # seller = self.cust_db.get_seller(Id)
        seller = requests.put(self.rotating_seq, json={'key': 'is_seller' ,'Id': Id})
        if seller is not None and len(seller)!=0:
            print(seller)
            return seller[0][1]
        else:
            return False

    def get_seller_rating(self, Id): #checked
        # seller = self.cust_db.get_seller(Id)
        seller = requests.put(self.rotating_seq, json={'key': 'get_seller_rating' ,'Id': Id})
        if seller is not None and len(seller)!=0:
            posfb, negfb = seller[0][3] , seller[0][4]
            return (posfb, negfb)
        return None
    
    def put_item_for_sale(self, item): #checked
        # Id = self.prod_db.create_item(item)
        payload = {"key": 'put_item_for_sale', "value": item}
        Id = requests.put(self.raft, json={'payload': payload})
        #increase the count of items of this seller by 1
        Id = Id.json()
        return Id
    
    def change_sale_price(self, Id, seller_id, price): #checked
        # item = self.prod_db.get_item(Id, seller_id)
        item = requests.get(self.raft, json={'Id': Id, 'seller_id': seller_id})
        new_item = {}
        if item is not None and len(item) != 0:
                item = item[0]
                new_item['name'] = item[0]
                new_item['cat'] = item[1]
                new_item['id'] = item[2]
                new_item['keywords'] = item[3]
                new_item['condition'] = item[4]
                new_item['price'] = price
                new_item['seller_id'] = item[6]
                new_item['quantity'] = item[7]
                # self.prod_db.update_item(new_item)
                requests.put(self.raft, json={'new_item': new_item})
        else:
            print("Item Not Found")
            return item
        return item
    
    def remove_item(self, Id, seller_id, quantity): #checked
        # item = self.prod_db.get_item(Id, seller_id)
        item = requests.get(self.raft, json={'Id': Id, 'value': seller_id})
        new_item = {}
        if item is not None and len(item)!=0:
            item = item[0]
            if quantity >= item[7]:
                self.prod_db.delete_item(Id)
            else:
                new_item['name'] = item[0]
                new_item['cat'] = item[1]
                new_item['id'] = item[2]
                new_item['keywords'] = item[3]
                new_item['condition'] = item[4]
                new_item['price'] = item[5]
                new_item['seller_id'] = item[6]
                new_item['quantity'] = item[7] - quantity
                # self.prod_db.update_item(new_item)
                requests.put(self.raft, json={'new_item': new_item})
        else:
            print("Item Not Found")
            return item
        return item
        
    def display_items(self, seller_id): #checked
        # items = self.prod_db.get_items(seller_id)
        payload = {"key": 'display_items', "value": seller_id}
        items = requests.put(self.raft, json={'payload': payload})
        items = items.json()
        print(items)
        return items['result']