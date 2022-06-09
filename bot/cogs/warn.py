import discord
import logical_definitions as lgd
import mongo_declaration as mn
from discord.ext import commands


def setup(client):
    client.add_cog(warn(client))

class warn(commands.Cog):
    def __init__(self, client):
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