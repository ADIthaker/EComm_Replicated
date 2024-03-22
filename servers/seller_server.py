import sys
import os
from dotenv import load_dotenv
load_dotenv(override=True)

sys.path.append(os.environ.get("DIR"))
#sys.path.append('H:/MS/Sem 2/DS/CSCI5673_Distributed_Systems/AssignmentTwo')
# sys.path.append('C:\\Users\\athak\\Desktop\\Documents\\CUB\\SEM2\\Distributed Systems\\CSCI5673_Distributed_Systems\\AssignmentOne')
# Added the above import cause I was facing ModuleImportError
from flask import Flask, request, jsonify
from routes.seller_routes import SellerRoutes
import time
import threading

app = Flask(__name__)

# Session timeout configuration
SESSION_TIMEOUT = 300  # 5 minutes
WARNING_THRESHOLD = 240  # 4 minutes

# Global variables for session tracking
last_activity_times = {}
client = {}

# Seller-related functions

def create_account(username, password):
    seller = {'name': username, 'password': password, 'items': 1, 'PosFb': 1, 'NegFb': 1}
    return seller

def login(username, password):
    seller = {'name': username, 'pwd': password}
    return seller

def create_item_for_sale(Pname, cat, keywords, cond, sale_price, seller_id, quant):
    item = {'name': Pname, 'category': int(cat), 'keywords': keywords, 'cond': cond,
            'price': sale_price, 'sellerId': seller_id, 'quantity': quant}
    return item

# Helper functions

def send_warning_to_client(client_address):
    print(f"Sending warning to {client_address}: Session will be terminated in 1 minute.")
    return 'You will be logged out in one minute'

def check_session_timeout():
    global last_activity_times

    while True:
        # Iterate through clients and check session timeout
        for client_address, last_activity_time in last_activity_times.copy().items():
            # Check if the client has a valid session (logged in)
            if client_address not in last_activity_times:
                return client_address + 'Not logged in!'

            # Check session timeout
            if time.time() - last_activity_times[client_address] > SESSION_TIMEOUT:
                # Clear the last activity time and disconnect the client
                print(last_activity_times)
                last_activity_times.pop(client_address)
                return client_address + 'Session timeout!'

            # Check if a warning needs to be sent
            if time.time() - last_activity_times[client_address] > WARNING_THRESHOLD:
                # Send a warning message to the client
                print(last_activity_time)
                print(last_activity_times)
                send_warning_to_client(client_address)
        time.sleep(1) # Sleep for 1 second to avoid constant checking

session_timeout_thread = threading.Thread(target=check_session_timeout)
session_timeout_thread.start()

# Routes

@app.route('/', methods=['POST'])
def handle_request():
    global last_activity_times
    global client_address
    global client

    # Initialize session tracking variables
    last_activity_times = {}
    client = {}

    data = request.get_json()
    client_address = data.get('ip')
    client[client_address] = None
    print(f"[NEW CLIENT CONNECTED] IP: {client_address}")

    # Acknowledge successful connection
    acknowledgment_message = 'Connection established'
    return jsonify(f'{acknowledgment_message}')

# 1. Create Account
@app.route('/create_account', methods=['POST'])
def rest_create_account():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    seller = create_account(username, password)
    route_handler = SellerRoutes()
    route_handler.create_seller(seller)

    return jsonify(f'Account created successfully for {username}!')

# 2. Login
@app.route('/login', methods=['POST'])
def rest_login():
    global last_activity_times
    global username
    global UserID
    data = request.get_json()
    seller = login(data.get('username'), data.get('password'))
    route_handler = SellerRoutes()
    result = route_handler.get_seller_id(seller)
    if result.msg != 'Invalid username or password':
        username = seller['name']
        UserID = result.msg
        client[client_address] = UserID
        print(f'{username} {UserID} has logged in')
        # Set last activity time for the new connection
        last_activity_times[client_address] = time.time()
        print(last_activity_times)
        return jsonify(f'Login successful! Welcome {username}')
    else:
        return jsonify('Username or Password invalid! Re-try')

# 3. Logout
@app.route('/logout', methods=['POST'])
def rest_logout():
    print(f"[CLIENT DISCONNECTED] {client_address}")
    keys_to_remove = [key for key, value in client.items() if value == UserID]
    for key in keys_to_remove:
        client.pop(key)
    return jsonify('Goodbye!')

# 4. Get Seller Rating
@app.route('/get_seller_rating', methods=['GET'])
def rest_get_seller_rating():
    if client[client_address] is not  None:
        print(UserID)
        route_handler = SellerRoutes()
        result = route_handler.get_seller_rating(UserID)
        print(result.posFb - 1)
        print(result.negFb - 1)
        # Set last activity time for the new connection
        last_activity_times[client_address] = time.time()
        return jsonify(f'Positive Feedbacks: {result.posFb - 1}, Negative Feedbacks: {result.negFb - 1}')
    else:
        print(f'{client_address} not logged in!')
        return jsonify('User not logged in!')

# 5. Put Item for Sale
@app.route('/put_item_for_sale', methods=['POST'])
def rest_put_item_for_sale():
    if client[client_address] is not  None:
        # Set last activity time for the new connection
        last_activity_times[client_address] = time.time()
        data = request.get_json()
        item = create_item_for_sale(data.get('item_name'), data.get('item_category'), data.get('keywords'),
                                    data.get('condition'), data.get('sale_price'), str(UserID), data.get('quantity'))
        route_handler = SellerRoutes()
        result = route_handler.put_item_for_sale(item)
        print(f'{result} changes made to database by {UserID}')
        return jsonify(f'Product: {data.get("Pname")} saved. Quantity: {data.get("quant")}')
    else:
        print(f'{client_address} not logged in!')
        return jsonify('User not logged in!')

# 6. Change Sale Price
@app.route('/change_sale_price', methods=['PUT'])
def rest_change_sale_price():
    data = request.get_json()
    print(client[client_address])
    if client[client_address] is not  None:
        # Set last activity time for the new connection
        last_activity_times[client_address] = time.time()
        item = {}
        item['price'] = data.get('new_sale_price')
        item['id'] = data.get('item_id')
        item['sellerId'] = UserID
        route_handler = SellerRoutes()
        result = route_handler.change_sale_price(item)
        print(result)
        print(f'{UserID} changed price to {item["price"]} of product {item["id"]}')
        return jsonify(f'Product: {item["id"]} price changed to ${item["price"]}')
    else:
        print(f'{client_address} not logged in!')
        return jsonify('User not logged in!')

# 7. Remove Item from Sale
@app.route('/remove_item_from_sale', methods=['DELETE'])
def rest_remove_item_from_sale():
    data = request.get_json()
    if client[client_address] is not  None:
        # Set last activity time for the new connection
        last_activity_times[client_address] = time.time()
        item = {}
        item['quantity'] = data.get('item_quantity')
        item['id'] = data.get('item_id')
        item['sellerId'] = UserID
        route_handler = SellerRoutes()
        result = route_handler.remove_item(item)
        print(result)
        print(f'{UserID} removed #{item["quantity"]} of product {item["id"]}')
        return jsonify( f'Product: {item["id"]} quantity changed to {item["quantity"]}')
    else:
        print(f'{client_address} not logged in!')
        return jsonify('User not logged in!')

# 8. Display Items on Sale
@app.route('/display_items_on_sale', methods=['GET'])
def rest_display_items_on_sale():
    global client_address
    if client[client_address] is not  None:
        # Set last activity time for the new connection
        last_activity_times[client_address] = time.time()
        print(UserID)
        route_handler = SellerRoutes()
        items = route_handler.display_items(UserID)
        print(items)
        # Convert set to a list of dictionaries
        items_list_of_dicts = [
            {
                'name': item.name,
                'category': item.category,
                'price': item.price,
                'id': item.id,
                'keywords': item.keywords,
                'cond': item.cond,
                'quantity': item.quantity,
                'sellerId': item.sellerId
            } for item in items.items
        ]
        print(items_list_of_dicts)
        return jsonify(items_list_of_dicts)
    else:
        print(f'{client_address} not logged in!')
        return jsonify('User not logged in!')

if __name__ == "__main__":
    try:
        app.run(host='localhost', port=5001, debug=False)  # 10.200.194.61
    finally:
        # Gracefully terminate the session_timeout_thread
        session_timeout_thread.join()
