import discord, asyncio, datetime
import logical_definitions as lgd
import mongo_declaration as mn
from discord.ext import commands

class Logs(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command()
	async def setlogChannel(self, ctx):
		logChannelEmbed = discord.Embed(description = "Mention the channel",
										   color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1})))
		logMessage = await ctx.send(embed = logChannelEmbed)
		try:
			authorcheck = lambda m: m.author == ctx.author and m.channel == ctx.channel
			name = await self.client.wait_for("message", check = authorcheck, timeout = 30)
		except asyncio.exceptions.TimeoutError:
			await logMessage.edit(embed = discord.Embed(description = "timed out",
														color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))),
								  delete_after = 10)
			return
		await name.delete()
		mn.guildpref.update_one({"_id":str(ctx.guild.id)},{"$set":{"Logs":name.content.lstrip("<#").rstrip(">")}})
		await logMessage.edit(embed = discord.Embed(
			description = "Log channel added successfully",
			color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
		))
			
	@commands.Cog.listener()
	async def on_member_join(self, member: discord.Member):
		if mn.guildpref.find_one({"_id": str(member.guild.id)},{"_id":0,"Logs":1})["Logs"] == False:
			pass
		else:
			time = member.created_at.utcnow()
			logChannel = discord.utils.get(member.guild.text_channels, id = int(mn.guildpref.find_one({"_id": str(member.guild.id)},{"_id":0,"Logs":1})["Logs"]))
			memberjoinLogEmbed = discord.Embed(
				title = "**Member Joined**",
				description = f"{member.mention} joined\n**Account Creation**\n{time}",
				timestamp=datetime.datetime.utcnow()
			)
			memberjoinLogEmbed.set_footer(text = '\u200b')
			await logChannel.send(embed = memberjoinLogEmbed)

	@commands.Cog.listener()
	async def on_raw_member_leave(self, payload):
		if mn.guildpref.find_one({"_id":str(payload.guild_id)},{"_id":0,"Logs":1})["Logs"] == False:
			pass
		else:
			Memberguild = self.client.get_guild(payload.guild_id)
			logChannel = discord.utils.get(Memberguild.text_channels,
										   id = int(mn.guildpref.find_one({"_id": str(payload.guild_id)},{"_id":0,"Logs":1})["Logs"]))
			memberleaveLogEmbed = discord.Embed(
				title = "**Member Left**",
				description = f"{payload.user.mention} left",
				timestamp = datetime.datetime.utcnow()
			)
			memberleaveLogEmbed.set_footer(text = "\u200b")
			await logChannel.send(embed = memberleaveLogEmbed)

	# @commands.Cog.listener()
	# async def on

def setup(client):
	client.add_cog(Logs(client))