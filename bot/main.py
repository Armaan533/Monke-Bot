import asyncio
import os
import discord
from discord import app_commands
from discord.ext import commands
import logical_definitions as lgd
import mongo_declaration as mn
import sys


intent = discord.Intents.default()
intent.members = True
intent.message_content = True

#invite link for invite command

invlink = 'https://discord.com/api/oauth2/authorize?client_id=860161020681388093&permissions=8&scope=bot'

defaultPrefix = "+"


def get_prefix(client, message: discord.Message):
	Gprefix: str = mn.guildpref.find_one({"_id": str(message.guild.id)},{"_id": 0,"Prefix": 1})["Prefix"]
	return commands.when_mentioned_or(Gprefix)(client, message)


class MyHelp(commands.HelpCommand):
	def get_command_signature(self, command):
			return '%s%s %s' % (self.clean_prefix, command.qualified_name, command.signature)

	async def send_bot_help(self, mapping):

		helpEmbed = discord.Embed(title = "Commands",
							  color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1})))

	#	Add more commands here

		# helpEmbed.add_field(name="`ping`", value="Shows the latency of the bot | Utility\n Aliases | pong", inline=True)
		# helpEmbed.add_field(name="`purge`", value="Deletes a specified number of messages | Utility\n Aliases | None", inline=True)
		# helpEmbed.add_field(name="`ban`", value="Bans a member  | Mod\n Aliases | None", inline=True)
		# helpEmbed.add_field(name="`unban`", value="Unbans a member  | Mod\n Aliases | None", inline=True)
		# helpEmbed.add_field(name="`say`", value="Make bot say something for you| Utility\n Aliases | None", inline=True)
		# helpEmbed.add_field(name="`invite`", value="Gives an invite link of bot| Utility\n Aliases | invitebot", inline=True)
		# helpEmbed.add_field(name="`nuke`", value="Deletes messages in bulk| Mod\n Aliases | None", inline=True)
		# helpEmbed.add_field(name = "`prefix`", value = "Changes the prefix of bot to desired prefix| Utility\n Aliases | None")
		helpEmbed.set_footer(text=f"Requested by {self.context.author.name} | Use {self.clean_prefix}help <command> to get more info about the command", icon_url = self.context.author.avatar_url)

		for cog, commands in mapping.items():
			filtered = await self.filter_commands(commands, sort=True)
			command_signatures = [self.get_command_signature(c) for c in filtered]
			if command_signatures:
				cog_name = getattr(cog, "qualified_name", "No Category")
				helpEmbed.add_field(name=cog_name, value="\n".join(command_signatures), inline=False)
		
		print("stuff works")
		await self.context.reply(embed = helpEmbed)

	async def send_command_help(self, command):
		helpCommandEmbed = discord.Embed(
			title = "Command Help",
			color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
		)
		helpCommandEmbed.add_field(name="Help", value=command.help)
		alias = command.aliases
		if alias:
			helpCommandEmbed.add_field(name="Aliases", value=", ".join(alias), inline=False)
		
		await self.context.reply(embed = helpCommandEmbed)


class MyClient(commands.Bot):
	def __init__(self) -> None:
		super().__init__(
			command_prefix = get_prefix, 
			intents = intent, 
			activity = discord.Game(name="with servers", type=3), 
			status = discord.Status.idle,
			case_insensitive = True,
			help_command = MyHelp()
		)

	async def setup_hook(self) -> None:
		await self.load_extension("cogs.channel")
		await self.load_extension("cogs.logs")
		await self.load_extension("cogs.serverinfo")
		await self.load_extension("cogs.userinfo")
		await self.load_extension("cogs.warn")


# Creating a bot instance
client = MyClient()

# this will get called when bot joins a guild

@client.event
async def on_guild_join(guild):
	guildDetails = {"_id": str(guild.id), "Prefix": "+", "Logs": False}
	mn.guildpref.insert_one(guildDetails)

@client.event
async def on_guild_remove(guild):
	mn.guildpref.delete_one({"_id": str(guild.id)})

#this will get called when bot is online
@client.event
async def on_ready():
	print("We are online!")

@client.event
async def on_member_join(member):
	if member.guild.id == 965285949447753769:
		role = discord.utils.get(member.guild.roles, name = "Soul Reapers")
		WelcomeEmbed = discord.Embed(description = f"Hey {member.mention},\nWelcome to Paradise!!\nWe hope you have a great stay in our server",
									color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1})))
		channel = discord.utils.get(member.guild.text_channels,id = 967822342459904051)
		ping = await channel.send(member.mention)
		await ping.delete()
		await channel.send(embed = WelcomeEmbed)
		await member.add_roles(role)

# new, upgraded and personalized help command



@client.command(help = "Changes the prefix of the bot for this guild")
@commands.guild_only()
@commands.has_guild_permissions(administrator = True)
async def prefix(ctx, newPrefix: str):
	if len(newPrefix) >= 5:
		await ctx.send(embed = discord.embed(title = "Prefix too long.",
											 description = "Please choose a shorter prefix!\nMaximum length of Prefix is 5 characters.",
											 color = lgd.hexConvertor(iterator = mn.colorCollection.find({},{"_id":0,"Hex":1}))))
	else:
		prev = {"_id":str(ctx.guild.id)} 
		next = {"$set":{"Prefix": newPrefix}}
		mn.guildpref.update_one(prev, next)
		prefixSuccess = discord.Embed(title = "Prefix changed!",
									  description = f"Prefix changed successfully to ``{newPrefix}``",
									  color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1})))
		await ctx.send(embed = prefixSuccess)

@prefix.error
async def prefix_error(ctx: commands.Context, error: commands.errors):
	if isinstance(error, commands.MissingPermissions):
		missingPermsEmbed = discord.Embed(
			title = "Hold Up!",
			description = "You need ``Administrator`` Permissions to use this command!",
			color = lgd.hexConvertor(iterator = mn.colorCollection.find({},{"_id":0,"Hex":1}))
		)
		await ctx.send(embed = missingPermsEmbed , delete_after = 20)
	elif isinstance(error, commands.MissingRequiredArgument):
		missingArgEmbed = discord.Embed(
			title = "Prefix needed",
			description = "You need to give prefix with command\n For example:- ``+prefix {newprefix}\n Put the new prefix in place of {newprefix}``",
			color = lgd.hexConvertor(iterator = mn.colorCollection.find({},{"_id":0,"Hex":1}))
		)
		await ctx.send(embed = missingArgEmbed)

@commands.is_owner()
@client.command(help = "For enabling cogs")
async def enable(ctx, *, cogname = None):
	if cogname == None:
		return
	
	try:
		await client.load_extension(cogname)
	except Exception as e:
		await ctx.send(f'Could not load cog {cogname}: {str(e)}')

	else:
		await ctx.send('Enabled Commands Successfully')

@commands.is_owner()
@client.command(help = "For disabling cogs")
async def disable(ctx,*, cogname = None):
	if cogname == None:
		return
    
	try:
		await client.unload_extension(cogname)
	except Exception as e:
		await ctx.send(f'Could not unload cog {cogname}: {str(e)}')

	else:
		await ctx.send('Disabled Commands Successfully')

# For checking bot latency

@client.command(help = "For checking the latensy of bot", aliases = ["pong"])
async def ping(ctx):
	pingem = discord.Embed(description = f"Pong! In {round(client.latency * 1000)}ms",
						   color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1})))
	await ctx.send(embed=pingem)

@client.command(help = "Fun command used for impersonating as bot. :warning: Warning :warning: Do NOT use this for bad stuff")
async def say(ctx, *, message = None):

	if message == None:
		e1 = discord.Embed(description = 'Please provide a message!',
						   color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1})))
		await ctx.send(embed=e1)
		return

# to prevent misuse of say command
	elif "@everyone" in message:
		if lgd.permscheck(ctx):
			me2 = discord.Embed(description = f"{message}",
								color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1})))
			await ctx.message.delete()
			await ctx.send(embed = me2)
		else:
			await ctx.send("Sorry you can't send the above message because you don't have administrator permission")

	else:
		me2 = discord.Embed(description = f"{message}",
							color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1})))
		await ctx.message.delete()
		await ctx.send(embed = me2)


@client.command(help = "For getting the link to invite the bot to your own server", aliases = ["invitebot"])
async def invite(ctx):
	inviteEmbed = discord.Embed(title = "Invite bot!",
								description = f"Click [here]({invlink}) to invite the bot",
								color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1})))
	await ctx.send(embed = inviteEmbed)



@client.listen("on_message")
async def on_message(message):
	if message.guild != None:
		guild = str(message.guild.id)
		gprefix = mn.guildpref.find_one({"_id": guild}, {"_id":0, "Prefix":1})["Prefix"]

		if (message.content == f"<@!{client.user.id}>" or message.content==f"<@{client.user.id}>") and message.author != message.guild.me:
	    
			mentionEmbed = discord.Embed(title = "Hello there :wave:",
										 description = f"My prefix is `{gprefix}`",
										 color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1})))
			await message.channel.send(embed = mentionEmbed)
	

@client.command(help = "For deleting the mentioned amount of messages")
@commands.has_guild_permissions(manage_messages = True)
async def purge(ctx, limit: int):
	await ctx.message.delete()
	await ctx.channel.purge(limit=limit)

@purge.error
async def purge_error(ctx, error):
	if isinstance(error, commands.MissingPermissions):
		missingpermEmbed = discord.Embed(title = "No permission",
										description = "You can't purge because you don't have manage messages permission",
										color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1})))
		await ctx.send(embed = missingpermEmbed)

@client.command(help = "For deleting large amount of messages in a channel")
@commands.has_guild_permissions(administrator = True)
async def nuke(ctx):
	await ctx.message.delete()
	limit = 10000
	await ctx.channel.purge(limit = limit)
    
@nuke.error
async def nuke_error(ctx, error):
	if isinstance(error, commands.MissingPermissions):
		NukeErrorEmbed = discord.Embed(title = "No Permission to do that",
									   description = "You can't nuke this channel because you don't have required permissions",
									   color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1})))
		await ctx.send(embed = NukeErrorEmbed)


@client.command(help = "For kicking members out of the server")
@commands.has_guild_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *kickReasonList):
	if member.id == 823894464798916688:
		devBanEmbed = discord.Embed(
			title = "Denied :octagonal_sign:",
			description = "You can't kick developer of this bot",
			color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
		)
		await ctx.reply(embed = devBanEmbed)
	else:
		if len(kickReasonList) != 0:
			kickReason = ""
			for i in kickReasonList:
				kickReason = kickReason + i + " "
		else:
			kickReason = None

		await member.kick(reason =  kickReason)
		if kickReason != None:
			SuccessKickEmbed = discord.Embed(title="Successful",
											description=f"Successfully kicked {member.name} for {kickReason}",
											color=lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1})))
		else:
			SuccessKickEmbed = discord.Embed(title="Successful",
											description=f"Successfully kicked {member.name}",
											color=lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1})))
		await ctx.send(embed = SuccessKickEmbed)

@kick.error
async def kick_error(ctx, error):
	if isinstance(error, commands.MissingPermissions):
		text = "Sorry {}, you do not have permissions to do that!".format(ctx.message.author)
		await ctx.send(text)
	

@client.command(help = "For banning members")
@commands.has_guild_permissions(ban_members = True)
async def ban(ctx, member: discord.Member, *banReasonList):

	if member.id == 823894464798916688:
		devBanEmbed = discord.Embed(
			title = "Denied :octagonal_sign:",
			description = "You can't ban developer of this bot",
			color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
		)
		await ctx.reply(embed = devBanEmbed)
	else:
		if len(banReasonList) != 0:
			banReason = ""
			for i in banReasonList:
				banReason = banReason + i + " "
		else:
			banReason = None
		
		await member.ban(reason = banReason)
		if banReason != None:	
			SuccessBanEmbed = discord.Embed(
				title="Successful",
				description=f"Successfully banned {member.name} for {banReason}",
				color=lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1})))
		else:
			SuccessBanEmbed = discord.Embed(title="Successful",
											description=f"Successfully banned {member.name}",
											color=lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1})))
		await ctx.send(embed = SuccessBanEmbed)

@ban.error
async def ban_error(ctx, error):
	if isinstance(error, commands.MissingPermissions):
		MissingPermsEmbed = discord.Embed(
			title = "Error",
			description = "What are you trying to do?\nYou can't ban that sucker because you don't have permissions to do that!",
			color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1})))
		await ctx.send(embed = MissingPermsEmbed)
	elif isinstance(error, commands.UserNotFound):
		banUserNotFoundEmbed = discord.Embed(title = "User not found",
											description = "try checking the id and discriminant of user again",
											color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1})))
		await ctx.send(embed = banUserNotFoundEmbed)


async def start():
	await client.start(os.environ.get('token'))
	

asyncio.run(start())