import os, pymongo

current = os.getcwd()
currentFiles = os.listdir(current)
if ".replit" in currentFiles:
    dbase = pymongo.MongoClient(os.getenv('mongo_db_link'),serverSelectionTimeoutMs = 5000)

botdbase = dbase["Bot_Database"]
guildpref = botdbase["Guild Preference"]
colors = dbase["hex_colours"]
colorCollection = colors["colours"]