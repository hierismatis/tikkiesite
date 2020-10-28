from flask import Flask
from flask_restful import Api, Resource, reqparse
from backendfunctions import *
import json
import hashlib

app = Flask(__name__)
app.config["SECRET_KEY"] = "6810527e5f4636beca705e70625e96bc"
api = Api(app)

login_post_args = reqparse.RequestParser()
login_post_args.add_argument("name", type=str, help="Login name", required=True)
login_post_args.add_argument("password", type=str, help="Login password", required=True)

changepass_put_args = reqparse.RequestParser()
changepass_put_args.add_argument("name", type=str, help="Login name", required=True)
changepass_put_args.add_argument("oldpass", type=str, help="Old/current login password", required=True)
changepass_put_args.add_argument("newpass", type=str, help="New/future login password", required=True)
changepass_put_args.add_argument("newpass1", type=str, help="Duplicate of newpass", required=True)

addtikkie_put_args = reqparse.RequestParser()
addtikkie_put_args.add_argument("name", type=str, help="Login name", required=True)
addtikkie_put_args.add_argument("password", type=str, help="Login password", required=True)
addtikkie_put_args.add_argument("tikkiename", type=str, help="What is the tikkie for?", required=True)
addtikkie_put_args.add_argument("url", type=str, help="The url of the tikkie", required=True)
addtikkie_put_args.add_argument("payers", type=str, help="People who have to pay", required=True)
addtikkie_put_args.add_argument("date", type=str, help="The date the money was spend", required=True)

pay_post_args = reqparse.RequestParser()
pay_post_args.add_argument("name", type=str, help="Login name", required=True)
pay_post_args.add_argument("password", type=str, help="Login password", required=True)
pay_post_args.add_argument("tikkieid", type=str, help="Id of the tikkie you paid", required=True)


class LogIn(Resource):
	def post(self):
		args = login_post_args.parse_args()
		name, password = args["name"], args["password"]

		if not check_login(name, password):
			return {"Authorization error": "Bad credentials"}, 403

		user_data = get_data("users")
		user_info = user_data[name]
		return user_info, 200

class ChangePassword(Resource):
	def put(self):
		args = changepass_put_args.parse_args()
		name, oldpass, newpass, newpass1 = args["name"], args["oldpass"], args["newpass"], args["newpass1"]

		if newpass != newpass1:
			return {"Authorization error": "New passwords don't are not the same!"}, 403

		if not check_login(name, oldpass):
			return {"Authorization error": "Bad credentials"}, 403

		user_data = get_data("users")
		user_data[name]["password"] = password_hasher(newpass)
		put_data("users", user_data)

		return {"Password change": "Succes"}, 200

class AddTikkie(Resource):
	def put(self):
		args = addtikkie_put_args.parse_args()
		name, password, t_name, t_url, t_payers, t_date = args["name"], args["password"], args["tikkiename"], args["url"], args["payers"].split(","), args["date"]


		tikkies = get_data("tikkies")
		user_data = get_data("users")

		if not check_login(name, password):
			return {"Authorization error": "Bad credentials"}, 403

		if set(t_payers) & set(user_data.keys()) != set(t_payers):
			return {"Bad request": "Not all payers are users"}, 400

		if len(tikkies) != 0:
			t_id = tikkies[len(tikkies)-1]["id"]+1
		else:
			t_id = 0

		tikkie = {
		"id": t_id,
		"creator": name,
		"name": t_name,
		"url": t_url,
		"unpaid": t_payers,
		"paid": [],
		"date": t_date
		}

		tikkies.append(tikkie)
		put_data("tikkies", tikkies)

		for payer in t_payers:
			user_data[payer]["tikkies"].append(t_id)
		
		put_data("users", user_data)

		return {"Tikkie added": "Succes"}, 201

class Payed(Resource):
	def post(self):
		args = pay_post_args.parse_args()
		name, password, t_id = args["name"], args["password"], args["tikkieid"]

		user_data = get_data("users")
		tikkies = get_data("tikkies")

		if not check_login(name, password):
			return {"Authorization error": "Bad credentials"}, 403

		try:
			t_id = int(t_id)
		except ValueError:
			return {"Error": "Tikkie_id not convertable to int"}, 400

		if name not in tikkies[t_id]["unpaid"]:
			return {"Exception": "Tikkie already paid!"}, 202

		tikkies[t_id]["unpaid"].remove(name)
		tikkies[t_id]["paid"].append(name)

		user_data[name]["tikkies"].remove(t_id)
		user_data[name]["paid"].append(t_id)

		put_data("tikkies", tikkies)
		put_data("users", user_data)
		
		return {"Tikkie paid": "Succes"}

api.add_resource(LogIn, "/login")
api.add_resource(ChangePassword, "/changepass")
api.add_resource(AddTikkie, "/addtikkie")
api.add_resource(Payed, "/pay")

if __name__ == "__main__":
	app.run(debug=True)