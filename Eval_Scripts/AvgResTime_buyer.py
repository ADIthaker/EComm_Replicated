import requests
import time

SERVER_IP = '10.128.0.7'
SERVER_PORT = 5002  # Assuming the Buyer server is running on port 5002
BASE_URL = f'http://{SERVER_IP}:{SERVER_PORT}'

RUNS = 10

headers = {'Content-Type': 'application/json'}

# Assuming the login endpoint is '/login'
login_payload = {'username': 'Adi', 'password': 'Adi'}
login_url = f'{BASE_URL}/login'

# Assuming the get_seller_rating endpoint is '/get_seller_rating'
get_seller_rating_payload = {'seller_id': '75eb5506d23a11eeb43842010a800008'}
get_seller_rating_url = f'{BASE_URL}/get_seller_rating'

# Assuming the add_to_cart endpoint is '/add_to_cart'
add_to_cart_payload = {'item_id': '9d950f40d23d11eeb43842010a8000081', 'quantity': 10}
add_to_cart_url = f'{BASE_URL}/add_to_cart'

# Assuming the logout endpoint is '/logout'
logout_url = f'{BASE_URL}/logout'

response_times = []

def send_request(url, payload=None):
    start_time = time.time()
    if payload:
        response = requests.post(url, json=payload, headers=headers)
    else:
        response = requests.post(url, headers=headers)
    end_time = time.time()
    response_time = end_time - start_time
    print(response.text)  # Assuming the server responds with some message
    return response_time

# Login
send_request(login_url, login_payload)

# Measure response time for subsequent requests
for _ in range(RUNS):
    response_time = send_request(get_seller_rating_url, get_seller_rating_payload)
    response_times.append(response_time)

    response_time = send_request(add_to_cart_url, add_to_cart_payload)
    response_times.append(response_time)

# Logout
send_request(logout_url)

# Calculate and print the average response time
average_response_time = sum(response_times) / len(response_times)
print(f"Average Response Time: {average_response_time} seconds")
