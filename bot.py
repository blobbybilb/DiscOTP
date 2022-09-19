import discord
import pyotp

bot = discord.Bot()

@bot.slash_command()
async def code(ctx):
    totp = pyotp.TOTP('totp secret')
    theCode = totp.now()

    await ctx.respond(f"code: {theCode}")

bot.run("token")
