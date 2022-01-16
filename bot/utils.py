import requests

def signup(username, password, email, full_name):
    payload = {}
    payload["username"] = username
    payload["password"] = password
    payload["email"] = email
    payload["full_name"] = full_name

    r = requests.post(url="http://0.0.0.0:8000/user/signup", json=payload)
    
    return r
    
def login(username, password):
    payload = {}
    payload["username"] = username
    payload["password"] = password
    
    r = requests.post(url="http://0.0.0.0:8000/user/login", json=payload)
    
    return r

def create_post(title, content, token):
    payload = {}
    payload["title"] = title
    payload["description"] = content
    
    headers = {'Authorization': "Bearer {}".format(token)}

    r = requests.post(url="http://0.0.0.0:8000/post/create", json=payload, headers=headers)

    return r

def like(id, token):
    headers = {'Authorization': "Bearer {}".format(token)}

    r = requests.get(url="http://0.0.0.0:8000/post/like/{}".format(id), headers=headers)
    
    return r