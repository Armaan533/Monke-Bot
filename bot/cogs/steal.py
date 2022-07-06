import discord
from discord.ext import commands
import logical_definitions as lgd
import mongo_declaration as mn
import traceback, sys

class Steal(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def steal(self, ctx: commands.Context, emoji: discord.PartialEmoji):
        if ctx.guild.emoji_limit == len(ctx.guild.emojis):
            emojiFullEmbed = discord.Embed(
                title = "No emoji slots available",
                description = "Hey, if you wanna add more emojis to the server\nthen please consider boosting the server\nor remove any useless ones",
                color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
            )
            await ctx.send(embed = emojiFullEmbed)

        else:
            emojibytes = await emoji.read()
            newemoji = await ctx.guild.create_custom_emoji(name = emoji.name, image = emojibytes, reason = f"Emoji added by {ctx.author.name}#{ctx.author.discriminator}")
            if newemoji.animated:
                successfulEmbed = discord.Embed(
                    title = "",
                    description = f"Emoji <a:{newemoji.name}:{newemoji.id}> added successfully",
                    color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
                )
            else:
                successfulEmbed = discord.Embed(
                    title = "",
                    description = f"Emoji <:{newemoji.name}:{newemoji.id}> added successfully",
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
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

async def setup(client):
    await client.add_cog(Steal(client))