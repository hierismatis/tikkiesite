import json
import hashlib

def get_data(filename):
	with open(f'data\\{filename}.json', "r") as f:
	#with open('/var/www/webApp/data/'+filename+'.json', "r") as f:
		data = json.load(f)
	return data

def put_data(filename, data):
	with open(f'data\\{filename}.json', "w") as f:
	#with open('/var/www/webApp/data/'+filename+'.json', "w") as f:
		json.dump(data, f)

def password_hasher(password):
	return hashlib.sha256(password.encode('utf-8')).hexdigest()

def check_login(name, password):
	user_data = get_data("users")

	if name not in user_data.keys():
		return False

	user_info = user_data[name]
	password = password_hasher(password)
	if password != user_info["password"]:
		return False

	return True