import requests

url = "http://localhost:5000/login"
headers = {"Content-Type": "application/json"}
data = {"username": "admin", "password": "admin123"}

try:
    response = requests.post(url, json=data, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    print(f"Cookies: {response.cookies}")
except Exception as e:
    print(f"Error: {e}")
