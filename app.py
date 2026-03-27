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
    if hasattr(session,"location"):
        player_coordinates=session["location"]
    else:
        player_coordinates=(0,0)
        session["location"]=player_coordinates
    tile=game.tile_details(player_coordinates)
    return render_template("gameboard.html",connected=tile["connected"],npcs=tile["npcs"],objects=tile["objects"])


@app.route("/inventory")
@login_required
def inventory():
    items=game.get_player_items(session["username"])
    return render_template("inventory.html",items=items,previous_page=request.referrer)


@app.route("/loot",methods=["POST","GET"])
@login_required
def loot():
    if request.method=="GET":
        container_id=request.args.get("container_id")
        if request.args.get("action")=="loot":
            items=game.get_container_items(container_id)
            return render_template("loot.html",items=items,container_id=container_id)
        
    if request.method=="POST":
        item_id=request.form["item_id"]
        container_id=request.form["container_id"]
        game.take_item(item_id,session["username"])
        items=game.get_container_items(container_id)
        return redirect(request.referrer)
    

@app.route("/drop",methods=["POST"])
@login_required
def drop():
        item_id=request.form["item_id"]
        message=game.drop_item(item_id,session["username"])
        flash(message)
        return redirect("/inventory")