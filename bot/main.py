import asyncio
import os
import discord
from discord import app_commands, ui
from discord.ext import commands, menus
import logical_definitions as lgd
import mongo_declaration as mn
import sys, traceback
from itertools import starmap


intent = discord.Intents.default()
intent.members = True
intent.message_content = True

#invite link for invite command

invlink = 'https://discord.com/api/oauth2/authorize?client_id=860161020681388093&permissions=8&scope=bot'

defaultPrefix = "+"


def get_prefix(client, message: discord.Message):
	Gprefix: str = mn.guildpref.find_one({"_id": str(message.guild.id)},{"_id": 0,"Prefix": 1})["Prefix"]
	return commands.when_mentioned_or(Gprefix)(client, message)
























class MyMenuPages(ui.View, menus.MenuPages):
	def __init__(self, source, *, delete_message_after=False):
		super().__init__(timeout=60)
		self._source = source
		self.current_page = 0
		self.ctx = None
		self.message = None
		self.delete_message_after = delete_message_after

	async def start(self, ctx, *, channel=None, wait=False):
        # We wont be using wait/channel, you can implement them yourself. This is to match the MenuPages signature.
		await self._source._prepare_once()
		self.ctx = ctx
		self.message = await self.send_initial_message(ctx, ctx.channel)

	async def _get_kwargs_from_page(self, page):
		"""This method calls ListPageSource.format_page class"""
		value = await super()._get_kwargs_from_page(page)
		if 'view' not in value:
			value.update({'view': self})
		return value

	async def interaction_check(self, interaction):
		"""Only allow the author that invoke the command to be able to use the interaction"""
		return interaction.user == self.ctx.author

	@ui.button(emoji='<:before_fast_check:754948796139569224>', style=discord.ButtonStyle.blurple)
	async def first_page(self, interaction, button):
		await self.show_page(0)
		await interaction.response.defer()

	@ui.button(emoji='<:before_check:754948796487565332>', style=discord.ButtonStyle.blurple)
	async def before_page(self, interaction, button):
		await self.show_checked_page(self.current_page - 1)
		await interaction.response.defer()

	@ui.button(emoji='<:stop_check:754948796365930517>', style=discord.ButtonStyle.blurple)
	async def stop_page(self, interaction, button):
		self.stop()
		if self.delete_message_after:
			await self.message.delete(delay=0)
		await interaction.response.defer()

	@ui.button(emoji='<:next_check:754948796361736213>', style=discord.ButtonStyle.blurple)
	async def next_page(self, interaction, button):
		await self.show_checked_page(self.current_page + 1)
		await interaction.response.defer()

	@ui.button(emoji='<:next_fast_check:754948796391227442>', style=discord.ButtonStyle.blurple)
	async def last_page(self, interaction, button):
		await self.show_page(self._source.get_max_pages() - 1)
		await interaction.response.defer()







class HelpPageSource(menus.ListPageSource):
    def __init__(self, data, helpcommand):
        super().__init__(data, per_page=6)
        self.helpcommand = helpcommand

    def format_command_help(self, no, command):
        signature = self.helpcommand.get_command_signature(command)
        docs = self.helpcommand.get_command_brief(command)
        return f"{no}. {signature}\n{docs}"
    
    async def format_page(self, menu, entries):
        page = menu.current_page
        max_page = self.get_max_pages()
        starting_number = page * self.per_page + 1
        iterator = starmap(self.format_command_help, enumerate(entries, start=starting_number))
        page_content = "\n".join(iterator)
        embed = discord.Embed(
            title=f"Help Command[{page + 1}/{max_page}]", 
            description=page_content,
            color=lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
        )
        author = menu.ctx.author
        embed.set_footer(text=f"Requested by {author.name}#{author.discriminator}", icon_url=author.display_avatar.url)  # author.avatar in 2.0
        return embed


class MyHelp(commands.HelpCommand):
	def get_command_signature(self, command):
			return '%s%s %s' % (self.context.clean_prefix, command.qualified_name, command.signature)

	def get_command_brief(self, command):
		return command.short_doc or "Command is not documented."

	async def send_bot_help(self, mapping):
		
		filtered = []

		for _, commands in mapping.items():
			filtered = await self.filter_commands(commands, sort=True)

		formatter = HelpPageSource(filtered, self)
		menu = MyMenuPages(formatter, delete_message_after=True)
		await menu.start(self.context)

			# command_signatures = [self.get_command_signature(c) for c in filtered]


		# 	if command_signatures:
		# 		cog_name = getattr(cog, "qualified_name", "Bot-related")
		# 		helpEmbed.add_field(name=cog_name, value="\n".join(command_signatures), inline=False)
		
		# await self.context.reply(embed = helpEmbed)

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
			case_insensitive = True
		)

	async def setup_hook(self) -> None:
		await self.load_extension("cogs.logs")
		await self.load_extension("cogs.info")
		await self.load_extension("cogs.admin")



# Creating a bot instance
client = MyClient()

# Connects the help command class as the main help command of the bot
client.help_command = MyHelp()




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

@client.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CommandNotFound):
		unknownEmbed = discord.Embed(
			title = "Command not found",
			description = "What command are you trying to use?\n``Protip:`` Use ``!help`` to see all the available commands!", 
			color = 0xf08080
			)
		await ctx.send(embed = unknownEmbed)

	else:
		print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
		traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


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
	

async def start():
	await client.start(os.environ.get('token'))
	

asyncio.run(start())