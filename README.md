# TOTP-discord-bot
Discord bot to generate TOTP codes, and manage TOTP accounts.

This is intended for when you need to share an account for something (I needed it for sharing a team google account, and we kept the password in the open so I set up TOTP 2FA on it, and made this).

Keep your recovery codes safe, don't rely completely on this bot. Things can go wrong with it, and you don't want to be locked out of your accounts.

[Invite link](https://discord.com/oauth2/authorize?client_id=1210714458024972358&permissions=0&scope=bot)

### Security

This bot is not designed to be extremely secure. It doesn't use end-to-end encryption, so if you use the public bot, you are trusting it with your TOTP secrets, and if it gets compromised, your accounts are at risk. I am not liable for any damages caused by using this bot.

**NOTE**: This is unrelated to my [TOTP[App]](http://github.com/blobbybilb/TOTP-App). That one uses end-to-end encryption, and is designed to be secure. (I'm not liable for that one either, but it's much more secure than this bot.)

### Self-hosting
1. Replace bot token in `config.py`.
2. Run `poetry install`
3. Run `poetry run python3 main.py`

### Usage
![Screenshot of Bot Commands](https://github.com/blobbybilb/TOTP-discord-bot/blob/main/Screenshot%202024-02-23%20at%207.19.49 PM.png)

### License

GPLv3
