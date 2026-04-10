CREATE TABLE users (
id INTEGER PRIMARY KEY,
username TEXT UNIQUE,
password_hash TEXT,
gold INTEGER DEFAULT 0 NOT NULL,
CHECK (gold >= 0));


CREATE TABLE worlds (
id TEXT PRIMARY KEY,
player INTEGER,
difficulty INTEGER,
world_name TEXT,
visited BOOLEAN DEFAULT FALSE,
FOREIGN KEY (player) REFERENCES users(id)
);

CREATE TABLE tile_types(
type_name TEXT PRIMARY KEY,
difficulty INTEGER
);


CREATE TABLE tiles (
id INTEGER PRIMARY KEY,
world_id TEXT,
x_coordinate INTEGER,
y_coordinate INTEGER,
tile_type TEXT,
FOREIGN KEY (world_id) REFERENCES worlds(id),
FOREIGN KEY (tile_type) REFERENCES tile_types(type_name)
UNIQUE (world_id,x_coordinate,y_coordinate)
);


CREATE TABLE paths (
id INTEGER PRIMARY KEY,
first_tile INTEGER,
second_tile INTEGER,
FOREIGN KEY (first_tile) REFERENCES tiles(id),
FOREIGN KEY (second_tile) REFERENCES tiles(id)
);


CREATE TABLE npcs (
id INTEGER PRIMARY KEY,
npc_name TEXT,
tile INTEGER,
FOREIGN KEY (tile) REFERENCES tiles(id)
);



CREATE TABLE containers (
id INTEGER PRIMARY KEY,
container_type TEXT,
tile INTEGER,
FOREIGN KEY (tile) REFERENCES tiles(id)
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

CREATE TABLE location (
player INTEGER UNIQUE NOT NULL,
tile INTEGER,
FOREIGN KEY (player) REFERENCES users(id),
FOREIGN KEY (tile) REFERENCES tiles(id)
);

CREATE TABLE stat_sheet (
id INTEGER PRIMARY KEY,
stamina INTEGER,
strength INTEGER,
agility INTEGER,
magic INTEGER,
player_id INTEGER UNIQUE,
npc_id INTEGER UNIQUE,
item_id INTEGER UNIQUE,
FOREIGN KEY (player_id) REFERENCES users(id),
FOREIGN KEY (npc_id) REFERENCES npcs(id),
FOREIGN KEY (item_id) REFERENCES items(id),
CHECK (
    player_id IS NULL
    OR player_id IS NOT NULL AND (npc_id IS NULL AND item_id IS NULL)
),
CHECK (
    npc_id IS NULL
    OR npc_id IS NOT NULL AND (player_id IS NULL AND item_id IS NULL)
),
CHECK (
    item_id IS NULL
    OR item_id IS NOT NULL AND (player_id IS NULL AND npc_id IS NULL)
)
);






INSERT INTO containers (container_type,x_coordinate,y_coordinate) VALUES ("barrel",0,0);
INSERT INTO npcs (npc_name,x_coordinate,y_coordinate) VALUES ("Test NPC",0,0);
INSERT INTO items (item_name,item_owner,player,container) VALUES ("Ann's dagger",1,NULL,NULL);
INSERT INTO items (item_name,item_owner,player,container) VALUES ("Rusty sword",NULL,NULL,(SELECT containers.id FROM containers WHERE container_type="barrel"));
INSERT INTO items (item_name,item_owner,player,container) VALUES ("Super sword",NULL,NULL,(SELECT containers.id FROM containers WHERE container_type="barrel"));


INSERT INTO tile_types(type_name,difficulty) VALUES ("City",0);
INSERT INTO tile_types(type_name,difficulty) VALUES ("Swamp",20);
INSERT INTO tile_types(type_name,difficulty) VALUES ("Dungeon",16);
INSERT INTO tile_types(type_name,difficulty) VALUES ("Forest",5);
INSERT INTO tile_types(type_name,difficulty) VALUES ("Village",0);
INSERT INTO tile_types(type_name,difficulty) VALUES ("Mountain",25);