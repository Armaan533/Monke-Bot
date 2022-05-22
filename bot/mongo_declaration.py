import os, pymongo
from pathlib import Path

current = Path(os.getcwd())
parentFiles = os.listdir(current.parent)

if ".replit" in parentFiles:
    dbase = pymongo.MongoClient(os.getenv('mongo_db_link'),serverSelectionTimeoutMs = 5000)
else:
    dbase = None

botdbase = dbase["Bot_Database"]
guildpref = botdbase["Guild Preference"]
colors = dbase["hex_colours"]
colorCollection = colors["colours"]