#!/usr/bin/env python3
# TELEGRAM BOT â€” CUSTOM EMOJI (TERI IDs)
# Owner: @unknown_tanveer | UNKNOWNBABU 10X

import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ========== CONFIG ==========
BOT_TOKEN = "8929527790:AAEFyNqSWbqzntDZmqockyix0gbkuY5WAMA"

if not BOT_TOKEN:
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
            BOT_TOKEN = config.get("bot_token")
    except:
        BOT_TOKEN = None

if not BOT_TOKEN:
    print("âŒ BOT_TOKEN not found!")
    exit(1)

# ========== CUSTOM EMOJI IDs (TUNE BHEJI THI) ==========
EMOJI = {
    "sparkles": "6089104607328342288",      # ðŸ’°
    "check": "6089364701957853465",         # âœ…
    "crown": "6089003761496232797",         # ðŸ‘‘
    "warning": "4956611513369494230",       # âš ï¸
    "play": "4956250031741993892",          # â–¶ï¸
    "clock": "4956720180337050608",         # ðŸ•½
    "gift": "4956722293460960020",          # ðŸŽ€
    "lightning": "6087079590377820415",     # âš¡
}

# ========== EMOJI HELPER ==========
def e(name):
    emoji_id = EMOJI.get(name, EMOJI["sparkles"])
    return f'<tg-emoji emoji-id="{emoji_id}">â¬›</tg-emoji>'

def emoji_button(text, emoji_name):
    return f"{e(emoji_name)} {text}"

# ========== START ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    first_name = user.first_name

    msg = f"""
{e('sparkles')} {e('lightning')} {e('crown')} {e('sparkles')}

<b>WELCOME TO THE BOT!</b>

{e('sparkles')} Hello <b>{first_name}</b>!

{e('crown')} This is a <b>Premium Bot</b>
{e('lightning')} Owner: <b>@unknown_tanveer</b>
{e('play')} Powered by <b>UNKNOWNBABU 10X</b>

{e('check')} All emojis are <b>custom premium</b>
{e('gift')} Enjoy the experience!

{e('sparkles')} {e('lightning')} {e('crown')} {e('sparkles')}
    """

    keyboard = [
        [
            InlineKeyboardButton(
                emoji_button("Help", "warning"),
                callback_data="help"
            ),
            InlineKeyboardButton(
                emoji_button("Info", "play"),
                callback_data="info"
            )
        ],
        [
            InlineKeyboardButton(
                emoji_button("Website", "gift"),
                url="https://t.me/unknown_tanveer"
            ),
            InlineKeyboardButton(
                emoji_button("Support", "sparkles"),
                url="https://t.me/unknown_tanveer"
            )
        ],
        [
            InlineKeyboardButton(
                emoji_button("Profile", "crown"),
                callback_data="profile"
            ),
            InlineKeyboardButton(
                emoji_button("Stats", "clock"),
                callback_data="stats"
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        msg,
        parse_mode="HTML",
        reply_markup=reply_markup
    )

# ========== CALLBACK HANDLER ==========
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "help":
        msg = f"""
{e('warning')} {e('sparkles')} <b>HELP SECTION</b> {e('sparkles')} {e('warning')}

{e('check')} <b>How to use:</b>
   â€¢ Send /start
   â€¢ Use buttons below
   â€¢ Enjoy custom emojis

{e('warning')} <b>Commands:</b>
   /start â€” Welcome message
   /help â€” This help

{e('crown')} <b>Owner:</b> @unknown_tanveer
{e('lightning')} <b>Powered by:</b> UNKNOWNBABU 10X

{e('gift')} {e('play')} {e('crown')} {e('gift')}
        """
        await query.edit_message_text(msg, parse_mode="HTML")
    
    elif data == "info":
        msg = f"""
{e('play')} {e('sparkles')} <b>BOT INFO</b> {e('sparkles')} {e('play')}

{e('crown')} <b>Owner:</b> @unknown_tanveer
{e('lightning')} <b>Version:</b> 2.0
{e('clock')} <b>Status:</b> Active

{e('check')} <b>Features:</b>
   â€¢ All custom premium emojis
   â€¢ Interactive buttons
   â€¢ Fast response

{e('gift')} <b>Made with â¤ï¸ by UNKNOWNBABU 10X</b>
        """
        await query.edit_message_text(msg, parse_mode="HTML")
    
    elif data == "profile":
        user_id = query.from_user.id
        first_name = query.from_user.first_name
        
        msg = f"""
{e('crown')} {e('sparkles')} <b>YOUR PROFILE</b> {e('sparkles')} {e('crown')}

{e('crown')} <b>Name:</b> {first_name}
{e('sparkles')} <b>ID:</b> <code>{user_id}</code>
{e('check')} <b>Status:</b> Premium User
{e('gift')} <b>Emojis:</b> Custom Premium

{e('gift')} {e('play')} {e('lightning')} {e('gift')}
        """
        await query.edit_message_text(msg, parse_mode="HTML")
    
    elif data == "stats":
        msg = f"""
{e('clock')} {e('sparkles')} <b>BOT STATS</b> {e('sparkles')} {e('clock')}

{e('crown')} <b>Total Users:</b> 1,234
{e('play')} <b>Commands:</b> 3
{e('gift')} <b>Emojis:</b> 8 Custom
{e('lightning')} <b>Uptime:</b> 99.9%

{e('check')} <b>Status:</b> Running Smoothly
{e('gift')} {e('sparkles')} {e('lightning')} {e('gift')}
        """
        await query.edit_message_text(msg, parse_mode="HTML")

# ========== HELP COMMAND ==========
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = f"""
{e('warning')} {e('sparkles')} <b>HELP</b> {e('sparkles')} {e('warning')}

{e('check')} /start â€” Welcome message
{e('check')} /help â€” This help

{e('crown')} Owner: @unknown_tanveer
{e('lightning')} Powered by UNKNOWNBABU 10X
    """
    await update.message.reply_text(msg, parse_mode="HTML")

# ========== MAIN ==========
def main():
    print("""
    â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
    â•‘                                                                   â•‘
    â•‘      ðŸ”¥ CUSTOM EMOJI BOT â€” TERI IDs ðŸ”¥                           â•‘
    â•‘                                                                   â•‘
    â•‘   Owner: @unknown_tanveer | UNKNOWNBABU 10X                       â•‘
    â•‘                                                                   â•‘
    â•‘   Emoji IDs: 8 Custom Premium Emojis                             â•‘
    â•‘   Bot Token: 8929527790:AAEFyNqSWbqzntDZmqockyix0gbkuY5WAMA      â•‘
    â•‘                                                                   â•‘
    â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    """)

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(handle_callback))

    print("âœ… Bot is running with your custom emojis...")
    app.run_polling()

if __name__ == "__main__":
    main()
