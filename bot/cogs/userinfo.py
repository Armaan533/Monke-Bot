from discord.ext import commands
import discord
import mongo_declaration as mn
import logical_definitions as lgd

def setup(client):
    client.add_cog(Userinfo(client))

class Userinfo(commands.Cog):
    
    def __init__(self, client):
        self.client = client

    @commands.command(aliases = ["Userinfo","Memberinfo"])
    async def userinfo(self, ctx: commands.Context, member):
        await ctx.send(type(member))