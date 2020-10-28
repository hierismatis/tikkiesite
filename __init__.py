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
addtikkie_put_args.add_argument("name", type=str, help="What is the tikkie for?", required=True)
addtikkie_put_args.add_argument("url", type=str, help="The url of the tikkie", required=True)
addtikkie_put_args.add_argument("payers", type=str, help="People who have to pay", required=True)
addtikkie_put_args.add_argument("date", type=str, help="The date the money was spend", required=True)

class LogIn(Resource):
	def post(self):
		args = login_post_args.parse_args()
		name, password = args["name"], args["password"]

		user_data = get_data("users")
		user_info = user_data[name]

		if not check_login(name, password):
			return {"Authorization error": "Bad credentials"}, 403

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
		name, url, payers, date = args["name"], args["url"], args["payers"].split(","), args["date"]
		print(payers)
		return payers

api.add_resource(LogIn, "/login")
api.add_resource(ChangePassword, "/changepass")
api.add_resource(AddTikkie, "/addtikkie")

if __name__ == "__main__":
	app.run(debug=True)