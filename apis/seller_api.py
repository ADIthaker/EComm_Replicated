class SellerAPIs:
    def __init__(self, cust_db, prod_db):
        self.cust_db = cust_db
        self.prod_db = prod_db

    def create_seller(self, seller): #create account checked
        self.cust_db.create_seller(seller)

    def get_seller_id(self, seller):
        idDB = self.cust_db.get_seller_id(seller)
        if idDB:
            return idDB
        else:
            return False
        
    def is_seller(self, Id): #login checked
        seller = self.cust_db.get_seller(Id)
        if seller is not None and len(seller)!=0:
            print(seller)
            return seller[0][1]
        else:
            return False

    def get_seller_rating(self, Id): #checked
        seller = self.cust_db.get_seller(Id)
        if seller is not None and len(seller)!=0:
            posfb, negfb = seller[0][3] , seller[0][4]
            return (posfb, negfb)
        return None
    
    def put_item_for_sale(self, item): #checked
        Id = self.prod_db.create_item(item)
        #increase the count of items of this seller by 1
        return Id
    
    def change_sale_price(self, Id, seller_id, price): #checked
        item = self.prod_db.get_item(Id, seller_id)
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
                self.prod_db.update_item(new_item)
        else:
            print("Item Not Found")
            return item
        return item
    
    def remove_item(self, Id, seller_id, quantity): #checked
        item = self.prod_db.get_item(Id, seller_id)
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
                self.prod_db.update_item(new_item)
        else:
            print("Item Not Found")
            return item
        return item
        
    def display_items(self, seller_id): #checked
        items = self.prod_db.get_items(seller_id)
        return items
    

