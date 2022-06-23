import discord, asyncio
from discord.ext import commands
import logical_definitions as lgd
import mongo_declaration as mn

class self_roles(commands.Cog):

	def __init__(self, client):
		self.client = client

	@commands.command()
	async def self_role_menu(self, ctx, num):
		roles = []
		roleEmbed = discord.Embed(
			title = "Role Selection",
			description = "Mention the role",
			color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0, "Hex":1}))
		)
		authorcheck = lambda m: m.author == ctx.author and m.channel == ctx.channel
		roleMessage = await ctx.send(embed = roleEmbed)
		while len(roles) < int(num):
			try:
				roleMention = await self.client.wait_for("message", check = authorcheck, timeout = 30)
			except asyncio.exceptions.TimeoutError:
				await roleMessage.edit(content = "timed out", delete_after = 10)
				break
				return
			await roleMention.delete()
			# temprole = discord.utils.get(ctx.guild.roles, id = int(roleMention.content.lstrip("<@&").rstrip(">")))
			# if temprole.is_assignable():
			roles.append(int(roleMention.content.lstrip("<@&").rstrip(">")))
			# elif roleMention.content == "cancel":
				# break
			# else:
				# await ctx.send(embed = discord.Embed(
					# name = "Invalid Role",
					# description = "This role is above bot or managed by an integration\nPlease try another role",
					# color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0, "Hex":1}))),
							  # delete_after = 10)
				
		await roleMessage.delete()
		emojis = []
		if len(roles) == int(num):
			for i in roles:
				role = discord.utils.get(ctx.guild.roles, id = i)
				EmojiEmbed = discord.Embed(
					title = "Emoji Selection",
					description = f"Send the emoji for {role.mention}",
					color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
				)
				emojiMessage = await ctx.send(embed = EmojiEmbed)
				authorcheck = lambda m: m.author == ctx.author and m.channel == ctx.channel
				try:
					emoji = await self.client.wait_for("message", check = authorcheck, timeout = 30)
				except asyncio.exceptions.TimeoutError:
					await emojiMessage.edit(content = "timed out", delete_after = 10)
					break
					return
				await emojiMessage.delete()
				await emoji.delete()
				emojis.append(emoji.content)

			print(emojis)
			print(roles)
				
			selfRoleEmbed = discord.Embed(
				description ="**React to take the role**",
				color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0, "Hex":1}))
			)
			j = 0
			while j < int(num):
				role = discord.utils.get(ctx.guild.roles, id = roles[j])
				selfRoleEmbed.add_field(name = "\u200b",value = f"{role.name}:    {emojis[j]}",inline = False)
				j+=1
			selfRoleMessage = await ctx.send(embed = selfRoleEmbed)
				
			for e in emojis:
				await selfRoleMessage.add_reaction(e)

		else:
			pass

async def setup(client):
	await client.add_cog(self_roles(client))