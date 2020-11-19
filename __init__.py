from flask import Flask, escape, request, render_template, url_for, flash, redirect, session
from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
from backendfunctions import *
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["SECRET_KEY"] = "6810527e5f4636beca705e70625e96bc"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(weeks=52)
api = Api(app)
db = SQLAlchemy(app)

###########################################################################
#DATABASE
###########################################################################
class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50), unique=True)
	password = db.Column(db.String(100))

	def __init__(self, name, password):
		self.name = name
		self.password = password

class Tikkie(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	description = db.Column(db.String(200))
	creator = db.Column(db.String(50), db.ForeignKey("user.name"))
	url = db.Column(db.String(50), unique=True)
	date = db.Column(db.DateTime, default=datetime.now())
	paid = db.Column(db.String(300), default="")
	unpaid = db.Column(db.String(300))
	amount = db.Column(db.Float)

	def __init__(self, description, creator, url, date, paid, unpaid, amount):
		self.description = description
		self.creator = creator
		self.url = url
		self.date = date
		self.paid = paid
		self.unpaid = unpaid
		self.amount = amount




# tikkie = Tikkie.query.filter_by(creator="David").first()
# db.session.delete(tikkie)
# db.session.commit()

###########################################################################
#WEBPAGE
###########################################################################
@app.route('/', methods=["POST", "GET"])
def login():

	try: 
		if User.query.filter_by(name=session["name"]).filter_by(password=session["password"]).first(): return redirect(url_for('homepage'))
		else: redirect(url_for('login'))
	except Exception: return redirect(url_for("login"))

	if request.method == "POST":
		name = request.form["name"].lower()
		password = request.form["pw"]

		if user := User.query.filter_by(name=name).filter_by(password=hash_password(password)).first():
			session["name"] = name
			session["password"] = hash_password(password)
			return redirect(url_for("homepage"))

		else:
			flash("Inlog gegevens kloppen niet!")
			return redirect(url_for('login'))

	return render_template('login.html')

@app.route("/loguit")
def loguit():
	session["name"] = None
	session["password"] = None
	flash("Je bent uitgelogd!", "info")
	return redirect(url_for("login"))

@app.route("/homepage")
def homepage():
	try: 
		if User.query.filter_by(name=session["name"]).filter_by(password=session["password"]).first(): pass
		else: redirect(url_for('login'))
	except Exception: return redirect(url_for("login"))

	if tikkies := Tikkie.query.filter(Tikkie.unpaid.like(f"%{session['name']}%")).all():
		tikkiejson = []
		for tikkie in reversed(tikkies):
			tikkiejson.append({"amount": tikkie.amount, "id": tikkie.id, "description": tikkie.description, "paid": tikkie.paid.split(","), "unpaid": tikkie.unpaid.split(","), "creator": tikkie.creator, 'url': tikkie.url, "date": tikkie.date.strftime("%Y-%m-%d")})
	else:
		tikkiejson = None

	return render_template("homepage.html", tikkies=tikkiejson)

@app.route("/mijntikkies")
def mijntikkies():
	try: 
		if User.query.filter_by(name=session["name"]).filter_by(password=session["password"]).first(): pass
		else: redirect(url_for('login'))
	except Exception: return redirect(url_for("login"))

	if tikkies := Tikkie.query.filter_by(creator=session["name"]).all():
		tikkiejson = []
		for tikkie in reversed(tikkies):
			tikkiejson.append({"amount": tikkie.amount, "id": tikkie.id, "description": tikkie.description, "paid": tikkie.paid.split(","), "unpaid": tikkie.unpaid.split(","), "creator": tikkie.creator, 'url': tikkie.url, "date": tikkie.date.strftime("%Y-%m-%d")})
	else:
		tikkiejson = None

	return render_template("mijntikkies.html", tikkies=tikkiejson)



@app.route("/alletikkies")
def alletikkies():
	try: 
		if User.query.filter_by(name=session["name"]).filter_by(password=session["password"]).first(): pass
		else: redirect(url_for('login'))
	except Exception: return redirect(url_for("login"))

	if tikkies := Tikkie.query.all():
		tikkiejson = []
		for tikkie in reversed(tikkies):
			tikkiejson.append({"amount": tikkie.amount, "id": tikkie.id, "description": tikkie.description, "paid": tikkie.paid.split(","), "unpaid": tikkie.unpaid.split(","), "creator": tikkie.creator, 'url': tikkie.url, "date": tikkie.date.strftime("%Y-%m-%d")})
	else:
		tikkiejson = None

	return render_template("alletikkies.html", tikkies=tikkiejson)




@app.route("/mijngegevens")
def mijngegevens():
	try: 
		if User.query.filter_by(name=session["name"]).filter_by(password=session["password"]).first(): pass
		else: redirect(url_for('login'))
	except Exception: return redirect(url_for("login"))

	return render_template("mijngegevens.html", name=session["name"])

@app.route("/tikkietoevoegen", methods=["POST", "GET"])
def tikkietoevoegen():
	try: 
		if User.query.filter_by(name=session["name"]).filter_by(password=session["password"]).first(): pass
		else: redirect(url_for('login'))
	except Exception: return redirect(url_for("login"))

	if request.method == "POST":
		amount = float(request.form["amount"].replace(",", "."))
		url = request.form["url"]
		description = request.form["description"]
		payers = ",".join(request.form.getlist('payers'))
		date = request.form["date"].split("-")
		date = datetime(int(date[0]), int(date[1]), int(date[2]))

		tikkie = Tikkie(description, session['name'], url, date, "", payers, amount) 
		db.session.add(tikkie)
		db.session.commit()
		flash("Tikkie succesvol toegevoegd!")
		return redirect(url_for("mijntikkies"))

	return render_template("tikkietoevoegen.html", users=[user.name for user in User.query.all()])

@app.route("/betaal")
def betaal():
	try: 
		if User.query.filter_by(name=session["name"]).filter_by(password=session["password"]).first(): pass
		else: redirect(url_for('login'))
	except Exception: return redirect(url_for("login"))

	if t_id := request.args.get('id', default=-1, type = int) == -1:
		return "dikke pech"
	tikkie = Tikkie.query.filter_by(id=int(t_id)).first()

	unpaid = tikkie.unpaid.split(",")
	paid = tikkie.paid.split(",")

	if session["name"] in unpaid:
		unpaid.remove(session["name"])
		paid.append(session["name"])
	tikkie.unpaid = ",".join(unpaid)
	tikkie.paid = ",".join(paid)
	db.session.commit()
	flash(f"Je hebt de tikkie voor {tikkie.description} betaald!")
	return redirect(url_for("homepage"))

@app.route("/verwijderen")
def verwijderen():
	try: 
		if User.query.filter_by(name=session["name"]).filter_by(password=session["password"]).first(): pass
		else: redirect(url_for('login'))
	except Exception: return redirect(url_for("login"))

	t_id = request.args.get('id', default=-1, type = int)

	if t_id == -1:
		return "dikke pech"
	tikkie = Tikkie.query.filter_by(id=int(t_id)).first()
	db.session.delete(tikkie)
	db.session.commit()
	flash(f"De tikkie is succesvol verwijderd!", "info")
	return redirect(url_for("mijntikkies"))

@app.route("/aanpassen", methods=["POST", "GET"])
def aanpassen():
	try: 
		if User.query.filter_by(name=session["name"]).filter_by(password=session["password"]).first(): pass
		else: redirect(url_for('login'))
	except Exception: return redirect(url_for("login"))

	t_id = request.args.get('id', default=-1, type = int)

	if t_id == -1:
		return "dikke pech"
	tikkie = Tikkie.query.filter_by(id=int(t_id)).first()

	if request.method == "POST":
		amount = float(request.form["amount"].replace(",", "."))
		url = request.form["url"]
		description = request.form["description"]
		payers = ",".join(request.form.getlist('payers'))
		date = request.form["date"].split("-")
		date = datetime(int(date[0]), int(date[1]), int(date[2]))
		paid = "".join([paid for paid in tikkie.paid.split(',') if paid not in payers.split(",")])


		tikkie.description, tikkie.url, tikkie.date, tikkie.unpaid, tikkie.amount, tikkie.paid = description, url, date, payers, amount, paid
		db.session.commit()
		flash("Tikkie succesvol aangepast!")
		return redirect(url_for("mijntikkies"))

	users = User.query.all()
	users = [user.name for user in users]
	tikkiejson = {"amount": tikkie.amount, "id": tikkie.id, "description": tikkie.description, "paid": tikkie.paid.split(","), "unpaid": tikkie.unpaid.split(","), "creator": tikkie.creator, 'url': tikkie.url, "date": tikkie.date.strftime("%Y-%m-%d")}
	return render_template("aanpassen.html", tikkie=tikkiejson, users=users)


###########################################################################
#API
###########################################################################
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

class ApiLogin(Resource):
	def post(self):
		args = login_post_args.parse_args()
		name, password = args["name"], hash_password(args["password"])


		user = User.query.filter_by(name=name).filter_by(password=password).first()

		if user is None:
			return {"Authorization error": "Bad credentials"}, 403, {"Access-Control-Allow-Origin": "*"}
		return {"login": "succes"}, 200, {"Access-Control-Allow-Origin": "*"}


class ChangePassword(Resource):
	def put(self):
		args = changepass_put_args.parse_args()
		name, oldpass, newpass, newpass1 = args["name"], args["oldpass"], args["newpass"], args["newpass1"]

		if newpass != newpass1:
			return {"Authorization error": "New passwords are not the same!"}, 403, {"Access-Control-Allow-Origin": "*"}

		user = User.query.filter_by(name=name).filter_by(password=hash_password(oldpass)).first()

		if user is None:
			return {"Authorization error": "Bad credentials"}, 403, {"Access-Control-Allow-Origin": "*"}

		user.password = hash_password(newpass)
		db.session.commit()

		return {"Password change": "Succes"}, 200, {"Access-Control-Allow-Origin": "*"}


class AddTikkie(Resource):
	def put(self):
		args = addtikkie_put_args.parse_args()
		name, password = args["name"], args["password"]
		t_name, t_url, t_payers = args["tikkiename"], args["url"], args["payers"].split(",")

		if User.query.filter_by(name=name).filter_by(password=hash_password(password)).first() is None:
			return {"Authorization error": "Bad credentials"}, 403, {"Access-Control-Allow-Origin": "*"}


		users = map(lambda user: user.name, User.query.all())

		if set(t_payers) & set(users) != set(t_payers):
			return {"Error": "not all payers are users!"}, 403

		tikkie = Tikkie(creator=name, description=t_name, url=t_url, unpaid=",".join(t_payers))
		db.session.add(tikkie)
		db.session.commit()

		return {"success": True, "id": tikkie.id}, 201, {"Access-Control-Allow-Origin": "*"}


class Payed(Resource):
	def post(self):
		args = pay_post_args.parse_args()
		name, password, t_id = args["name"], args["password"], args["tikkieid"]

		if User.query.filter_by(name=name).filter_by(password=hash_password(password)).first() is None:
			return {"Authorization error": "Bad credentials"}, 403, {"Access-Control-Allow-Origin": "*"}

		try:
			t_id = int(t_id)
		except ValueError:
			return {"Error": "Tikkie_id not convertable to int"}, 400, {"Access-Control-Allow-Origin": "*"}

		tikkie = Tikkie.query.filter_by(id=t_id).first()

		if tikkie is None:
			return {"Error": "Tikkie not found"}, 400

		paid = tikkie.paid.split(",")
		unpaid = tikkie.unpaid.split(",")

		if name not in unpaid:
			return {"Exception": "Tikkie already paid!"}, 202, {"Access-Control-Allow-Origin": "*"}

		paid.append(name)
		tikkie.paid = ",".join(paid)

		unpaid.remove(name)
		tikkie.unpaid = ",".join(unpaid)

		db.session.commit()

		return {"Tikkie paid": "Succes"}


api.add_resource(ApiLogin, "/api/login")
api.add_resource(ChangePassword, "/api/changepass")
api.add_resource(AddTikkie, "/api/addtikkie")
api.add_resource(Payed, "/api/pay")

if __name__ == "__main__":

	app.run(debug=True)
