from discord.ext import commands
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
            id = member

        user = discord.utils.get(ctx.guild.members, id = id)
        
        if user == None:
            pass
        else:
            userinfoEmbed = discord.Embed(
                title = user.name + "#" + user.discriminator,
                color = lgd.hexConvertor(mn.colorCollection.find({},{"_id": 0, "Hex": 1}))
            )

            userinfoEmbed.add_field(
                name = "Joined at",
                value = user.joined_at,
                inline = True
            )

            userinfoEmbed.add_field(
                name = "Created at",
                value = user.created_at,
                inline = True
            )

            # userinfoEmbed.add_field(
            #     name = ""
            # )
            await ctx.send(embed = userinfoEmbed)