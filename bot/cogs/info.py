from discord.ext import commands
import discord
import logical_definitions as lgd
import mongo_declaration as mn
import datetime

async def setup(client):
    await client.add_cog(Info(client))

class Info(commands.Cog):
    
    def __init__(self, client):
        self.client = client

    @commands.command(help = "For getting info about this server")
    async def serverinfo(self, ctx: commands.Context):
        guild = ctx.guild
        serverInfoEmbed = discord.Embed(
            title = guild.name,
            timestamp = guild.created_at,
            color = lgd.hexConvertor(mn.colorCollection.find({},{"_id":0,"Hex":1}))
        )
        serverInfoEmbed.set_thumbnail(url = guild.icon.url)
        serverInfoEmbed.set_footer(text = f"Requested By {ctx.author.name} | Server Created On", icon_url = ctx.author.display_avatar.url)

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
            inline = True
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
            inline = True
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
            inline = True
        )

        serverInfoEmbed.add_field(
            name = "Boosts",
            value = f"```{str(guild.premium_subscription_count)}```",
            inline = True
        )

        await ctx.send(embed = serverInfoEmbed)

    @commands.command(help = "For getting information about the user/member", aliases = ["Memberinfo"])
    async def userinfo(self, ctx: commands.Context, member: str = None):
        if member == None:
            id = ctx.author.id

        elif member.startswith("<@") and member.endswith(">"):
            id = int(member.lstrip("<@").rstrip(">"))

        elif member.startswith("<@!") and member.endswith(">"):
            id = int(member.lstrip("<@!").rstrip(">"))

        else:
            id = int(member)

        user = discord.utils.get(ctx.guild.members, id = id)
        
        if user == None:
            pass
        else:
            userinfoEmbed = discord.Embed(
                title = user.name + "#" + user.discriminator,
                color = lgd.hexConvertor(mn.colorCollection.find({},{"_id": 0, "Hex": 1}))
            )

            joiningDateTime = user.joined_at
            joinTimestamp = datetime.datetime.timestamp(joiningDateTime)

            userinfoEmbed.add_field(
                name = "Joined at",
                value = f"<t:{int(joinTimestamp)}:F>",
                inline = True
            )

            creationDateTime = user.created_at
            createTimestamp = datetime.datetime.timestamp(creationDateTime)
            userinfoEmbed.add_field(
                name = "Created at",
                value = f"<t:{int(createTimestamp)}:F>",
                inline = True
            )
            roleMention = ""
            totalRoles = 0
            for i in user.roles:
                if totalRoles == 0:
                    totalRoles += 1
                    continue
                roleMention += i.mention

            userinfoEmbed.add_field(
                name = f"Roles: [{totalRoles}]",
                value = roleMention,
                inline = False
            )

            userinfoEmbed.set_thumbnail(url = user.avatar_url)
            userinfoEmbed.set_footer(text = f"Requested by {ctx.author.name}", icon_url = ctx.author.avatar_url)

            await ctx.send(embed = userinfoEmbed)