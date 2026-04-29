from flask import Flask
import modules.login as login
from flask import redirect, render_template, request, flash, session, abort
import modules.config as config
from functools import wraps
import modules.game as game
import modules.marketplace as marketplace
import modules.world_generation as world
import modules.player as player
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

@app.before_request
def set_gold_amount():
    if session.get("username"):
        gold=marketplace.get_gold_amount(session["username"])
        session["gold"]=gold


@app.route("/")
@cant_be_in_game
def index():
    worlds=[]
    if session.get("username"):
        worlds=player.get_user_worlds(session["username"])
    return render_template("index.html",worlds=worlds)



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
    session.clear()
    return redirect("/")


@app.route("/inventory")
@login_required
def inventory():
    items=player.get_player_items(session["username"])
    worn_items=player.get_equipped_items(session["username"])
    stats=player.get_total_stats(session["username"])
    return render_template("inventory.html",items=items,worn_items=worn_items,stats=stats,previous_page=request.referrer if request.referrer else "")

#Add checks that you're in the same tile
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
        if result["rows_affected"]==1:
            flash(f"{request.form['item_name']} has been added to your inventory")
        return redirect(request.referrer)
    

@app.route("/drop",methods=["POST"])
@login_required
def drop():
        check_csrf()
        item_id=request.form["item_id"]
        message=player.drop_item(item_id,session["username"])
        flash(message)
        return redirect("/inventory")


@app.route("/marketplace")
@login_required
@cant_be_in_game
def use_marketplace():
    query=request.args.get("query")
    items=marketplace.get_listed_items(query)
    for item in items:
        print(item)
        for value in item:
            print(value)
    return render_template("marketplace.html",items=items)


@app.route("/sell",methods=["GET","POST"])
@login_required
@cant_be_in_game
def sell():
    if request.method=="GET":
        item_id=request.args.get("item_id")
        item=marketplace.check_item_owner(item_id,session["username"])
        #MAKE ANOTHER CHECK HERE
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
        #MAKE ANOTHER CHECK HERE
        if item:
            result=marketplace.put_item_for_sale(item_id,market_price)
            if result["rows_affected"]==1:
                flash(f"{item[0]['item_name']} has been listed to the marketplace")
            else:
                flash("Item no longer available")
                print(result["error"])
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

@app.route("/modify",methods=["GET","POST"])
@login_required
@cant_be_in_game
def modify():
    if request.method=="GET":
        item_id=request.args.get("item_id")
        username=session["username"]
        item=marketplace.check_item_owner(item_id,username)
        listing=marketplace.check_item_is_listed(item_id,username)
        if item and listing:
            print(listing[0]["marketplace_price"])
            return render_template("modify_listing.html",item_name=item[0]["item_name"],current_price=listing[0]["marketplace_price"],item_id=item[0]["id"])
        else:
            flash("Listing no longer available")
            return redirect("/marketplace")

    if request.method=="POST":
        check_csrf()
        item_id=request.form["item_id"]
        username=session["username"]
        new_price=request.form["new_price"]
        item=marketplace.check_item_owner(item_id,username)
        listing=marketplace.check_item_is_listed(item_id,username)
        if item and listing:
            marketplace.modify_listing(item_id,username,new_price)
            flash("Listing updated")
        else:
            flash("Listing no longer available")
        return redirect("/marketplace")
    

@app.route("/cancel_offer",methods=["POST"])
@login_required
@cant_be_in_game
def cancel_offer():
    check_csrf()
    offer_id=request.form["offer_id"]
    result=marketplace.cancel_offer(offer_id,session["username"])
    flash(result)
    return redirect("/my_offers")


@app.route("/offer_trade", methods=["POST","GET"])
@login_required
@cant_be_in_game
def trade():
    if request.method=="GET":
        item_id=request.args.get("item_id")
        item=marketplace.get_item_details(item_id)
        #ADD A CHECK HERE
        if item:
            offers=marketplace.get_offers_for_item(item_id)
            items=player.get_player_items(session["username"])
            return render_template("trade_offer.html",items=items,item=item[0],offers=offers)

    if request.method=="POST":
        check_csrf()
        items_to_offer=request.form.getlist("item_offer")
        item_id=request.form["item_id"]
        gold_offer=request.form["gold_offer"]
        try:
            gold_offer=int(gold_offer)
        except ValueError:
            gold_offer=0
        if gold_offer < 0:
            flash("Gold offer can't be negative")
            return redirect(request.referrer)
        result=marketplace.create_trade_offer(item_id,items_to_offer,session["username"],gold_offer)
        flash(result)
        return redirect(request.referrer)

@app.route("/my_offers")
@login_required
@cant_be_in_game
def my_offers():
    username=session["username"]
    my_offers=marketplace.get_my_offers(username)
    other_offers=marketplace.get_offers_for_me(username)
    return render_template("my_offers.html",my_offers=my_offers,other_offers=other_offers)

@app.route("/accept", methods=["POST"])
@login_required
@cant_be_in_game
def accept_trade_offer():
    check_csrf()
    buyer_id=request.form["buyer_id"]
    sold_item_id=request.form["sold_item_id"]
    offer_id=request.form["offer_id"]
    result=marketplace.accept_offer(offer_id,session["username"],buyer_id,sold_item_id)
    flash(result)
    return redirect("/my_offers")


@app.route("/new_world",methods=["POST"])
@login_required
@cant_be_in_game
def generate_new_world():
    check_csrf()
    if request.form["world_name"]:
        world.World(50,session["username"],request.form["world_name"]).generate_world()
        flash("New world generated!")
    else:
        flash("World needs a name!")
    return redirect("/")

@app.route("/delete",methods=["POST"])
@login_required
@cant_be_in_game
def delete_world():
    check_csrf()
    if request.form["world_id"]:
        result=player.delete_world(request.form["world_id"],session["username"])
        flash(result)

    return redirect("/")

@app.route("/use",methods=["POST"])
@login_required
def use_items():
    check_csrf()
    item_id=request.form["item_id"]
    result=player.use_item(item_id,session["username"])
    flash(result)
    return redirect("/inventory")

@app.route("/play", methods=["POST","GET"])
@login_required
def play():
    if request.method=="GET":
        
        if session.get("location"):
            print(session["location"])
            tile=game.tile_details(session["location"])
            return render_template("gameboard.html",connected=tile["connected"],npcs=tile["npcs"],containers=tile["containers"],tile_type=tile["tile_type"])
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



@app.route("/move",methods=["POST"])
@login_required
def move():
    check_csrf()
    target_tile=request.form["tile"]
    current_tile=session["location"]
    if game.move(target_tile,current_tile):
        result=game.update_location(current_tile,target_tile,session["username"])
        if result["rows_affected"]==1:
            session["location"]=target_tile
    return redirect("/play")


@app.route("/leave", methods=["POST"])
@login_required
def leave():
    check_csrf()
    result=game.update_location(session["location"],None,session["username"])
    if result["rows_affected"]==1:
        del session["location"]
    return redirect("/")

@app.route("/player/<username>",methods=["GET","POST"])
def player_page(username):
    info=player.get_player_info(username)
    items=player.get_player_items(username)
    worn_items=player.get_equipped_items(username)
    stats=player.get_total_stats(username)
    if info:
        return render_template("player_page.html",items=items,stats=stats,info=info,worn_items=worn_items)
    else:
        abort(404)


@app.route("/set_stats",methods=["POST"])
@login_required
@cant_be_in_game
def set_stats():
    #check_csrf()
    
    agility=int(request.form["agility"])
    strength=int(request.form["strength"])
    stamina=int(request.form["stamina"])
    magic=int(request.form["magic"])
    stats=(agility+strength+stamina+magic)
    print(stats)
    if stats>15:
        flash("Stats can't exceed total of 15")
        return redirect(request.referrer)
    result=player.set_stats(session["username"],agility,magic,stamina,strength,stats)
    flash(result)
    return redirect(request.referrer)
