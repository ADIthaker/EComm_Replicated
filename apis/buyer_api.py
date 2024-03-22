from zeep import Client

class BuyerAPIs:
    def __init__(self, cust_db, prod_db):
        self.cust_db = cust_db
        self.prod_db = prod_db
    
    def create_buyer(self, buyer): #create account checked
        self.cust_db.create_buyer(buyer)

    def get_buyer_id(self, buyer):
        idDB = self.cust_db.get_buyer_id(buyer)
        if idDB:
            return idDB
        else:
            return False
        
    def is_buyer(self, id): #login checked
        buyer = self.cust_db.get_buyer(id)
        if buyer is not None and len(buyer)!=0:
            return buyer[0][1]
        else:
            return False

    def get_seller_rating(self, Id): #checked
        seller = self.cust_db.get_seller(Id)
        if seller is not None and len(seller)!=0:
            posfb, negfb = seller[0][3], seller[0][4]
            return (posfb, negfb)
        return None
    
    # provide feedback takes in a list of items, and updates the feedback of each items sellers individually after grouping by seller id
    def provide_feedback(self, items): #checked
        pos_fb = {}
        neg_fb = {}
        for item in items:
            pos_fb[item['seller_id']] = 0
            neg_fb[item['seller_id']] = 0

        for item in items:
            if item['feedback'] == 1:
                pos_fb[item['seller_id']] += 1
            else:
                neg_fb[item['seller_id']] += 1

        # call update to all sellers and update their pos and neg fb
        updates = []
        for seller_id in pos_fb.keys():
            seller = self.cust_db.get_seller(seller_id)
            if seller is not None and len(seller)!=0:
                posfb, negfb = seller[0][4], seller[0][5]
                newposfb = posfb + pos_fb[seller[0][2]]
                newnegfb = negfb + neg_fb[seller[0][2]]
                new_seller = {}
                new_seller['name'] = seller[0][0]
                new_seller['password']  = seller[0][1]
                new_seller['id'] = seller[0][2]
                new_seller['items'] = seller[0][3]
                new_seller['PosFb'] = newposfb
                new_seller['NegFb'] = newnegfb
                updates.append(new_seller)
            else:
                print("Seller not found in provide_feedback")
                return
        val = True
        for update in updates:
            print(update)
            val &= self.cust_db.update_seller(update)
        return val

    def _add_cart_items(self, new_items, cart): #checked
        existing_items = self._convert_string_cart(cart)
        for it, quant in new_items.items():
            if it in existing_items:
                existing_items[it] += quant
            else:
                existing_items[it] = quant
        return existing_items
    
    def _remove_cart_items(self, new_items, cart): #checked
        existing_items = self._convert_string_cart(cart)
        for it, quant in new_items.items():
            if it in existing_items:
                existing_items[it] -= quant
            else:
                existing_items[it] = quant
            if existing_items[it] < 0:
                existing_items[it] = 0
        return existing_items
                
    def add_items_cart(self, items, buyer_id): # items must be a list of dicts where each dict has {'id': quantity} checked
        # assume cart exists only and then add
        cart = self.cust_db.get_cart(buyer_id)
        if cart is not None and len(cart)!=0:
            new_items = self._add_cart_items(items, cart[0])
            updated_cart = {}
            updated_cart['products'] = self._convert_cart_string(new_items)
            updated_cart['buyer_id'] = cart[0][1]
            updated_cart['id'] = cart[0][0]
            return self.cust_db.update_cart(updated_cart)
        else:
            print("Cart not found in add_items_cart")
            return None


    def remove_items_cart(self, items, buyer_id): #checked
        # assume cart exists only and then remove
        cart = self.cust_db.get_cart(buyer_id)
        if cart is not None and len(cart)!=0:
            new_items = self._remove_cart_items(items, cart[0])
            updated_cart = {}
            updated_cart['products'] = self._convert_cart_string(new_items)
            updated_cart['buyer_id'] = cart[0][1]
            updated_cart['id'] = cart[0][0]
            return self.cust_db.update_cart(updated_cart)
        else:
            print("Cart not found in remove_items_cart")
            return None

    def get_available_items(self, search): # search is a dictionary with 'cat' | checked
        items = self.prod_db.search_item(search)
        return items
    
    def get_cart(self, buyer_id): #checked
        cart = self.cust_db.get_cart(buyer_id)
        if cart is not None and len(cart)!=0:
            cart = cart[0]
            res = self._convert_string_cart(cart)
            res['id'] = cart[0]
            res['buyer_id'] = cart[1]
            return res
        else:
            print("Cart not found in get_cart")
            return None

    def _convert_cart_string(self, cart): #checked
        res = ""
        for key, val in cart.items():
            res += str(key) + "-" + str(val) + "|"
        res = res[:-1]
        return res
    
    def _convert_string_cart(self, cart): #checked
        prods = cart[2].split("|")
        res = {}
        for p in prods:
            quant = p.split('-')
            res[quant[0]] = int(quant[1])
        return res
    
    def save_cart(self, cart, buyer_id): # cart is a list of product id strings checked
        res = self._convert_cart_string(cart)
        cart["products"] = res
        cart["buyer_id"] = buyer_id
        return self.cust_db.create_cart(cart)
    
    def delete_cart(self, buyerId): #checked
        return self.cust_db.delete_cart(buyerId)
    
    def pre_purchase(self, card_details):
        client = Client('http://localhost:8000/?wsdl')
        result = client.service.complete_transaction(card_details['name'], card_details['cardno'], card_details['expiry'], 1000)
        print("GOT RESULT", result)
        return result

    def post_purchase(self, buyerID, cart):
        self.cust_db.create_purchase(cart)

    def make_purchase_from_db(self, buyerID, card_details): #checked
        pur_res = self.pre_purchase(card_details)
        if pur_res:
            cart = self.cust_db.get_cart(buyerID)
            if cart is not None and len(cart)!=0:
                cart = cart[0]
                cart_obj = {
                    "buyer_id": cart[1],
                    "products": cart[2]
                }
                self.cust_db.delete_cart(buyerID)
                self.post_purchase(buyerID, cart_obj)
                return True
            else:
                print("Cart not found in make_purchase")
                return None
        else:
            return False
        
    def make_purchase_from_cart(self, cart, buyerID, card_details): #checked
        pur_res = self.pre_purchase(card_details)
        if pur_res:
            res = self._convert_cart_string(cart)
            cart["products"] = res
            cart["buyer_id"] = buyerID
            self.post_purchase(buyerID, cart)
            return True
        else:
            return False

    def get_history(self, BuyerId): #checked
        res = self.cust_db.get_purchases(BuyerId)
        if res is not None and len(res) !=0:
            history = []
            for purchase in res:
                history.append(self._convert_string_cart(purchase))
            return history
        else:
            print("History not found")
            return None