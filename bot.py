from time import time
import discord
import pyotp

bot = discord.Bot()

data = {
    "google": "totp secret",
    "github": "totp secret",
}


@bot.slash_command()
async def code(ctx, account):
    try:
        totp = pyotp.TOTP(data[account])
    except KeyError:
        return await ctx.respond(f"Account `{account}` not found")

    theCode = totp.now()

    return await ctx.respond(f"""
    {account} code: {theCode}

    Expires in: {int(30 - time() % 30)} seconds
    """)

bot.run("token")
