import discord
from discord.ext import commands

class Events(commands.Cog):

    def __init__(self, client):

        self.client = client

    @commands.Cog.listener()
    async def on_member_join(self, member):
        
        await self.client.get_channel(861569491393445928).send(member)

    @commands.command()
    async def lol(self, ctx):
        await ctx.send(":lmao:")


def setup(client):
    client.add_cog(Events(client))