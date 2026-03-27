CREATE TABLE users (
id INTEGER PRIMARY KEY,
username TEXT UNIQUE,
password_hash TEXT);


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
listed_for_sale BOOLEAN,
marketplace_price INTEGER,
FOREIGN KEY (item_owner) REFERENCES npcs(id),
FOREIGN KEY (player) REFERENCES users(id),
FOREIGN KEY (container) REFERENCES containers(id)
);

CREATE TABLE tiles (
x_coordinate INTEGER,
y_coordinate INTEGER,
tile_type TEXT,
PRIMARY KEY (x_coordinate,y_coordinate)
);



INSERT INTO tiles (x_coordinate,y_coordinate,tile_type) VALUES (0,0,"swamp");
INSERT INTO containers (container_type,x_coordinate,y_coordinate) VALUES ("barrel",0,0);
INSERT INTO npcs (npc_name,x_coordinate,y_coordinate) VALUES ("Ann",0,0);
INSERT INTO items (item_name,item_owner,player,container) VALUES ("Ann's dagger",1,NULL,NULL);
INSERT INTO items (item_name,item_owner,player,container) VALUES ("Rusty sword",NULL,NULL,1);
INSERT INTO items (item_name,item_owner,player,container) VALUES ("Super sword",NULL,1,NULL);
INSERT INTO items (item_name,item_owner,player,container,price,listed_for_sale,marketplace_price) VALUES ("Super sword",NULL,1,NULL,200,TRUE,400);