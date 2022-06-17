import discord, asyncio, datetime
import logical_definitions as lgd
import mongo_declaration as mn
from discord.ext import commands
from datetime import datetime

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
			createtime = member.created_at()
			createtimestamp = datetime.timestamp(createtime)
			logChannel = discord.utils.get(member.guild.text_channels, id = int(mn.guildpref.find_one({"_id": str(member.guild.id)},{"_id":0,"Logs":1})["Logs"]))
			memberjoinLogEmbed = discord.Embed(
				title = "**Member Joined**",
				description = f"{member.mention} joined\n**Account Creation**\n<t:{createtimestamp}:F>",
				timestamp = datetime.utcnow()
			)
			memberjoinLogEmbed.set_footer(text = "\u200b")
			await logChannel.send(embed = memberjoinLogEmbed)

	@commands.Cog.listener()
	async def on_member_remove(self, member: discord.Member):
		if mn.guildpref.find_one({"_id":str(member.guild_id)},{"_id":0,"Logs":1})["Logs"] == False:
			pass
		else:
			Memberguild = discord.utils.get(self.client.guilds, id = member.guild.id)
			logChannel = discord.utils.get(Memberguild.text_channels,
										   id = int(mn.guildpref.find_one({"_id": str(member.guild_id)},{"_id":0,"Logs":1})["Logs"]))
			memberleaveLogEmbed = discord.Embed(
				title = "**Member Left**",
				description = f"{member.mention} left",
				timestamp = datetime.utcnow()
			)
			memberleaveLogEmbed.set_footer(text = "\u200b")
			memberleaveLogEmbed.set_thumbnail(url = member.avatar_url)
			await logChannel.send(embed = memberleaveLogEmbed)

	@commands.Cog.listener()
	async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
		if mn.guildpref.find_one({"_id":str(payload.guild_id)},{"_id":0,"Logs":1})["Logs"] == False:
			pass
		else:
			Memberguild = self.client.get_guild(payload.guild_id)
			logchannel = discord.utils.get(Memberguild.text_channels, id = int(mn.guildpref.find_one({"_id": str(payload.guild_id)},{"_id":0,"Logs":1})["Logs"]))
			message = payload.cached_message
			if message != None:
				author = message.author
				cachemessagedeleteEmbed = discord.Embed(
					title = f"Message Deleted By {author.name}#{author.discriminator}",
					description = f"Message Contents: ``{message.content}``",
					timestamp = datetime.utcnow(),
					color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
				)
				cachemessagedeleteEmbed.set_footer(text = "\u200b")
				await logchannel.send(embed = cachemessagedeleteEmbed)
			else:
				noCacheMessageDeleteEmbed = discord.Embed(
					title = f"Message Deleted in <#{payload.channel_id}",
					description = "Message Content not available",
					timestamp = datetime.utcnow(),
					color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0, "Hex": 1}))
				)

def setup(client):
	client.add_cog(Logs(client))