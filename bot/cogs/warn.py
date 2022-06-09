import asyncio
import discord
import logical_definitions as lgd
import mongo_declaration as mn
from discord.ext import commands, tasks


def setup(client):
    client.add_cog(warn(client))

class warn(commands.Cog):
    def __init__(self, client: discord.Client):
        self.client = client

    @commands.command()
    async def warn(self, ctx, member: discord.Member, *reasonList):

        if (member.guild_permissions.administrator) or (member == ctx.guild.owner):
            await ctx.reply(f"I cannot warn {member.mention} because they have administrator permissions")
        
        elif ctx.author.id == member.id:
            samePersonEmbed = discord.Embed(
                title = "",
                description = "Dude, you can't warn yourself. ||Atleast by this bot||",
                color = lgd.hexConvertor(mn.colorCollection.find({},{"_id": 0, "Hex": 1}))
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
                    color = lgd.hexConvertor(mn.colorCollection.find({},{"_id": 0, "Hex": 1}))
                )

            warnEmbed = discord.Embed(
                    title = "",
                    description = f"_{member.mention} is warned by {ctx.author.mention} for {reason}_\n_Current Warn(s)_: `{currentwarns+1}`",
                    color = lgd.hexConvertor(mn.colorCollection.find({},{"_id": 0, "Hex": 1}))
                )

            await ctx.reply(embed = warnEmbed)
            dmchannel = await member.create_dm()
            await dmchannel.send(embed = warnDmEmbed)
            
            warnpunishdoc = mn.warnPunishCollection.find_one({"_id": str(ctx.guild.id)},{"_id":0})
            if warnpunishdoc != None:
                for i in warnpunishdoc:
                    await ctx.send(i)

    @commands.command()
    async def warn_remove(self, ctx : commands.Context, member: discord.Member, number: int):
        warnsDoc = mn.warncollection.find_one({"_id": str(member.id), "guild": ctx.guild.id},{"_id": 0, "warns": 1})
        if warnsDoc == None:
            noWarnsEmbed = discord.Embed(
                title = "No Warns",
                description = f"{member.mention} has 0 warns",
                color = lgd.hexConvertor(mn.colorCollection.find({},{"_id": 0, "Hex": 1}))
            )
            await ctx.reply(embed = noWarnsEmbed)
        elif number > warnsDoc["warns"]:
            negativeRemovalEmbed = discord.Embed(
                title = "Bad Argument",
                description = f"You can't remove more warns than {member.mention} already has",
                color = lgd.hexConvertor(mn.colorCollection.find({},{"_id": 0, "Hex": 1}))
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
                color = lgd.hexConvertor(mn.colorCollection.find({},{"_id": 0, "Hex": 1}))
            )
            await ctx.reply(embed = warnsRemovedEmbed)

        
    @commands.command()
    async def set_warn_punishment(self, ctx: commands.Context):
        punishList = []
        while True:

            punishTypeEmbed = discord.Embed(
                title = "Punishment Type",
                description = "For Example: **kick** or **ban**\nOlder Punishments will be discarded",
                color = lgd.hexConvertor(mn.colorCollection.find({},{"_id": 0, "Hex": 1}))
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
                color = lgd.hexConvertor(mn.colorCollection.find({},{"_id": 0, "Hex": 1}))
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
                color = lgd.hexConvertor(mn.colorCollection.find({},{"_id": 0, "Hex": 1}))
            )
            await msg.edit(embed = morePunishmentEmbed)
            try:
                choice = await self.client.wait_for("message", check = lambda m: m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ["yes","no"], timeout = 30)
            except asyncio.exceptions.TimeoutError:
                await msg.edit(embed = discord.Embed(title = "", description = "Timed Out"))
                return
                break
            if choice.content.lower() == "no":
                break
            await msg.delete()
        
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
            color = lgd.hexConvertor(mn.colorCollection.find({},{"_id": 0, "Hex": 1}))
        )
        await ctx.send(embed = punishmentSuccessEmbed)