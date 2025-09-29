import urllib.request
import json

url = "http://localhost:5000/login"
data = json.dumps({"username": "admin", "password": "admin123"}).encode("utf-8")
headers = {"Content-Type": "application/json"}

try:
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req) as response:
        print(f"Status Code: {response.getcode()}")
        print(f'Response: {response.read().decode("utf-8")}')
        print(f'Cookies: {response.headers.get_all("Set-Cookie")}')
except Exception as e:
    print(f"Error: {e}")
