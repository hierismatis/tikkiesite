from flask import Flask, escape, request, render_template, url_for, flash, redirect
import os
import time
import random
import hashlib
import glob
from backendfunctions import *

app = Flask(__name__)
app.config["SECRET_KEY"] = "6810527e5f4636beca705e70625e96bc"


@app.route('/', methods=["POST", "GET"])
def Home():
	if request.method == "POST":
		password = request.form["pw"]
		name = request.form["name"]
		if not check_login(name, password):
			return render_template('login.html', falsepw=1)
	return render_template('login.html', falsepw=0)

if __name__ == "__main__":
	app.run(debug=True)
	