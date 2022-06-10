from discord.ext import commands
import discord
import logical_definitions as lgd
import mongo_declaration as mn

def setup(client):
    client.add_cog(serverinfo(client))

class serverinfo(commands.Cog):
    
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def serverinfo(self, ctx: commands.Context):
        guild = ctx.guild
        serverInfoEmbed = discord.Embed(
            title = guild.name,
            timestamp = guild.created_at,
            color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
        )
        serverInfoEmbed.set_thumbnail(url = guild.icon_url)
        serverInfoEmbed.set_footer(text = f"Requested By {ctx.author.name} | Server Created On", icon_url = ctx.author.avatar_url)

        serverInfoEmbed.add_field(
            name = "Owner",
            value = f"```{guild.owner.name}#{guild.owner.discriminator}```",
            inline = False
        )

        member = 0
        bot = 0
        for i in guild.members:
            if i.bot:
                bot += 1
            else:
                member += 1

        serverInfoEmbed.add_field(
            name = "Members",
            value = f"```Members: {str(member)}```",
            inline = False
        )

        serverInfoEmbed.add_field(
            name = "Bots",
            value = f"```Bots: {str(bot)}```",
            inline = True
        )

        serverInfoEmbed.add_field(
            name = "Server ID",
            value = f"```{str(ctx.guild.id)}```",
            inline = False
        )

        serverInfoEmbed.add_field(
            name = "Categories",
            value = f"```{str(len(guild.categories))}```",
            inline = False
        )
        
        serverInfoEmbed.add_field(
            name = "Text Channels",
            value = f"```{str(len(guild.text_channels))}```",
            inline = True
        )

        serverInfoEmbed.add_field(
            name = "Voice Channels",
            value = f"```{str(len(guild.voice_channels))}```",
            inline = True
        )

        normal = 0
        animated = 0
        
        for i in guild.emojis:
            if i.animated:
                animated += 1
            else:
                normal += 1

        serverInfoEmbed.add_field(
            name = "Server Emojis",
            value = f"```Normal Emojis: {str(normal)} | Animated Emojis: {str(animated)}```",
            inline = False
        )

        serverInfoEmbed.add_field(
            name = "Server Boost Level",
            value = f"```{str(guild.premium_tier)}```",
            inline = False
        )

        serverInfoEmbed.add_field(
            name = "Boosts",
            value = f"```{str(guild.premium_subscription_count)}```",
            inline = True
        )


        # serverInfoEmbed.add_field(
        #     name = ""
        # )

        await ctx.send(embed = serverInfoEmbed)