import discord
from discord.ext import commands
import mongo_declaration as mn
import logical_definitions as lgd

class Channel(commands.Cog):

	def __init__(self, client):

		self.client = client

	@commands.command()
	async def lock(self, ctx):
		everyoneRole = discord.utils.get(ctx.guild.roles, name = "@everyone")
		await ctx.channel.set_permissions(everyoneRole, read_messages=True, send_messages=False)
		await ctx.send(embed = discord.Embed(description = "Channel locked successfully",
											color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))))

	@commands.command()
	async def unlock(self, ctx):
		everyoneRole = discord.utils.get(ctx.guild.roles, name = "@everyone")
		await ctx.channel.set_permissions(everyoneRole, send_messages = True)
		await ctx.send(embed = discord.Embed(description = "Channel unlocked successfully",
											color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))))

def setup(client):
    client.add_cog(Channel(client))