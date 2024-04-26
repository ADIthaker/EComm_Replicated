import mysql.connector
import uuid
import os
import time
from dotenv import load_dotenv
from pysyncobj import SyncObj, replicated

load_dotenv()

class ProductDatabase(SyncObj):
    def __init__(self, selfNodeAddr, otherNodeAddrs):
        try:
            super(ProductDatabase, self).__init__(selfNodeAddr, otherNodeAddrs)
            print(otherNodeAddrs)
            time.sleep(10)
            mydb = mysql.connector.connect(
            host="localhost",
            user=os.environ.get("USER"),
            password=os.environ.get("PWD"),
            db="product"
            )
            self.conn = mydb
            self.cursor = self.conn.cursor()
            self.cursor.execute("CREATE DATABASE IF NOT EXISTS Product")
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS Item(
                                Pname VARCHAR(32) NOT NULL, 
                                Category INT NOT NULL,
                                Id VARCHAR(40) NOT NULL,
                                Keyword TINYTEXT NOT NULL,
                                Cond INT NOT NULL,
                                Price INT NOT NULL,
                                SellerID VARCHAR(40) NOT NULL,
                                Quantity INT NOT NULL DEFAULT 0,
                                PRIMARY KEY(Id)
                                )''')
            print("Product DB is RUNNING...")
            time.sleep(10)
            print(self.getStatus())
        except mysql.connector.Error as error:
            print("Failed to create table in MySQL: {}".format(error))

    @replicated
    def create_item(self, item):
        try:
            Id = uuid.uuid1().hex + str(item['category'])
            query = 'INSERT INTO Item (Pname, Category, Id, Keyword, Cond, Price, SellerID, Quantity) VALUES(%s, %s, %s, %s, %s, %s, %s, %s);'
            vals = (item['name'], item['category'], Id, item['keywords'], item['cond'], item['price'], item['sellerId'], item['quantity'])
            self.cursor.execute(query, vals)
            self.conn.commit()
            return Id
        except mysql.connector.Error as error:
            print("Failed to insert entry in MySQL: {}".format(error))
            return "Failed to insert entry in MySQL: {}".format(error)

    @replicated
    def get_item(self, Id, seller_id):
        try:
            query = "SELECT * FROM Item WHERE Id=%s AND SellerID =%s"
            self.cursor.execute(query, (Id, seller_id))
            result = self.cursor.fetchall()
            return result
        except mysql.connector.Error as error:
            print("Failed to get product in MySQL: {}".format(error))
            return None
    @replicated
    def get_items(self, seller_id):
        try:
            query = "SELECT * FROM Item WHERE SellerID =%s"
            self.cursor.execute(query, (seller_id,))
            result = self.cursor.fetchall()
            return result
        except mysql.connector.Error as error:
            print("Failed to get product in MySQL: {}".format(error))
            return None
    
    @replicated
    def search_item(self, search):
        try:
            query = "SELECT * FROM Item WHERE Category=%s AND INSTR(Keyword, %s) > 0"
            self.cursor.execute(query, (search['category'], search['keywords']))
            result = self.cursor.fetchall()
            return result
        except mysql.connector.Error as error:
            print("Failed to get product in MySQL: {}".format(error))
            return None

    @replicated
    def update_item(self, item):
        try:
            query = "UPDATE Item SET Pname=%s, Category=%s, Keyword=%s, Cond=%s, Price=%s, Quantity=%s WHERE Id=%s AND SellerID=%s"
            val = (item['name'], item['cat'], item['keywords'], item['condition'], item['price'], item['quantity'], item['id'], item['seller_id'])
            self.cursor.execute(query, val)
            self.conn.commit()
            return True
        except mysql.connector.Error as error:
            print("Failed to update product in MySQL: {}".format(error))
            return False

    @replicated
    def delete_item(self, Id):
        try:
            query = "DELETE FROM Item WHERE Id=%s"
            val = (Id,)
            self.cursor.execute(query, val)
            self.conn.commit()
            return True
        except mysql.connector.Error as error:
            print("Failed to delete product in MySQL: {}".format(error))
            return False

    def __del__(self):
        if self.conn.is_connected():
            self.cursor.close()
            self.conn.close()
            print("MySQL Product connection is closed")

class CustomerDatabase:
    def __init__(self, db_name):
        try:
            mydb = mysql.connector.connect(
            host="localhost",
            user=os.environ.get("USER"),
            password=os.environ.get("PWD"),
            db=db_name
            )
            self.conn = mydb
            self.cursor = self.conn.cursor()
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS Buyer(
                                Username varchar(32) NOT NULL,
                                Pwd varchar(32) NOT NULL,
                                Items int NOT NULL DEFAULT 0,
                                Id varchar(40) NOT NULL,
                                PRIMARY KEY(Id)
                                )''')
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS Seller(
                                Username varchar(32) NOT NULL,
                                Pwd varchar(32) NOT NULL,
                                Id varchar(40) NOT NULL,
                                Items int NOT NULL DEFAULT 0,
                                Posfb int NOT NULL DEFAULT 0,
                                Negfb int NOT NULL DEFAULT 0,
                                PRIMARY KEY(Id)
                                )''')
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS Cart(
                                Id varchar(40) NOT NULL,
                                BuyerID varchar(40) NOT NULL,
                                Products varchar(4000) NOT NULL,
                                PRIMARY KEY(Id),
                                FOREIGN KEY (BuyerID) REFERENCES Buyer(Id)
                                )''')
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS Purchase(
                                Id varchar(40) NOT NULL,
                                BuyerID varchar(40) NOT NULL,
                                Products varchar(4000) NOT NULL,
                                PRIMARY KEY(Id),
                                FOREIGN KEY (BuyerID) REFERENCES Buyer(Id)
                                )''')
            print("Customer DB is RUNNING...")
        except mysql.connector.Error as error:
            print("Failed to create table in MySQL: {}".format(error))

    def create_buyer(self, buyer):
        try:
            id = uuid.uuid1().hex
            query = 'INSERT INTO Buyer (Username, Pwd, Items, Id) VALUES(%s, %s, %s, %s);'
            self.cursor.execute(query, (buyer['name'], buyer['password'], buyer['items'], id))
            self.conn.commit()
            return True
        except mysql.connector.Error as error:
            print("Failed to insert buyer in MySQL: {}".format(error))
            return False

    def get_buyer_id(self, buyer):
        try:
            query = 'SELECT Id FROM buyer WHERE Username=%s AND Pwd=%s'
            vals = (buyer['name'], buyer['password'],)
            self.cursor.execute(query, vals)
            result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as error:
            print("Failed to get buyer in MySQL: {}".format(error))
        return None

    def get_buyer(self, id):
        try:
            query = 'SELECT * FROM  Buyer WHERE Id=%s;'
            vals = (id,)
            self.cursor.execute(query, vals)
            result = self.cursor.fetchall()
            return result
        except mysql.connector.Error as error:
            print("Failed to get buyer in MySQL: {}".format(error))
        return None
    
    def get_cart_id(self, buyer_id):
        try:
            query = 'SELECT * FROM cart WHERE BuyerID=%s;'
            vals = (buyer_id,)
            self.cursor.execute(query, vals)
            result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as error:
            print("Failed to get buyer in MySQL: {}".format(error))
        return None

    def update_buyer(self, buyer):
        try:
            query = "UPDATE Buyer SET Username=%s, Pwd=%s, Items=%s, WHERE Id=%s"
            val = (buyer['name'], buyer['password'], buyer['items'], id)
            self.cursor.execute(query, val)
            self.conn.commit()
            return True
        except mysql.connector.Error as error:
            print("Failed to update buyer in MySQL: {}".format(error))
            return False

    def delete_buyer(self, id):
        try:
            query = "DELETE FROM Buyer WHERE Id=%s"
            val = (id,)
            self.cursor.execute(query, val)
            self.conn.commit()
            return True
        except mysql.connector.Error as error:
            print("Failed to delete buyer in MySQL: {}".format(error))
            return False

    def create_seller(self, seller):
        try:
            id = uuid.uuid1().hex
            query =  'INSERT INTO Seller (Username, Pwd, Id, items, PosFb, NegFb) VALUES(%s, %s, %s, %s, %s, %s);'
            vals = (seller['name'], seller['password'], id, seller['items'], seller['PosFb'], seller['NegFb'])
            self.cursor.execute(query, vals)
            self.conn.commit()
            return True
        except mysql.connector.Error as error:
            print("Failed to insert seller in MySQL: {}".format(error))
            return False

    def get_seller_id(self, seller):
        try:
            query = 'SELECT Id FROM seller WHERE Username=%s AND Pwd=%s'
            vals = (seller['name'], seller['password'],)
            self.cursor.execute(query, vals)
            result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as error:
            print("Failed to get buyer in MySQL: {}".format(error))
        return None

    def get_seller(self, id):
        try:
            query = 'SELECT * FROM Seller WHERE Id=%s;'
            vals = (id,)
            self.cursor.execute(query, vals)
            result = self.cursor.fetchall()
            return result
        except mysql.connector.Error as error:
            print("Failed to get seller in MySQL: {}".format(error))
        return None

    def update_seller(self, seller):
        try:
            query = "UPDATE Seller SET Username=%s, Pwd=%s, Items=%s, PosFb=%s, NegFb=%s WHERE Id=%s"
            vals = (seller['name'], seller['password'], seller['items'],  seller['PosFb'], seller['NegFb'], seller['id'])
            self.cursor.execute(query, vals)
            self.conn.commit()
            return True
        except mysql.connector.Error as error:
            print("Failed to update seller in MySQL: {}".format(error))
            return False

    def delete_seller(self, id):
        try:
            query = "DELETE FROM Seller WHERE Id=%s"
            val = (id,)
            self.cursor.execute(query, val)
            self.conn.commit()
            return True
        except mysql.connector.Error as error:
            print("Failed to delete seller in MySQL: {}".format(error))
            return False
            
    def create_cart(self, cart):
        try:
            Id = uuid.uuid1().hex
            query =  'INSERT INTO Cart (Id, BuyerID, Products) VALUES(%s, %s, %s);'
            vals = (Id, cart['buyer_id'], cart['products'])
            self.cursor.execute(query, vals)
            self.conn.commit()
            return True
        except mysql.connector.Error as error:
            print("Failed to insert cart in MySQL: {}".format(error))
            return False
    
    def get_cart(self, Id):
        try:
            query = 'SELECT * FROM Cart WHERE BuyerID=%s;'
            vals = (Id,)
            self.cursor.execute(query, vals)
            result = self.cursor.fetchall()
            return result
        except mysql.connector.Error as error:
            print("Failed to get cart in MySQL: {}".format(error))
        return None

    def update_cart(self, cart):
        try:
            query = "UPDATE Cart SET Products=%s WHERE BuyerID=%s"
            vals = (cart['products'], cart['buyer_id'])
            self.cursor.execute(query, vals)
            self.conn.commit()
            return True
        except mysql.connector.Error as error:
            print("Failed to update cart in MySQL: {}".format(error))
            return False
    
    def delete_cart(self, buyer_id):
        try:
            query = "DELETE FROM Cart WHERE BuyerID=%s"
            val = (buyer_id,)
            self.cursor.execute(query, val)
            self.conn.commit()
            return True
        except mysql.connector.Error as error:
            print("Failed to delete cart in MySQL: {}".format(error))
            return False
    
    def create_purchase(self, cart):
        try:
            Id = uuid.uuid1().hex
            query =  'INSERT INTO Purchase (Id, BuyerID, Products) VALUES(%s, %s, %s);'
            vals = (Id, cart['buyer_id'], cart['products'])
            self.cursor.execute(query, vals)
            self.conn.commit()
            return True
        except mysql.connector.Error as error:
            print("Failed to insert purchase in MySQL: {}".format(error))
            return False
    
    def get_purchases(self, buyer_id):
        try:
            query = 'SELECT * FROM  Purchase WHERE BuyerID=%s;'
            vals = (buyer_id,)
            self.cursor.execute(query, vals)
            result = self.cursor.fetchall()
            return result
        except mysql.connector.Error as error:
            print("Failed to get purchases in MySQL: {}".format(error))
        return None

    def __del__(self):
        if self.conn.is_connected():
            self.cursor.close()
            self.conn.close()
            print("MySQL Customer connection is closed")