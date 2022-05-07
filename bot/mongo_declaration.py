import os, pymongo

dbase = pymongo.MongoClient(os.getenv('pymongo_link'),serverSelectionTimeoutMs = 5000)

botdbase = dbase["Bot_Database"]
guildpref = botdbase["Guild Preference"]
colors = dbase["hex_colours"]
colorCollection = colors["colours"]