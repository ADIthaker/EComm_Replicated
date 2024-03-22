import sys
import os
from dotenv import load_dotenv
load_dotenv(override=True)

sys.path.append(os.environ.get("DIR"))
# Added the above import cause I was facing ModuleImportError
from flask import Flask, request, jsonify
from routes.buyer_routes import BuyerRoutes
import time
import threading

app = Flask(__name__)

# Session timeout configuration
SESSION_TIMEOUT = 300  # 5 minutes
WARNING_THRESHOLD = 240  # 4 minutes

# Global variables for session tracking
last_activity_times = {}
client = {}
cart = {}

# Buyer-related functions
def create_buyer_account(username, password):
    buyer = {}
    buyer['name'] = username
    buyer['password'] = password
    buyer['items'] = 1
    return buyer

def login(username, password):
    buyer = {'name': username, 'pwd': password}
    return buyer

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

    buyer = create_buyer_account(username, password)
    route_handler = BuyerRoutes()
    route_handler.create_buyer(buyer)

    return jsonify(f'Account created successfully for {username}!')

# 2. Login
@app.route('/login', methods=['POST'])
def rest_login():
    global last_activity_times
    global username
    global UserID
    data = request.get_json()
    buyer = login(data.get('username'), data.get('password'))
    route_handler = BuyerRoutes()
    result = route_handler.get_buyer_id(buyer)
    if result.msg != 'Invalid username or password':
        username = buyer['name']
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
        seller_id = request.get_json()
        route_handler = BuyerRoutes()
        result = route_handler.get_seller_rating(seller_id)
        print(type(result.posFb))
        last_activity_times[client_address] = time.time()
        return jsonify(f'Positive Feedbacks: {result.posFb-1}, Negative Feedbacks: {result.negFb-1}')
    else:
        print(f'{client_address} not logged in!')
        return jsonify('User not logged in!')
    
# 5. Search Available Items
@app.route('/search_available_items', methods=['GET'])
def rest_search_available_items():
    if client[client_address] is not  None:
        data = request.get_json()
        search = {'category': data.get('item_category'), 'keywords': data.get('keywords')}
        route_handler = BuyerRoutes()
        results = route_handler.get_available_items(search)
        print(results)
        
        # Process and format the results
        formatted_results = [
            {
                'name': result.name,
                'category': result.category,
                'id': result.id,
                'keywords': result.keywords,
                'condition': 'NEW' if result.cond == 1 else 'OLD',
                'price': result.price,
                'quantity': result.quantity
            } for result in results.items
        ]
        
        # Set last activity time for the new connection
        last_activity_times[client_address] = time.time()
        return jsonify(formatted_results)
    else:
        print(f'{client_address} not logged in!')
        return jsonify('User not logged in!')
    
# 6. Add Item to Cart
@app.route('/add_to_cart', methods=['POST'])
def rest_add_to_cart():
    global last_activity_times
    global username
    global UserID
    global cart
    
    data = request.get_json()
    if client[client_address] is not  None:
        cart[data.get('item_id')] = data.get('quantity')
        print(cart)
        return jsonify(f'#{data.get("quantity")} of Item {data.get("item_id")} added to the cart!')
    else:
        return jsonify('You are not logged in!')
    
# 7. Remove Item from Cart
@app.route('/remove_item_from_cart', methods=['POST'])
def rest_remove_item_from_cart():
    global last_activity_times
    global username
    global UserID
    global cart

    if client[client_address] is not  None:
        if cart:
            item_id_to_remove = request.get_json()
            if item_id_to_remove in cart:
                cart.pop(item_id_to_remove)
                return jsonify(f'{item_id_to_remove} removed from the cart successfully')
            else:
                return jsonify(f'Item {item_id_to_remove} not found in the cart')
        else:
            return jsonify('Cart for current session is empty. Add items and try again!')
    else:
        return jsonify('You are not logged in!')
    
# 8. Display Items in Cart
@app.route('/display_items_in_cart', methods=['GET'])
def rest_display_items_in_cart():
    global last_activity_times
    global username
    global UserID
    global cart

    route_handler = BuyerRoutes()

    if client[client_address] is not  None:
        print(f"Displayed unsaved cart to {username}")
        if cart:
            cart_items = [{'product': key, 'quantity': values} for key, values in cart.items()]
            return jsonify(cart_items)
        else:
            result = route_handler.get_cart(UserID)
            print(result)
            if result:
                cart_items_db = [{'prod': ids.id, 'quant': quantities.q} for ids, quantities in zip(result.ids, result.quantities)]
                cart = cart_items_db # poplulate the cart for the current session with the data saved in DB
                print(cart)
                return jsonify(cart_items_db)
            else:
                print("No cart displayed")
                return jsonify('Your cart is empty! Consider adding items')
    else:
        return jsonify('You are not logged in!')
    
# 9. Buy Cart
@app.route('/buy_cart', methods=['POST']) # TODO
def rest_buy_cart():
    global last_activity_times
    global username
    global UserID
    global cart
    route_handler = BuyerRoutes()

    data = request.get_json()
    purchase_req = {
        "cardno": data.get("cardNo"),
        "expiry":data.get("expiry"),
        "name": username,
        "buyer_id": UserID
    }
    if client[client_address] is not  None:
        if cart:
            route_handler.make_purchase_cart(cart, purchase_req)
            cart.clear()  # Clear the cart after a successful purchase
            return jsonify('Purchase made successfully')
        else:
            result = route_handler.get_cart(UserID)
            if result:
                route_handler.make_purchase_db(purchase_req)
                return jsonify('Purchase made successfully')
            else:
                return jsonify('Your cart is empty! Consider adding items')
    else:
        return jsonify('You are not logged in!')
    
# 10. Clear Cart
@app.route('/clear_cart', methods=['DELETE'])
def rest_clear_cart():
    global last_activity_times
    global username
    global UserID
    global cart

    if client[client_address] is not  None:
        if cart:
            cart.clear()
            return jsonify('Cart emptied!!')
        else:
            return jsonify('Cart for the current session is empty. Add items and try again!')
    else:
        return jsonify('You are not logged in!')
    
# 11. Save Cart
@app.route('/save_cart', methods=['POST'])
def rest_save_cart():
    global last_activity_times
    global username
    global UserID
    global cart
    route_handler = BuyerRoutes()
    if client[client_address] is not  None:
        if cart:
            route_handler.save_cart(cart, UserID)
            cart.clear()  # Clear the cart after saving
            return jsonify(f'****{username}\'s cart is saved****\nCurrent cart emptied')
        else:
            return jsonify('Cart for the current session is empty. Add items and try again!')
    else:
        return jsonify('You are not logged in!')
    
# 12. Get Purchase History
@app.route('/get_purchase_history', methods=['GET']) # TODO needs to checked after implementing make_purchase
def rest_get_purchase_history():
    global last_activity_times
    global username
    global UserID

    route_handler = BuyerRoutes()  # Create an instance of the BuyerRoutes class

    if client[client_address] is not  None:
        results = route_handler.get_history(UserID)
        if results:
            # Construct a response with the purchase history
            purchase_history = '\n'.join([f'You have bought\n***{result}***' for result in results])
            return jsonify(purchase_history)
        else:
            return jsonify('You have no purchase history.')
    else:
        return jsonify('You are not logged in!')
    
# 13. Provide Feedback
@app.route('/provide_feedback', methods=['POST']) # There is some weird bug here related to positive feedbacks
def rest_provide_feedback():
    global last_activity_times
    global username
    global UserID

    route_handler = BuyerRoutes()  # Create an instance of the BuyerRoutes class
    Feedbacks = []
    data = request.get_json()
    print(data)
    Feedbacks.append(data)
    
    if client[client_address] is not None:
        route_handler.provide_feedback(Feedbacks)
        return jsonify('Thank you for providing feedback!')
    else:
        return jsonify('You are not logged in!')
    
if __name__ == "__main__":
    try:
        app.run(host='localhost', port=5002, debug=True)  # 10.200.194.61
    finally:
        # Gracefully terminate the session_timeout_thread
        session_timeout_thread.join()
