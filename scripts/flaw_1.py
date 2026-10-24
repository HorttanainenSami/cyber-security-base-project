import requests

BASE = "http://127.0.0.1:8000"
LOGIN = f"{BASE}/todo/accounts/login/"

session = requests.Session()
session.get(LOGIN) 
token = session.cookies["csrftoken"]
CORRECT_PASSWORD = "admin"
PASSES = 20
body = {
    "username": "admin",
    "password": "admin",
    "csrfmiddlewaretoken": token,
}
for i in range(1, PASSES + 1):
    if(i == PASSES):
        body["password"] = CORRECT_PASSWORD
    else:
        body["password"] = f"password{i}"
    session.post(LOGIN, data=body)
    if session.cookies.get("sessionid"):
        print(f"success with password: {body['password']}")
        break
else:
    print("failed")
