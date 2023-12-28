from flask import render_template

from app import app


# Displays home page
@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")
