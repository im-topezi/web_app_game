DELETE FROM equipped_items;
UPDATE items SET container=NULL,npc=NULL,player=1;
UPDATE users SET gold=1000;
