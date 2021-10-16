# fbtc-claimer

The script links with freebitco.in website through GET and POST requests and claims free BTC every hour.
Requirement is to unlock the account to play without captcha.

It uses account cookies to avoid logging in. Recent update replaces RP bonus with WOF bonus. FBTC_WOF.py claims the WOF bonus also every hour.

<b>Features:</b>
1. Auto Roll every hour
2. Auto Redeem points (WOF Bonus)

Insert your account’s cookies, Telegram bot token, your Telegram chatID, linux username for cronjob.
I’m running this bot on a GCP basic instance, the BTC earned from this bot covers the monthly cost.

<b>Telegram message:</b>
![](telegram_msg.png)
