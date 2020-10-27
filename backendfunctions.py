import json
import hashlib

def get_data(filename):
	with open(f'data\\{filename}.json', "r") as f:
	#with open(f'/var/www/webApp/data/{filename}.json') as f:
		data = json.load(f)
	return data

def put_data(filename, data):
	with open(f'data\\{filename}.json', "w") as f:
	#with open(f'/var/www/webApp/data/{filename}.json') as f:
		json.dump(data, f)

def password_hasher(password):
	return hashlib.sha256(password.encode('utf-8')).hexdigest()

def check_login(name, password):
	user_data = get_data("users")
	user_info = user_data[name]

	password = password_hasher(password)
	if name not in user_data.keys() or password != user_info["password"]:
		return False

	else:
		return True