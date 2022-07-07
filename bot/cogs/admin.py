import asyncio
import discord
import logical_definitions as lgd
import mongo_declaration as mn
from discord.ext import commands
import traceback, sys

async def setup(client):
    await client.add_cog(Admin(client))

class Admin(commands.Cog):
    def __init__(self, client: discord.Client):
        self.client = client

    @commands.has_guild_permissions(administrator = True)
    @commands.command()
    async def lock(self, ctx):
        everyoneRole = discord.utils.get(ctx.guild.roles, name = "@everyone")
        await ctx.channel.set_permissions(everyoneRole, read_messages=True, send_messages=False)
        await ctx.send(embed = discord.Embed(description = "Channel locked successfully",
											color = 0x000000))


    @commands.has_guild_permissions(administrator = True)
    @commands.command()
    async def unlock(self, ctx):
        everyoneRole = discord.utils.get(ctx.guild.roles, name = "@everyone")
        await ctx.channel.set_permissions(everyoneRole, send_messages = True)
        await ctx.send(embed = discord.Embed(description = "Channel unlocked successfully",
											color = 0x000000))


    @commands.has_guild_permissions(administrator = True)
    @commands.command()
    async def warn(self, ctx, member: discord.Member, *reasonList):

        if (member.guild_permissions.administrator) or (member == ctx.guild.owner):
            await ctx.reply(f"I cannot warn {member.mention} because they have administrator permissions")
        
        elif member.top_role > ctx.author.top_role:
            higherheirarchyEmbed = discord.Embed(
                title = "",
                description = f"You cannot warn {member.mention} because they have higher role than you",
                color = 0x000000
            )
            await ctx.reply(embed = higherheirarchyEmbed)

        elif ctx.author.id == member.id:
            samePersonEmbed = discord.Embed(
                title = "",
                description = "Dude, you can't warn yourself. ||Atleast by this bot||",
                color = 0x000000
            )
            await ctx.reply(embed = samePersonEmbed)
        else:
            
            warndocument = mn.warncollection.find_one({"_id": str(member.id), "guild": ctx.guild.id},{"_id": 0, "warns":1})

            reason = ""
            for i in reasonList:
                reason = reason + i + " "

            if warndocument == None:
                newWarn = {
                    "_id": str(member.id),
                    "guild": ctx.guild.id,
                    "warns": 1
                }

                mn.warncollection.insert_one(newWarn)
                currentwarns = 0
            else:
                currentwarns = warndocument["warns"]
                upwarn = {
                    "$set": {
                        "warns": currentwarns+1
                    }
                }
                mn.warncollection.update_one({"_id": str(member.id), "guild": ctx.guild.id}, upwarn)

            warnDmEmbed = discord.Embed(
                    title = "",
                    description = f"You were warned for {reason} by {ctx.author.name}#{ctx.author.discriminator} in {ctx.guild.name}\nCurrent Warn(s): `{currentwarns+1}`\nWe hope you manner well now onwards\nRegards,\nMonke Bot",
                    color = 0x000000
                )

            warnEmbed = discord.Embed(
                    title = "",
                    description = f"_{member.mention} is warned by {ctx.author.mention} for {reason}_\n_Current Warn(s)_: `{currentwarns+1}`",
                    color = 0x000000
                )

            await ctx.reply(embed = warnEmbed)
            dmchannel = await member.create_dm()
            await dmchannel.send(embed = warnDmEmbed)
            
            warnpunishdoc = mn.warnPunishCollection.find_one({"_id": str(ctx.guild.id)},{"_id":0})
            if warnpunishdoc != None:
                print(warnpunishdoc)

    @commands.has_guild_permissions(administrator = True)
    @commands.command()
    async def warn_remove(self, ctx : commands.Context, member: discord.Member, number: int):
        warnsDoc = mn.warncollection.find_one({"_id": str(member.id), "guild": ctx.guild.id},{"_id": 0, "warns": 1})
        if warnsDoc == None:
            noWarnsEmbed = discord.Embed(
                title = "No Warns",
                description = f"{member.mention} has 0 warns",
                color = 0x000000
            )
            await ctx.reply(embed = noWarnsEmbed)
        elif number > warnsDoc["warns"]:
            negativeRemovalEmbed = discord.Embed(
                title = "Bad Argument",
                description = f"You can't remove more warns than {member.mention} already has",
                color = 0x000000
            )
            await ctx.reply(embed = negativeRemovalEmbed)
        else:
            currentwarns = warnsDoc["warns"] - number
            update = {
                "$set": {"warns": warnsDoc["warns"] - number}
            }
            mn.warncollection.update_one({"_id": str(member.id), "guild": ctx.guild.id},update)
            
            warnsRemovedEmbed = discord.Embed(
                title = "Warns Removed",
                description = f"Removed `{number}` warn(s) for {member.mention}\nNow they have {currentwarns} warn(s) left",
                color = 0x000000
            )
            await ctx.reply(embed = warnsRemovedEmbed)

    @commands.has_guild_permissions(administrator = True)
    @commands.command()
    async def set_warn_punishment(self, ctx: commands.Context):
        punishList = []
        while True:

            punishTypeEmbed = discord.Embed(
                title = "Punishment Type",
                description = "For Example: **kick** or **ban**\nOlder Punishments will be discarded",
                color = 0x000000
            )
            msg = await ctx.send(embed = punishTypeEmbed)
            try:
                punishment = await self.client.wait_for("message",check = lambda m: m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ["kick", "ban"], timeout = 30)
            except asyncio.exceptions.TimeoutError:
                await msg.edit(embed = discord.Embed(title = "", description = "Timed Out"))
                return
                break
            await punishment.delete()

            numberOfWarnsEmbed = discord.Embed(
                title = "Number of Warns needed",
                description = "How many warns are needed to trigger the punishment?",
                color = 0x000000
            )
            await msg.edit(embed = numberOfWarnsEmbed)
            try:
                noOfWarns = await self.client.wait_for("message", check= lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout = 30)
            except asyncio.exceptions.TimeoutError:
                await msg.edit(embed = discord.Embed(title = "", description = "Timed Out"))
                return
                break
            await noOfWarns.delete()

            punishList.append({punishment.content: int(noOfWarns.content)})

            morePunishmentEmbed = discord.Embed(
                title = "More Punishments?",
                description = "Do you want more punishments on warn?\nYes or No",
                color = 0x000000
            )
            await msg.edit(embed = morePunishmentEmbed)
            try:
                choice = await self.client.wait_for("message", check = lambda m: m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ["yes","no"], timeout = 30)
            except asyncio.exceptions.TimeoutError:
                await msg.edit(embed = discord.Embed(title = "", description = "Timed Out"))
                return
                break
            await choice.delete()
            await msg.delete()
            if choice.content.lower() == "no":
                break
        
        oldpunishdoc = mn.warnPunishCollection.find_one({"_id":str(ctx.guild.id)},{"_id": 0, "Punishment": 1})
        
        if oldpunishdoc == None:
            mn.warnPunishCollection.insert_one({"_id": str(ctx.guild.id), "Punishment": punishList})
        else:
            mn.warnPunishCollection.update_one(
                {"_id": str(ctx.guild.id)},
                {"$set": {"Punishment":punishList}}
                )

        punishmentSuccessEmbed = discord.Embed(
            title = "",
            description = "_Punishment Saved Successfully_\n||Rule Breakers Watchout!!||",
            color = 0x000000
        )
        await ctx.send(embed = punishmentSuccessEmbed)

    @commands.command(help = "For deleting the mentioned amount of messages")
    @commands.has_guild_permissions(manage_messages = True)
    async def purge(self, ctx: commands.Context, limit: int, type: str = None):
        await ctx.message.delete()
        if type == None:
            await ctx.channel.purge(limit=limit, reason = f"{ctx.author.name}#{ctx.author.discriminator} purged messages sent by users and bots")
        elif type.lower() in ["bot","bots"]:
            botcheck = lambda m: m.author.bot == True
            await ctx.channel.purge(limit = limit, check = botcheck, reason = f"{ctx.author.display_name}#{ctx.author.discriminator} purged messages sent by bots")
        elif type.lower() in ["user","users","members","member"]:
            usercheck = lambda m: m.author.bot == False
            await ctx.channel.purge(limit = limit, check = usercheck, reason = f"{ctx.author.display_name}#{ctx.author.discriminator} purged messages sent by users")
    @purge.error
    async def purge_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            missingpermEmbed = discord.Embed(title = "No permission",
										description = "You can't purge because you don't have manage messages permission",
										color = 0x000000)
            await ctx.send(embed = missingpermEmbed)
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    @commands.command(help = "For deleting large amount of messages in a channel")
    @commands.has_guild_permissions(administrator = True)
    async def nuke(self, ctx):
        await ctx.message.delete()
        limit = 10000
        await ctx.channel.purge(limit = limit)
    
    @nuke.error
    async def nuke_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            NukeErrorEmbed = discord.Embed(title = "No Permission to do that",
									   description = "You can't nuke this channel because you don't have required permissions",
									   color = 0x000000)
            await ctx.send(embed = NukeErrorEmbed)


    @commands.command(help = "For kicking members out of the server")
    @commands.has_guild_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *kickReasonList):
        if member.id == 823894464798916688:
            devBanEmbed = discord.Embed(
			    title = "Denied :octagonal_sign:",
			    description = "You can't kick developer of this bot",
			    color = 0x000000
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
											color=0x000000)
            else:
                SuccessKickEmbed = discord.Embed(title="Successful",
											description=f"Successfully kicked {member.name}",
											color=0x000000)
            await ctx.send(embed = SuccessKickEmbed)

    @kick.error
    async def kick_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            text = "Sorry {}, you do not have permissions to do that!".format(ctx.message.author)
            await ctx.send(text)
	

    @commands.command(help = "For banning members")
    @commands.has_guild_permissions(ban_members = True)
    async def ban(self, ctx, member: discord.Member, *banReasonList):

        if member.id == 823894464798916688:
            devBanEmbed = discord.Embed(
			    title = "Denied :octagonal_sign:",
			    description = "You can't ban developer of this bot",
			    color = 0x000000
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
				    color=0x000000)
            else:
                SuccessBanEmbed = discord.Embed(title="Successful",
											description=f"Successfully banned {member.name}",
											color=0x000000)
            await ctx.send(embed = SuccessBanEmbed)

    @ban.error
    async def ban_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            MissingPermsEmbed = discord.Embed(
			    title = "Error",
			    description = "What are you trying to do?\nYou can't ban that sucker because you don't have permissions to do that!",
			    color = 0x000000)
            await ctx.send(embed = MissingPermsEmbed)
        elif isinstance(error, commands.UserNotFound):
            banUserNotFoundEmbed = discord.Embed(title = "User not found",
											description = "try checking the id and discriminant of user again",
											color = 0x000000)
            await ctx.send(embed = banUserNotFoundEmbed)

    @commands.guild_only()
    @commands.has_guild_permissions(administrator = True)
    @commands.command(help = "To set a channel as a log channel")
    async def setlogChannel(self, ctx):
        logChannelEmbed = discord.Embed(description = "Mention the channel",
										   color = 0x000000)
        logMessage = await ctx.send(embed = logChannelEmbed)
        try:
            authorcheck = lambda m: m.author == ctx.author and m.channel == ctx.channel
            name = await self.client.wait_for("message", check = authorcheck, timeout = 30)
        except asyncio.exceptions.TimeoutError:
            await logMessage.edit(embed = discord.Embed(description = "timed out",
														color = 0x000000),
								  delete_after = 10)
            return
        await name.delete()
        mn.guildpref.update_one({"_id":str(ctx.guild.id)},{"$set":{"Logs":name.content.lstrip("<#").rstrip(">")}})
        await logMessage.edit(embed = discord.Embed(
			description = "Log channel added successfully",
			color = 0x000000
		))