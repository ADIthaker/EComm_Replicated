import requests
import time

SERVER_IP = '10.128.0.7'
SERVER_PORT = 5002  # Assuming the Buyer server is running on port 5002
BASE_URL = f'http://{SERVER_IP}:{SERVER_PORT}'

RUNS = 10
API_INVOCATIONS_PER_RUN = 1000

headers = {'Content-Type': 'application/json'}

login_payload = {'username': 'Adi', 'password': 'Adi'}
login_url = f'{BASE_URL}/login'

get_seller_rating_payload = {'seller_id': '75eb5506d23a11eeb43842010a800008'}
get_seller_rating_url = f'{BASE_URL}/get_seller_rating'

add_to_cart_payload = {'item_id': '9d950f40d23d11eeb43842010a8000081', 'quantity': 10}
add_to_cart_url = f'{BASE_URL}/add_to_cart'

logout_url = f'{BASE_URL}/logout'

response_times = []

def send_request(url, payload=None):
    if payload:
        response = requests.post(url, json=payload, headers=headers)
    else:
        response = requests.post(url, headers=headers)
    print(response.text)  # Assuming the server responds with some message

# Login
send_request(login_url, login_payload)

# Perform 1000 API invocations for each run
for _ in range(RUNS):
    start_time = time.time()

    for _ in range(API_INVOCATIONS_PER_RUN):
        send_request(get_seller_rating_url, get_seller_rating_payload)
        send_request(add_to_cart_url, add_to_cart_payload)
        
    end_time = time.time()
    response = end_time - start_time
    response_times.append(response)

# Logout
send_request(logout_url)

# Calculate and print the average throughput
average_throughput = (API_INVOCATIONS_PER_RUN * RUNS) / sum(response_times)
print(f"Average Server Throughput: {average_throughput} API invocations per second")
