from flask import Flask
import modules.login as login
from flask import redirect, render_template, request, flash, session, abort
import modules.config as config
from functools import wraps
import modules.game as game
import modules.marketplace as marketplace
import modules.world_generation as world
import secrets


app = Flask(__name__)
app.secret_key = config.secret_key

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("username"):
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def cant_be_in_game(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("username"):
            tile=game.check_if_in_game(session["username"])
            if tile:
                session["location"]=tile[0]["tile"]
                return redirect("/play")
        return f(*args, **kwargs)
    return decorated_function

def check_csrf():
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)




@app.route("/")
@cant_be_in_game
def index():
    worlds=[]
    if session.get("username"):
        worlds=game.get_user_worlds(session["username"])
    return render_template("index.html",worlds=worlds)

@app.route("/new_world",methods=["POST"])
@login_required
@cant_be_in_game
def generate_new_world():
    check_csrf()
    if request.form["world_name"]:
        world.World(16,session["username"],request.form["world_name"]).generate_world()
        flash("New world generated!")
    else:
        flash("World needs a name!")
    return redirect("/")

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
            session["csrf_token"] = secrets.token_hex(16)
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
        

@app.route("/logout")
def logout():
    del session["csrf_token"]
    del session["username"]
    if session.get("location"):
        del session["location"]
    return redirect("/")


@app.route("/play", methods=["POST","GET"])
@login_required
def play():
    if request.method=="GET":
        if session.get("location"):
            print(session["location"])
            tile=game.tile_details(session["location"])
            return render_template("gameboard.html",connected=tile["connected"],npcs=tile["npcs"],objects=tile["objects"],tile_type=tile["tile_type"])
        else:
            flash("You're not on an adventure, choose a world to play!")
            return redirect("/")

    elif request.method=="POST":
        world_id=request.form["world_id"]
        location=game.visit_world(world_id,session["username"])
        if location:
            session["location"]=location[0]["tile"]
            
            return redirect("/play")
        else:
            flash("World is not available")
            return redirect("/")



@app.route("/inventory")
@login_required
def inventory():
    items=game.get_player_items(session["username"])
    return render_template("inventory.html",items=items,previous_page=request.referrer if request.referrer else "")


@app.route("/loot",methods=["POST","GET"])
@login_required
def loot():
    if request.method=="GET":
        container_id=request.args.get("container_id")
        items=game.get_container_items(container_id)
        return render_template("loot.html",items=items,container_id=container_id)
        
    if request.method=="POST":
        check_csrf()
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
        check_csrf()
        item_id=request.form["item_id"]
        message=game.drop_item(item_id,session["username"])
        flash(message)
        return redirect("/inventory")


@app.route("/marketplace")
@login_required
@cant_be_in_game
def use_marketplace():
    query=request.args.get("query")
    items=marketplace.get_listed_items(query)
    return render_template("marketplace.html",items=items)


@app.route("/sell",methods=["GET","POST"])
@login_required
@cant_be_in_game
def sell():
    if request.method=="GET":
        item_id=request.args.get("item_id")
        item=marketplace.check_item_owner(item_id,session["username"])
        if item:
            return render_template("sell.html",item=item[0])
        else:
            abort(403)
    if request.method=="POST":
        check_csrf()
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
@cant_be_in_game
def buy():
    check_csrf()
    item_id=request.form["item_id"]
    seller=request.form["seller"]
    result=marketplace.trade_item(item_id,session["username"],seller)
    flash(result)
    return redirect("/marketplace")


@app.route("/cancel",methods=["POST"])
@login_required
@cant_be_in_game
def cancel():
    check_csrf()
    item_id=request.form["item_id"]
    result=marketplace.cancel_listing(item_id,session["username"])
    flash(result)
    return redirect("/marketplace")

@app.route("/move",methods=["POST"])
@login_required
def move():
    check_csrf()
    target_tile=request.form["tile"]
    current_tile=session["location"]
    if game.move(target_tile,current_tile):
        updated=game.update_location(current_tile,target_tile,session["username"])
        if updated==1:
            session["location"]=target_tile
    return redirect("/play")


@app.route("/leave", methods=["POST"])
@login_required
def leave():
    check_csrf()
    updated=game.update_location(session["location"],None,session["username"])
    if updated==1:
        del session["location"]
    return redirect("/")