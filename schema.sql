CREATE TABLE users (
id INTEGER PRIMARY KEY,
username TEXT UNIQUE,
password_hash TEXT,
set_stats BOOLEAN DEFAULT FALSE,
gold INTEGER DEFAULT 0 NOT NULL,
CHECK (gold >= 0));


CREATE TABLE worlds (
id TEXT UNIQUE,
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
npc INTEGER,
player INTEGER,
container INTEGER,
trader_price INTEGER,
FOREIGN KEY (npc) REFERENCES npcs(id),
FOREIGN KEY (player) REFERENCES users(id),
FOREIGN KEY (container) REFERENCES containers(id)
CHECK (
    player IS NULL
    OR player IS NOT NULL AND (npc IS NULL AND container IS NULL)
),
CHECK (
    npc IS NULL
    OR npc IS NOT NULL AND (player IS NULL AND container IS NULL)
),
CHECK (
    container IS NULL
    OR container IS NOT NULL AND (player IS NULL AND npc IS NULL)
)
);


CREATE TABLE trade_offers (
id INTEGER PRIMARY KEY,
sold_item INTEGER NOT NULL,
buyer_id INTEGER NOT NULL,
gold_offer INTEGER,
FOREIGN KEY (sold_item) REFERENCES items(id),
FOREIGN KEY (buyer_id) REFERENCES users(id)
);

CREATE TABLE offered_items (
id INTEGER PRIMARY KEY,
offer_id INTEGER NOT NULL,
item_id INTEGER NOT NULL,
FOREIGN KEY (item_id) REFERENCES items(id),
FOREIGN KEY (offer_id) REFERENCES trade_offers(id)
);

CREATE TABLE marketplace_listings (
id INTEGER PRIMARY KEY,
item_id INTEGER NOT NULL,
seller_id INTEGER NOT NULL,
marketplace_price INTEGER,
FOREIGN KEY (item_id) REFERENCES items(id),
FOREIGN KEY (seller_id) REFERENCES users(id)
);


CREATE TABLE location (
player INTEGER UNIQUE NOT NULL,
tile INTEGER,
FOREIGN KEY (player) REFERENCES users(id),
FOREIGN KEY (tile) REFERENCES tiles(id)
);

CREATE TABLE stat_sheet (
id INTEGER PRIMARY KEY,
stamina INTEGER DEFAULT 0,
strength INTEGER DEFAULT 0,
agility INTEGER DEFAULT 0,
magic INTEGER DEFAULT 0,
player_id INTEGER UNIQUE,
npc_id INTEGER UNIQUE,
item_id INTEGER UNIQUE,
FOREIGN KEY (player_id) REFERENCES users(id),
FOREIGN KEY (npc_id) REFERENCES npcs(id),
FOREIGN KEY (item_id) REFERENCES items(id),

CHECK (
    player_id IS NULL
    OR player_id IS NOT NULL AND (npc_id IS NULL AND item_id IS NULL) AND ((stamina+strength+agility+magic)<16)
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







INSERT INTO items (item_name,player,container) VALUES ("Rusty sword",NULL,(SELECT containers.id FROM containers WHERE container_type="barrel"));
INSERT INTO items (item_name,player,container) VALUES ("Super sword",NULL,(SELECT containers.id FROM containers WHERE container_type="barrel"));


INSERT INTO tile_types(type_name,difficulty) VALUES ("City",0);
INSERT INTO tile_types(type_name,difficulty) VALUES ("Swamp",20);
INSERT INTO tile_types(type_name,difficulty) VALUES ("Dungeon",16);
INSERT INTO tile_types(type_name,difficulty) VALUES ("Forest",5);
INSERT INTO tile_types(type_name,difficulty) VALUES ("Village",0);
INSERT INTO tile_types(type_name,difficulty) VALUES ("Mountain",25);