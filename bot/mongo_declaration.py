import os, pymongo

dbase = pymongo.MongoClient("",serverSelectionTimeoutMs = 5000)

botdbase = dbase["Bot_Database"]
guildpref = botdbase["Guild Preference"]
colors = dbase["hex_colours"]
colorCollection = colors["colours"]