from time import time
import discord
from discord.ext.commands import Context as Ctx
import pyotp
import data

'''
TODO:
- error handling
'''


bot = discord.Bot()


def user_has_permission(ctx: Ctx):
    return (ctx.author.guild_permissions.administrator
            or ctx.guild.get_role(data.get_allowed_role(ctx.guild.id)) in ctx.author.roles
            )


@bot.slash_command()
async def code(ctx: Ctx, account: str):
    '''Generates a TOTP code for the given account'''
    if not user_has_permission(ctx):
        return await ctx.respond('You do not have permission to use this command.')
    try:
        totp = pyotp.TOTP(data.get(ctx.guild.id)[account])
    except KeyError:
        return await ctx.respond(f"Account `{account}` not found")

    theCode = totp.now()

    return await ctx.respond(f"{account} code: __**{theCode}**__\n\nExpires in: {int(30 - time() % 30)} seconds")


@bot.slash_command()
async def add(ctx: Ctx, account: str, secret: str):
    '''Adds an account'''
    if not user_has_permission(ctx):
        return await ctx.respond('You do not have permission to use this command.')
    data.add_account(ctx.guild.id, account, secret)
    return await ctx.respond(f"Added account `{account}`")


@bot.slash_command()
async def remove(ctx: Ctx, account: str):
    '''Remove an account'''
    if not user_has_permission(ctx):
        return await ctx.respond('You do not have permission to use this command.')
    data.remove_account(ctx.guild.id, account)
    return await ctx.respond(f"Account `{account}` removed")


@bot.slash_command()
async def set_allowed_role(ctx: Ctx, role: discord.Role):
    '''Allows users with the specified role to use the bot'''
    if not user_has_permission(ctx):
        return await ctx.respond("You are not an administrator")

    data.set_allowed_role(ctx.guild.id, role.id)
    await ctx.respond(f"Allowed role set to {role.name}")


@bot.slash_command()
async def create(ctx: Ctx):
    '''Creates/Resets server's stored accounts'''
    if not user_has_permission(ctx):
        return await ctx.respond('You do not have permission to use this command.')
    data.create_guild(ctx.guild.id)
    await ctx.respond("Created/reset storage file for this guild")


@bot.slash_command()
async def list(ctx: Ctx):
    '''Lists all accounts'''
    if not user_has_permission(ctx):
        return await ctx.respond('You do not have permission to use this command.')
    accounts = data.get(ctx.guild.id)
    await ctx.respond(', '.join(accounts.keys()).replace(', --allowed_role--', '').replace('--allowed_role--', ''))


# help command
@ bot.slash_command()
async def help(ctx: Ctx):
    '''Shows help'''
    await ctx.respond(
        '''
** Commands: **

`/ code <account>`: Get the code for an account
`/ add <account> <secret >`: Add an account
`/ remove <account>`: Remove an account
`/ list`: List all accounts
`/ set_allowed_role <role>`: Set the role that can use the bot(TODO)

Note: This bot is open source and can be self-hosted. More info at <https://github.com/blobbybilb/TOTP-discord-bot>.
'''
    )

bot.run("token")
