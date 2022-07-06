import discord
from discord.ext import commands
import logical_definitions as lgd
import mongo_declaration as mn

class Steal(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def steal(self, ctx: commands.Context, emoji: discord.Emoji):
        if ctx.guild.emoji_limit == len(ctx.guild.emojis):
            emojiFullEmbed = discord.Embed(
                title = "No emoji slots available",
                description = "Hey, if you wanna add more emojis to the server\nthen please consider boosting the server\nor remove any useless ones",
                color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
            )
            await ctx.send(embed = emojiFullEmbed)

        else:
            emojibytes = emoji.url.read()
            newemoji = await ctx.guild.create_custom_emoji(name = emoji.name, image = emojibytes, reason = f"Emoji added by {ctx.author.name}#{ctx.author.discriminator}")
            successfulEmbed = discord.Embed(
                title = "",
                description = f"Emoji :{newemoji.name}: added successfully",
                color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
            )
            await ctx.send(embed = successfulEmbed)
    
    @steal.error
    async def steal_error(self, ctx: commands.Context, error):
        if isinstance(error, discord.Forbidden):
            noBotPermsEmbed = discord.Embed(
                title = "No permission",
                description = "I do not have the required permissions, please ask admins to give me these permission(s):\n``Manage emojis``",
                color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":1,"Hex":1}))
            )
            await ctx.send(noBotPermsEmbed)

async def setup(client):
    await client.add_cog(Steal(client))