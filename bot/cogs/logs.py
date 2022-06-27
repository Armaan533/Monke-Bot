import discord, asyncio, datetime
import logical_definitions as lgd
import mongo_declaration as mn
from discord.ext import commands
from datetime import datetime

class Logs(commands.Cog):
	def __init__(self, client):
		self.client = client
			
	@commands.Cog.listener()
	async def on_member_join(self, member: discord.Member):
		if mn.guildpref.find_one({"_id": str(member.guild.id)},{"_id":0,"Logs":1})["Logs"] == False:
			pass
		else:
			createtime = member.created_at
			createtimestamp = datetime.timestamp(createtime)
			logChannel = discord.utils.get(member.guild.text_channels, id = int(mn.guildpref.find_one({"_id": str(member.guild.id)},{"_id":0,"Logs":1})["Logs"]))
			memberjoinLogEmbed = discord.Embed(
				title = "**Member Joined**",
				description = f"{member.mention} joined\n**Account Creation**\n <t:{int(createtimestamp//1)}:F>",
				timestamp = discord.utils.utcnow(),
				color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
			)
			memberjoinLogEmbed.set_footer(text = "\u200b")
			await logChannel.send(embed = memberjoinLogEmbed)

	@commands.Cog.listener()
	async def on_member_remove(self, member: discord.Member):
		if mn.guildpref.find_one({"_id":str(member.guild.id)},{"_id":0,"Logs":1})["Logs"] == False:
			pass
		else:
			Memberguild = discord.utils.get(self.client.guilds, id = member.guild.id)
			logChannel = discord.utils.get(Memberguild.text_channels,
										   id = int(mn.guildpref.find_one({"_id": str(member.guild_id)},{"_id":0,"Logs":1})["Logs"]))
			memberleaveLogEmbed = discord.Embed(
				title = "**Member Left**",
				description = f"{member.mention} left",
				timestamp = discord.utils.utcnow(),
				color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
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

			async for entry in Memberguild.audit_logs(limit = 1, action = discord.AuditLogAction.message_delete):
				sender = entry.target
				if sender == message.author:
					deleter = entry.user
				else:
					deleter = message.author

			msgchannel = discord.utils.get(Memberguild.text_channels, id = payload.channel_id)
			if message != None:
				cachemessagedeleteEmbed = discord.Embed(
					title = f"Message Deleted By {deleter.name}#{deleter.discriminator}",
					description = "",
					timestamp = discord.utils.utcnow(),
					color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
				)
				cachemessagedeleteEmbed.set_footer(text = f"ID:{message.id}")

				cachemessagedeleteEmbed.add_field(
					name = "Message Sender",
					value = f"{message.author.mention}",
					inline = True
				)

				cachemessagedeleteEmbed.add_field(
					name = "Message Deleter",
					value = f"{deleter.mention}",
					inline = True
				)

				cachemessagedeleteEmbed.add_field(
					name = "Channel",
					value = msgchannel.mention,
					inline = False
				)
				if message.content != "":
					cachemessagedeleteEmbed.add_field(
						name = "Message Content",
						value = f"```{message.clean_content}```",
						inline = False
					)

				await logchannel.send(embed = cachemessagedeleteEmbed)
			else:
				noCacheMessageDeleteEmbed = discord.Embed(
					title = "Message Deleted",
					description = f"Message Content not available\nChannel: {msgchannel.mention}",
					timestamp = discord.utils.utcnow(),
					color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0, "Hex": 1}))
				)
				noCacheMessageDeleteEmbed.set_footer(text = f"ID: {payload.message_id}")

				await logchannel.send(embed = noCacheMessageDeleteEmbed)

	# @commands.Cog.listener()
	# async def on_raw_bulk_message_delete(self, payload: discord.RawBulkMessageDeleteEvent):
	# 	if mn.guildpref.find_one({"_id":str(payload.guild_id)},{"_id":0,"Logs":1})["Logs"] == False:
	# 		pass
	# 	else:
	# 		Memberguild = self.client.get_guild(payload.guild_id)
	# 		logchannel = discord.utils.get(Memberguild.text_channels, id = int(mn.guildpref.find_one({"_id": str(payload.guild_id)},{"_id":0,"Logs":1})["Logs"]))

	# 		async for entry in Memberguild.audit_logs(limit = 1, action = discord.AuditLogAction.message_bulk_delete):
	# 			deleter = entry.user

			
			

async def setup(client):
	await client.add_cog(Logs(client))