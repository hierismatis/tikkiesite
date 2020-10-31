from flask import Flask
from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
from backendfunctions import *
from datetime import datetime

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

pay_post_args = reqparse.RequestParser()
pay_post_args.add_argument("name", type=str, help="Login name", required=True)
pay_post_args.add_argument("password", type=str, help="Login password", required=True)
pay_post_args.add_argument("tikkieid", type=str, help="Id of the tikkie you paid", required=True)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50), unique=True)
	password = db.Column(db.String(100))

class Tikkie(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	description = db.Column(db.String(200))
	creator = db.Column(db.String(50), db.ForeignKey("user.name"))
	url = db.Column(db.String(50), unique=True)
	date = db.Column(db.DateTime, default=datetime.now)
	paid = db.Column(db.String(300), default="")
	unpaid = db.Column(db.String(300))

class LogIn(Resource):
	def post(self):
		args = login_post_args.parse_args()
		name, password = args["name"], password_hasher(args["password"])

		user = User.query.filter_by(name=name).filter_by(password=password).first()

		if user is None:
			return {"Authorization error": "Bad credentials"}, 403
		return json.dumps(dict(name=user.name, password=user.password)), 200

class ChangePassword(Resource):
	def put(self):
		args = changepass_put_args.parse_args()
		name, oldpass, newpass, newpass1 = args["name"], args["oldpass"], args["newpass"], args["newpass1"]

		if newpass != newpass1:
			return {"Authorization error": "New passwords are not the same!"}, 403

		user = User.query.filter_by(name=name).filter_by(password=password_hasher(oldpass)).first()

		if user is None:
			return {"Authorization error": "Bad credentials"}, 403

		user.password = password_hasher(newpass)
		db.session.commit()

		return {"Password change": "Succes"}, 200

class AddTikkie(Resource):
	def put(self):
		args = addtikkie_put_args.parse_args()
		name, password, t_name, t_url, t_payers = args["name"], args["password"], args["tikkiename"], args["url"], args["payers"].split(",")

		if User.query.filter_by(name=name).filter_by(password=password_hasher(password)).first() is None:
			return {"Authorization error": "Bad credentials"}, 403

		users = map(lambda user: user.name, User.query.all())

		if set(t_payers) & set(users) != set(t_payers):
			return {"Bad request": "Not all payers are users"}, 400

		tikkie = Tikkie(creator=name, description=t_name, url=t_url, unpaid=",".join(t_payers))
		db.session.add(tikkie)
		db.session.commit()

		return {"success": True, "id": tikkie.id}, 201

class Payed(Resource):
	def post(self):
		args = pay_post_args.parse_args()
		name, password, t_id = args["name"], args["password"], args["tikkieid"]

		if User.query.filter_by(name=name).filter_by(password=password_hasher(password)).first() is None:
			return {"Authorization error": "Bad credentials"}, 403

		try:
			t_id = int(t_id)
		except ValueError:
			return {"Error": "Tikkie_id not convertable to int"}, 400

		tikkie = Tikkie.query.filter_by(id=t_id).first()

		if tikkie is None:
			return {"Error": "Tikkie not found"}, 400

		paid = tikkie.paid.split(",")
		unpaid = tikkie.unpaid.split(",")

		if name not in unpaid:
			return {"Exception": "Tikkie already paid!"}, 202

		paid.append(name)
		tikkie.paid = ",".join(paid)

		unpaid.remove(name)
		tikkie.unpaid = ",".join(unpaid)

		db.session.commit()
		
		return {"Tikkie paid": "Succes"}

api.add_resource(LogIn, "/login")
api.add_resource(ChangePassword, "/changepass")
api.add_resource(AddTikkie, "/addtikkie")
api.add_resource(Payed, "/pay")

if __name__ == "__main__":
	app.run(debug=True)