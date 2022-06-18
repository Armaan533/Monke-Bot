from keep_alive import keep_alive
import os
import discord
from discord.ext import commands
import logical_definitions as lgd
import mongo_declaration as mn
from pathlib import Path


intent = discord.Intents.default()
intent.members = True
intent.messages = True

defaultPrefix = "+"

def get_prefix(client, message: discord.Message):
	Gprefix: str = mn.guildpref.find_one({"_id": str(message.guild.id)},{"_id": 0,"Prefix": 1})["Prefix"]
	return commands.when_mentioned_or(Gprefix)(client, message)

# Creating a bot instance
client = commands.Bot(command_prefix = get_prefix, intents = intent)

# Deleting inbuilt help command
client.remove_command('help')

#invite link for invite command
invlink = 'https://discord.com/api/oauth2/authorize?client_id=860161020681388093&permissions=8&scope=bot'


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
	activity = discord.Game(name="with servers", type=3)
	await client.change_presence(status=discord.Status.idle, activity=activity)
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

@client.command(aliases = ["Help","helpme","Helpme"])
async def help(ctx):
	helpEmbed = discord.Embed(title = "Commands",
							  color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1})))
	#	Add more commands here

	helpEmbed.add_field(name="`ping`", value="Shows the latency of the bot | Utility\n Aliases | pong", inline=True)
	helpEmbed.add_field(name="`purge`", value="Deletes a specified number of messages | Utility\n Aliases | None", inline=True)
	helpEmbed.add_field(name="`ban`", value="Bans a member  | Mod\n Aliases | None", inline=True)
	helpEmbed.add_field(name="`unban`", value="Unbans a member  | Mod\n Aliases | None", inline=True)
	helpEmbed.add_field(name="`say`", value="Make bot say something for you| Utility\n Aliases | None", inline=True)
	helpEmbed.add_field(name="`invite`", value="Gives an invite link of bot| Utility\n Aliases | invitebot", inline=True)
	helpEmbed.add_field(name="`nuke`", value="Deletes messages in bulk| Mod\n Aliases | None", inline=True)
	helpEmbed.add_field(name = "`prefix`", value = "Changes the prefix of bot to desired prefix| Utility\n Aliases | None")
	helpEmbed.set_footer(text=f"Requested by {ctx.author.name}", icon_url = ctx.author.avatar_url)

	await ctx.send(embed = helpEmbed)

@client.command(aliases = ["Prefix"])
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


@client.command()
async def enable(ctx, *, cogname = None):
	if cogname == None:
		return
	
	try:
		client.load_extension(cogname)
	except Exception as e:
		await ctx.send(f'Could not load cog {cogname}: {str(e)}')

	else:
		await ctx.send('Enabled Commands Successfully')

@client.command()
async def disable(ctx,*, cogname = None):
	if cogname == None:
		return
    
	try:
		client.unload_extension(cogname)
	except Exception as e:
		await ctx.send(f'Could not unload cog {cogname}: {str(e)}')

	else:
		await ctx.send('Disabled Commands Successfully')

# For checking bot latency

@client.command(aliases = ["Ping","pong","Pong"])
async def ping(ctx):
	pingem = discord.Embed(description = f"Pong! In {round(client.latency * 1000)}ms",
						   color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1})))
	await ctx.send(embed=pingem)

@client.command(aliases = ["Say"])
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


@client.command()
async def roleinfo(ctx, role: discord.Role):
	await ctx.send(role.id)
    
#	Deprecated Command
#	Not in use anymore

#@client.command()
#@commands.has_permissions(administrator=True)
#async def spam(ctx, num:int, *, text: str):
#  await ctx.message.delete()
#  for i in range(num):
#    await ctx.send(text)


@client.command(aliases = ["Invite","invitebot","Invitebot"])
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
	    # elif "★" in message.description:
	    #     await message.channel.send("it is working")
	

@client.command(aliases = ["Purge"])
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

@client.command(aliases = ["Nuke"])
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


@client.command(aliases = ["Kick"])
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
	

@client.command()
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



client.load_extension("cogs.channel")
client.load_extension("cogs.warn")
client.load_extension("cogs.serverinfo")
client.load_extension("cogs.userinfo")

if ".replit" in os.listdir():
	keep_alive()
	client.run(os.getenv('token'))
else:
	client.run(os.environ.get('token'))