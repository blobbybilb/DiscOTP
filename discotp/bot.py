import binascii
from time import time
import interactions as d
import discotp.data as data
import pyotp
from discotp.config import TOKEN

client = d.Client()


async def check_permissions(ctx: d.SlashContext) -> bool | None:
    if ctx.guild is None:
        return True

    server_id = ctx.guild.id
    server_config = data.get_server_config(server_id)
    if server_config is None:
        await ctx.send("Please configure the bot first! Use /config.")
        return None

    auth_role_id = server_config.get("auth_role")
    auth_channel_id = server_config.get("auth_channel")

    if auth_role_id is None or auth_channel_id is None:
        await ctx.send(
            "Please configure the bot first! Use /config. (Note: if you have already configured the bot, please reconfigure it.)"
        )
        return None

    auth_role = ctx.guild.get_role(auth_role_id)
    auth_channel = ctx.guild.get_channel(auth_channel_id)

    if auth_role is None or auth_channel is None:
        await ctx.send(
            "Invalid configuration! Please reconfigure the bot with a valid auth_role and auth_channel (one or both may have been deleted)."
        )
        return None

    # the if is only to satisfy mypy, this part is only reached if ctx.guild is not None
    if type(ctx.author) == d.Member:

        if ctx.channel != auth_channel:
            await ctx.send(
                f"Please use the bot in the configured channel: {auth_channel.mention}"
            )
            return False
        if not ctx.author.has_role(auth_role):
            await ctx.send(
                f"You do not have permission to use this command. You need the {auth_role.mention} role. And now they have been summoned."
            )
            return False

        return True
    else:
        return True


async def check_account_commands(ctx: d.SlashContext) -> int | None:
    if ctx.guild is None:
        server_id = ctx.channel_id
    else:
        server_id = ctx.guild.id

    server_id: int = int(server_id)  # type: ignore

    if not data.is_configured(server_id):
        await ctx.send("Please configure the bot first! Use /config.")
        return False

    if not await check_permissions(ctx):
        return False

    return server_id


async def ensure_valid_secret(ctx: d.SlashContext, secret: str) -> str | None:
    try:
        return pyotp.TOTP(secret).now()
    except binascii.Error:
        await ctx.send("Invalid secret! Please add a valid TOTP secret.")
        return None


@d.listen()
async def on_ready():
    print(f"Online.")


@d.slash_command(name="config", description="Configure the bot for your server.")
@d.slash_option(
    name="auth_role",
    description="The role that is allowed to use the bot.",
    required=True,
    opt_type=d.OptionType.ROLE,
)
@d.slash_option(
    name="auth_channel",
    description="The channel that the bot will listen to.",
    required=True,
    opt_type=d.OptionType.CHANNEL,
)
async def config(ctx: d.SlashContext, auth_role: d.Role, auth_channel: d.GuildChannel):
    if ctx.guild is None:
        server_id = ctx.channel_id
    else:
        server_id = ctx.guild.id

    server_id: int = int(server_id)  # type: ignore
    auth_role_id: int = int(auth_role.id)  # type: ignore
    auth_channel_id: int = int(auth_channel.id)  # type: ignore

    msg = None

    server_config = data.get_server_config(server_id)
    if server_config is None:
        server_config = {
            "id": server_id,
            "auth_role": auth_role_id,
            "auth_channel": auth_channel_id,
            "accounts": [],
        }
        msg = "Config created!"
    else:
        server_config["auth_role"] = auth_role_id
        server_config["auth_channel"] = auth_channel_id
        msg = "Config updated!"

    data.set_server_config(server_id, server_config)
    await ctx.send(msg)


@d.slash_command(
    name="view-config", description="View the bot configuration for your server."
)
async def view_config(ctx: d.SlashContext):
    if ctx.guild is None:
        server_id = ctx.channel_id
    else:
        server_id = ctx.guild.id

    server_id: int = int(server_id)  # type: ignore

    server_config = data.get_server_config(server_id)
    if server_config is None:
        await ctx.send("No configuration found for this server.")
    else:
        auth_role_id = server_config.get("auth_role")
        auth_channel_id = server_config.get("auth_channel")
        accounts = server_config.get("accounts")

        response = f"Configuration for server {server_id}:\n"
        response += f"Auth Role: {auth_role_id}\n"
        response += f"Auth Channel: {auth_channel_id}\n"
        response += f"Accounts: {accounts}\n"

        await ctx.send(response)


@d.slash_command(name="add-account", description="Add a TOTP account.")
@d.slash_option(
    name="name",
    description="The name of the account.",
    required=True,
    opt_type=d.OptionType.STRING,
)
@d.slash_option(
    name="secret",
    description="The secret of the account.",
    required=True,
    opt_type=d.OptionType.STRING,
)
async def add_account(ctx: d.SlashContext, name: str, secret: str):
    server_id = await check_account_commands(ctx)
    if not server_id:
        return

    account: data.Account = {"name": name, "secret": secret}

    if not await ensure_valid_secret(ctx, secret):
        return

    if data.add_account(server_id, account):
        await ctx.send(f"Account {name} added!")
    else:
        print(1)
        await ctx.send(f"Account {name} already exists!")


@d.slash_command(name="update-account", description="Update a TOTP account.")
@d.slash_option(
    name="name",
    description="The name of the account.",
    required=True,
    opt_type=d.OptionType.STRING,
)
@d.slash_option(
    name="new_secret",
    description="The new secret of the account.",
    required=True,
    opt_type=d.OptionType.STRING,
)
async def update_account(ctx: d.SlashContext, name: str, new_secret: str):
    server_id = await check_account_commands(ctx)
    if not server_id:
        return

    account = data.get_account(server_id, name)
    if account is None:
        await ctx.send(f"Account {name} does not exist!")
        return

    if not await ensure_valid_secret(ctx, new_secret):
        return

    account["secret"] = new_secret
    data.update_account(server_id, account)
    await ctx.send(f"Account {name} updated!")


@d.slash_command(name="delete-account", description="Delete a TOTP account.")
@d.slash_option(
    name="name",
    description="The name of the account.",
    required=True,
    opt_type=d.OptionType.STRING,
)
async def delete_account(ctx: d.SlashContext, name: str):
    server_id = await check_account_commands(ctx)
    if not server_id:
        return

    if data.delete_account(server_id, name):
        await ctx.send(f"Account {name} deleted!")
    else:
        await ctx.send(f"Account {name} does not exist!")


@d.slash_command(name="list-accounts", description="List all TOTP accounts.")
async def list_accounts(ctx: d.SlashContext):
    server_id = await check_account_commands(ctx)
    if not server_id:
        return

    accounts = data.get_account_names(server_id)

    if not accounts:
        await ctx.send("No accounts found!")
        return

    response = "Accounts:\n"
    for account in accounts:
        response += f"{account}\n"

    await ctx.send(response)


@d.slash_command(name="totp", description="Generate a TOTP code for an account.")
@d.slash_option(
    name="name",
    description="The name of the account.",
    required=True,
    opt_type=d.OptionType.STRING,
)
async def totp(ctx: d.SlashContext, name: str):
    if ctx.guild is None:
        server_id = ctx.channel_id
    else:
        server_id = ctx.guild.id

    server_id: int = int(server_id)  # type: ignore

    if not data.is_configured(server_id):
        await ctx.send("Please configure the bot first! Use /config.")
        return

    account = data.get_account(server_id, name)
    if account is None:
        await ctx.send(f"Account {name} does not exist!")
        return

    totp = pyotp.TOTP(account["secret"])

    code = await ensure_valid_secret(ctx, account["secret"])
    if code is None:
        return

    await ctx.send(
        f"Code for '{name}': __**{code}**__\nExpires in {int(30 - time() % 30)} seconds"
    )


client.start(TOKEN)


data.db.close()
