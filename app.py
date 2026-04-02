from flask import Flask
import modules.login as login
from flask import redirect, render_template, request, flash, session, abort
import modules.config as config
from functools import wraps
import modules.game as game
import modules.marketplace as marketplace


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
    
    return render_template("inventory.html",items=items,previous_page=request.referrer if request.referrer and "/sell" not in request.referrer else "")


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
        result=game.take_item(item_id,session["username"])
        if result==1:
            flash(f"{request.form["item_name"]} has been added to your inventory")
        items=game.get_container_items(container_id)
        return redirect(request.referrer)
    

@app.route("/drop",methods=["POST"])
@login_required
def drop():
        item_id=request.form["item_id"]
        message=game.drop_item(item_id,session["username"])
        flash(message)
        return redirect("/inventory")


@app.route("/marketplace")
@login_required
def use_marketplace():
    query=request.args.get("query")
    items=marketplace.get_listed_items(query)
    return render_template("marketplace.html",items=items)


@app.route("/sell",methods=["GET","POST"])
@login_required
def sell():
    if request.method=="GET":
        item_id=request.args.get("item_id")
        item=marketplace.check_item_owner(item_id,session["username"])
        if item:
            return render_template("sell.html",item=item[0])
        else:
            abort(403)
    if request.method=="POST":
        item_id=request.form["item_id"]
        market_price=request.form["market_price"]
        if int(market_price) < 1:
            flash("Price has to be more than 0")
            return redirect("/inventory")
        item=marketplace.check_item_owner(item_id,session["username"])
        if item:
            result=marketplace.put_item_for_sale(item_id,market_price)
            if result==1:
                flash(f"{item[0]["item_name"]} has been listed to the marketplace")
            else:
                flash(result)
            return redirect("/inventory")
        else:
            abort(403)


@app.route("/buy",methods=["POST"])
@login_required
def buy():
    item_id=request.form["item_id"]
    seller=request.form["seller"]
    result=marketplace.trade_item(item_id,session["username"],seller)
    flash(result)
    return redirect("/marketplace")


@app.route("/cancel",methods=["POST"])
@login_required
def cancel():
    item_id=request.form["item_id"]
    result=marketplace.cancel_listing(item_id,session["username"])
    flash(result)
    return redirect("/marketplace")