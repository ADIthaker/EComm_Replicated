import requests
import json
import socket
import threading

API_BASE_URL = 'http://localhost:5006'  # 10.200.194.61

def notify_server():
    try:
        ip = socket.gethostbyname(socket.gethostname())
        response = requests.post(f"{API_BASE_URL}", json={'ip': ip})
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        data = response.json()

        # Check if the connection was established
        if data == 'Connection established':
            print(data)
        else:
            print('Connection unsuccessful!')
    except requests.exceptions.RequestException as e:
        print(f"Error during server notification: {e}")
    

def create_account():
    username = input("Enter username: ")
    password = input("Enter password: ")
    response = requests.post(f"{API_BASE_URL}/create_account", json={'username': username, 'password': password})
    response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
    data = response.json()
    print(data)

def login():
    username = input("Enter username: ")
    password = input("Enter password: ")
    response = requests.post(f"{API_BASE_URL}/login", json={'username': username, 'password': password})
    response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
    data = response.json()
    print(data)

def logout():
    response = requests.post(f"{API_BASE_URL}/logout")
    response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
    data = response.json()
    print(data)

def get_seller_rating():
    response = requests.get(f"{API_BASE_URL}/get_seller_rating")
    response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
    data = response.json()
    print(data)

def put_item_for_sale():
    item_name = input("Enter item name: ")
    item_category = int(input("Enter item category: "))
    keywords = input("Enter keywords (comma-separated): ").split(',')
    condition = int(input("Enter condition (New(1)/Used(0)): "))
    sale_price = int(input("Enter sale price: "))
    quantity = int(input("Enter quantity: "))
    data = {'item_name': item_name, 'item_category': item_category,
            'keywords': ','.join(keywords), 'condition': condition, 'sale_price': sale_price, 'quantity': quantity}
    response = requests.post(f"{API_BASE_URL}/put_item_for_sale", json=data)
    print(response.json())

def change_sale_price():
    item_id = input("Enter item ID: ")
    new_sale_price = int(input("Enter new sale price: "))
    data = {'item_id': item_id, 'new_sale_price': new_sale_price}
    response = requests.put(f"{API_BASE_URL}/change_sale_price", json=data)
    print(response.json())

def remove_item_from_sale():
    item_id = input("Enter item ID: ")
    item_quant = int(input("Enter item quantity:"))
    data = {'item_id': item_id, 'item_quantity': item_quant}
    response = requests.delete(f"{API_BASE_URL}/remove_item_from_sale", json=data)
    print(response.json())

def on_items_list(data):
    items_list = data

    if items_list:
        print("Items List on sale:")
        for item in items_list:
            item_output = (
                f"Item ID: {item['id']}\n"
                f"Name: {item['name']}\n"
                f"Category: {item['category']}\n"
                f"Price: ${item['price']}\n"
                f"Keywords: {item['keywords']}\n"
                f"Condition: {item['cond']}\n"
                f"Quantity: {item['quantity']}\n"
                f"Seller ID: {item['sellerId']}\n"
                "------"
            )
            print(item_output)
    else:
        print("Received an empty Items List")

def display_items_on_sale():
    response = requests.get(f"{API_BASE_URL}/display_items_on_sale")
    try:
        data = response.json()
        if data != 'User not logged in!':
            on_items_list(data)
        else:
            print(data)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")

# Notify the server of the new client
notify_server()

def interface():
    while True:
        print("\n****Welcome to the E-Market Place****")
        print("\nSeller Options:")
        print("1. Create Account")
        print("2. Login")
        print("3. Logout")
        print("4. Get Seller Rating")
        print("5. Put Item for Sale")
        print("6. Change Sale Price")
        print("7. Remove Item from Sale")
        print("8. Display Items on Sale")
        print("9. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            create_account()
        elif choice == '2':
            login()
        elif choice == '3':
            logout()
            break
        elif choice == '4':
            get_seller_rating()
        elif choice == '5':
            put_item_for_sale()
        elif choice == '6':
            change_sale_price()
        elif choice == '7':
            remove_item_from_sale()
        elif choice == '8':
            display_items_on_sale()
        elif choice == '9':
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 9.")

interface()
