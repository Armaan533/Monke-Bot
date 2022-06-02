import discord
from discord.ext import commands
import mongo_declaration as mn
import logical_definitions as lgd

def setup(client):
    client.add_cog(warn(client))

class warn(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def warn(self, ctx, member: discord.Member, *reasonList):

        if ("administrator" in member.guild_permissions) or (member == ctx.guild.owner):
            await ctx.send(f"I cannot warn {member.mention} because he/she has administrator permissions")
        else:
            warncollection = mn.botdbase["Warns"]
            warndocument = warncollection.find_one({"_id": str(member.id), "guild": ctx.guild.id},{"_id": 0, "warns":1})

            reason = ""
            for i in reasonList:
                reason = reason + i + " "

            if warndocument == None:
                newWarn = {
                    "_id": str(member.id),
                    "guild": ctx.guild.id,
                    "warns": 1
                }

                warncollection.insert_one(newWarn)
                currentwarns = 0
            else:
                currentwarns = warndocument["warns"]
                upwarn = {
                    "$set": {
                        "warns": currentwarns+1
                    }
                }
                warncollection.update_one({"_id": str(member.id), "guild": ctx.guild.id}, upwarn)

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

            await ctx.send(embed = warnEmbed)
            dmchannel = await member.create_dm()
            await dmchannel.send(warnDmEmbed)