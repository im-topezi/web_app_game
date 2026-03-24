from flask import Flask
import modules.login as login
from flask import redirect, render_template, request, flash, session
import modules.config as config
from functools import wraps
import modules.game as game


app = Flask(__name__)
app.secret_key = config.secret_key

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("username"):
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login",methods=["POST","GET"])
def login_page():
    if request.method=="GET":
        if session.get("username"):
            return redirect("/")
        return render_template("login.html",username="")
    if request.method=="POST":
        username=request.form["username"]
        password=request.form["password"]
        if login.login_succesfully(username,password):
            session["username"]=username
            flash(f"Succesfully logged in as {username}")
            return redirect("/")
        else:
            flash("Wrong username or password")
            return render_template("login.html",username=username)



@app.route("/register", methods=["POST","GET"])
def register():
    if request.method=="GET":
        return render_template("register.html",username="")
    if request.method=="POST":
        message=login.create_new_user(request.form["username"],request.form["password1"],request.form["password2"])
        flash(message)
        if message=="User created succesfully":
            return redirect("/login")
        else:
            username=request.form["username"]
            return render_template("register.html",username=username)
        

@app.route("/logout",methods=["POST"])
def logout():
    del session["username"]
    return redirect("/")


@app.route("/play")
@login_required
def play():
    tile=game.tile_details(0,0)
    return render_template("gameboard.html",connected=tile["connected"],npcs=tile["npcs"],objects=tile["objects"])