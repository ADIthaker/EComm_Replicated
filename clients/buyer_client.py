import requests
import json
import socket

API_BASE_URL = 'http://localhost:5002'  # 10.200.194.61

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

# Function to create a new account
def create_account():
    username = input("Enter username: ")
    password = input("Enter password: ")
    response = requests.post(f"{API_BASE_URL}/create_account", json={'username': username, 'password': password})
    response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
    data = response.json()
    print(data)

# Function to log in
def login():
    username = input("Enter username: ")
    password = input("Enter password: ")
    response = requests.post(f"{API_BASE_URL}/login", json={'username': username, 'password': password})
    response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
    data = response.json()
    print(data)

# Function to log out
def logout():
    response = requests.post(f"{API_BASE_URL}/logout")
    response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
    data = response.json()
    print(data)

# Function to get seller rating
def get_seller_rating():
    seller_id = input('Provide seller ID: ')
    response = requests.get(f"{API_BASE_URL}/get_seller_rating", json=seller_id)
    response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
    data = response.json()
    print(data)

# Function to search for items for sale
def search_available_items():
    item_category = int(input("Enter item category: "))
    keywords = input("Enter keywords (comma-separated): ").split(',')
    req = {'item_category': item_category, 'keywords': ','.join(keywords)}
    response = requests.get(f"{API_BASE_URL}/search_available_items", json=req)
    response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
    data = response.json()
    for item in data:
        print('--------------')
        print(item)

# Function to add items to the cart
def add_to_cart():
    prodID = input('Enter Product ID:')
    prodQuant = int(input('Enter Quantity to purchase:'))
    cart = {'item_id': prodID, 'quantity': prodQuant}
    response = requests.post(f"{API_BASE_URL}/add_to_cart", json=cart)
    response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
    data = response.json()
    print(data)    

# Function to remove an item from the cart
def remove_item_from_cart():
    item_id = input("Enter item ID: ")
    response = requests.post(f"{API_BASE_URL}/remove_item_from_cart", json=item_id)
    response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
    data = response.json()
    print(type(data)) 

# Function to display items in the cart
def display_items_in_cart():
    response = requests.get(f"{API_BASE_URL}/display_items_in_cart")
    response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
    data = response.json()
    if type(data) == list:
        for item in data:
            print('--------------')
            print(item)
    else:
        print(data)

# Function to buy items in the cart
def buy_cart():
    cardNo = input("Enter card no: ")
    expiry = input("Card Expiry")
    card = {"cardNo": cardNo, "expiry": expiry}
    response = requests.post(f"{API_BASE_URL}/buy_cart", json=card)
    response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
    data = response.json()
    print(data)

# Function to clear the cart
def clear_cart():
    response = requests.delete(f"{API_BASE_URL}/clear_cart")
    response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
    data = response.json()
    print(data)

# Function to save the cart
def save_cart():
    response = requests.post(f"{API_BASE_URL}/save_cart")
    response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
    data = response.json()
    print(data)

# Function to get purchase history
def get_purchase_history():
    response = requests.get(f"{API_BASE_URL}/get_purchase_history")
    response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
    data = response.json()
    print(data)

# Function to provide feedback
def provide_feedback():
    sellerID = input("Enter sellerID: ")
    feedback = int(input("Enter feedback (1/0): "))
    response = requests.post(f"{API_BASE_URL}/provide_feedback", json={'sellerId': sellerID, 'feedback': feedback})
    response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
    data = response.json()
    print(data)

# Notify the server of the new client
notify_server()

# Main interface function
def interface():
    while True:
        print("****Welcome to the E-Market Place****")
        print("\nBuyer Options:")
        print("1. Create Account")
        print("2. Login")
        print("3. Logout")
        print("4. Get Seller Rating")
        print("5. Search for items")
        print("6. Add items")
        print("7. Remove items")
        print("8. Show cart")
        print("9. Buy cart")
        print("10. Clear cart")
        print("11. Save Cart")
        print("12. Display purchase history")
        print("13. Provide feedback")
        print("14. Exit")

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
            search_available_items()
        elif choice == '6':
            add_to_cart()
        elif choice == '7':
            remove_item_from_cart()
        elif choice == '8':
            display_items_in_cart()
        elif choice == '9':
            buy_cart()
        elif choice == '10':
            clear_cart()
        elif choice == '11':
            save_cart()
        elif choice == '12':
            get_purchase_history()
        elif choice == '13':
            provide_feedback()
        elif choice == '14':
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 14.")

# Run the interface function
interface()
