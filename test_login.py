import requests

url_otp = 'http://localhost:5000/api/request-otp'
data = {
    "email": "admin@l2f.com",
    "password": "boss@123"
}

response = requests.post(url_otp, json=data)
print(f"OTP Request Status: {response.status_code}")
res_json = response.json()
print(f"OTP Response: {res_json}")

if response.status_code == 200:
    otp = res_json.get("dev_otp")
    print(f"Got OTP: {otp}")
    
    url_login = 'http://localhost:5000/api/admin-login'
    login_data = {
        "email": "admin@l2f.com",
        "password": "boss@123",
        "otp": otp
    }
    
    login_res = requests.post(url_login, json=login_data)
    print(f"Login Status: {login_res.status_code}")
    print(f"Login Response: {login_res.json()}")
