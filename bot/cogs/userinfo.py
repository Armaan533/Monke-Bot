from discord.ext import commands
import datetime
import discord
import mongo_declaration as mn
import logical_definitions as lgd

def setup(client):
    client.add_cog(Userinfo(client))

class Userinfo(commands.Cog):
    
    def __init__(self, client):
        self.client = client

    @commands.command(aliases = ["Userinfo","Memberinfo"])
    async def userinfo(self, ctx: commands.Context, member: str):
        if member.startswith("<@") and member.endswith(">"):
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

            await ctx.send(embed = userinfoEmbed)