CREATE TABLE users (
id INTEGER PRIMARY KEY,
username TEXT UNIQUE,
password_hash TEXT,
gold INTEGER DEFAULT 0 NOT NULL,
CHECK (gold >= 0));


CREATE TABLE tiles (
x_coordinate INTEGER,
y_coordinate INTEGER,
tile_type TEXT,
PRIMARY KEY (x_coordinate,y_coordinate)
);


CREATE TABLE npcs (
id INTEGER PRIMARY KEY,
npc_name TEXT,
x_coordinate INTEGER,
y_coordinate INTEGER,
FOREIGN KEY (x_coordinate) REFERENCES tiles(x_coordinate),
FOREIGN KEY (y_coordinate) REFERENCES tiles(y_coordinate)
);



CREATE TABLE containers (
id INTEGER PRIMARY KEY,
container_type TEXT,
x_coordinate INTEGER,
y_coordinate INTEGER,
FOREIGN KEY (x_coordinate) REFERENCES tiles(x_coordinate),
FOREIGN KEY (y_coordinate) REFERENCES tiles(y_coordinate)
);

CREATE TABLE items (
id INTEGER PRIMARY KEY,
item_name TEXT,
item_owner INTEGER,
player INTEGER,
container INTEGER,
price INTEGER,
listed_for_sale BOOLEAN DEFAULT FALSE,
marketplace_price INTEGER,
FOREIGN KEY (item_owner) REFERENCES npcs(id),
FOREIGN KEY (player) REFERENCES users(id),
FOREIGN KEY (container) REFERENCES containers(id)
);

"""CREATE TABLE transactions (
    id INTEGER PRIMARY KEY,
    item_id INTEGER,
    buyer_id INTEGER,
    seller_id INTEGER,
    transaction_state TEXT,
    time
)"""





INSERT INTO tiles (x_coordinate,y_coordinate,tile_type) VALUES (0,0,"swamp");
INSERT INTO containers (container_type,x_coordinate,y_coordinate) VALUES ("barrel",0,0);
INSERT INTO npcs (npc_name,x_coordinate,y_coordinate) VALUES ("Test NPC",0,0);
INSERT INTO items (item_name,item_owner,player,container) VALUES ("Ann's dagger",1,NULL,NULL);
INSERT INTO items (item_name,item_owner,player,container) VALUES ("Rusty sword",NULL,NULL,(SELECT containers.id FROM containers WHERE container_type="barrel"));
INSERT INTO items (item_name,item_owner,player,container) VALUES ("Super sword",NULL,NULL,(SELECT containers.id FROM containers WHERE container_type="barrel"));
