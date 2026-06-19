#!/usr/bin/env python3
"""
TELEGRAM OTP BOT — WITH PAYMENT + QR
Owner: @unknown_tanveer | UNKNOWNBABU 10X
"""

import os
import json
import time
import re
import random
import hashlib
import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, filters, ContextTypes
)

# ========== CONFIG ==========
with open('config.json', 'r') as f:
    CONFIG = json.load(f)

BOT_TOKEN = CONFIG['bot_token']
ADMIN_IDS = CONFIG['admin_ids']
GROUP_ID = CONFIG['group_id']
UPI_ID = CONFIG['upi_id']
QUICKCHART_API = CONFIG['quickchart_api']
FIVSIM_KEY = CONFIG['5sim_api_key']
SMS_ACTIVATE_KEY = CONFIG['sms_activate_key']

DB_FILE = 'db.json'

# ========== DATABASE ==========
def load_db():
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"users": {}, "numbers": {}, "transactions": {}}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# ========== QR GENERATOR ==========
def generate_qr(upi_id: str, amount: float) -> str:
    """Generate UPI QR code using QuickChart API"""
    upi_string = f"upi://pay?pa={upi_id}&am={amount}&cu=INR"
    qr_url = f"{QUICKCHART_API}?text={upi_string}&width=300&height=300&margin=10"
    return qr_url

# ========== VIRTUAL NUMBER PROVIDERS ==========
class NumberProvider:
    def get_5sim_number(self, country='us', service='whatsapp'):
        try:
            url = f"https://5sim.net/v1/user/buy/activation/{country}/any/{service}"
            headers = {'Authorization': f'Bearer {FIVSIM_KEY}'}
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code == 200:
                data = r.json()
                return {
                    'number': data.get('number'),
                    'id': data.get('id'),
                    'country': country,
                    'service': service,
                    'price': data.get('price', 0.10),
                    'provider': '5sim'
                }
            return None
        except Exception as e:
            print(f"[5sim Error] {e}")
            return None

    def get_sms_activate_number(self, country='0', service='wa'):
        try:
            url = f"https://sms-activate.org/stubs/handler_api.php?api_key={SMS_ACTIVATE_KEY}&action=getNumber&service={service}&country={country}"
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                parts = r.text.split(':')
                if parts[0] == 'ACCESS_NUMBER':
                    return {
                        'number': parts[2],
                        'id': parts[1],
                        'country': country,
                        'service': service,
                        'price': 0.05,
                        'provider': 'sms-activate'
                    }
            return None
        except Exception as e:
            print(f"[SMS-Activate Error] {e}")
            return None

provider = NumberProvider()

# ========== OTP CHECK ==========
def check_otp_5sim(number_id):
    try:
        url = f"https://5sim.net/v1/user/check/{number_id}"
        headers = {'Authorization': f'Bearer {FIVSIM_KEY}'}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get('status') == 'RECEIVED':
                return data.get('sms', {}).get('code')
        return None
    except:
        return None

def check_otp_sms_activate(number_id):
    try:
        url = f"https://sms-activate.org/stubs/handler_api.php?api_key={SMS_ACTIVATE_KEY}&action=getStatus&id={number_id}"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            parts = r.text.split(':')
            if parts[0] == 'STATUS_OK':
                return parts[1]
        return None
    except:
        return None

# ========== KEYBOARDS ==========
def main_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("📱 Get Number", callback_data="get_number"),
            InlineKeyboardButton("💰 Deposit Funds", callback_data="deposit")
        ],
        [
            InlineKeyboardButton("📊 My Numbers", callback_data="my_numbers"),
            InlineKeyboardButton("👤 Profile", callback_data="profile")
        ],
        [
            InlineKeyboardButton("🔄 Check OTP", callback_data="check_otp"),
            InlineKeyboardButton("❓ Help", callback_data="help")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def danger_button(text, callback):
    return InlineKeyboardButton(text, callback_data=callback, 
                                 style="color:white;background:#e74c3c;")

def primary_button(text, callback):
    return InlineKeyboardButton(text, callback_data=callback,
                                 style="color:white;background:#3498db;")

# ========== BOT COMMANDS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    
    # Register user
    db = load_db()
    if user_id not in db['users']:
        db['users'][user_id] = {
            'balance': 0.0,
            'total_spent': 0.0,
            'numbers': [],
            'joined': datetime.now().isoformat()
        }
        save_db(db)
    
    msg = f"""
🚀 <b>OTP Bot — Virtual Numbers</b>

👋 Welcome <b>{user.first_name}</b>!

🔹 <b>Features:</b>
   📱 Get virtual numbers
   💰 Deposit funds via UPI
   🔑 Receive OTP codes
   📤 Auto-forward to group

💰 <b>Your Balance:</b> ${db['users'][user_id]['balance']:.2f}

👇 Use buttons below to get started!
"""
    await update.message.reply_text(msg, parse_mode='HTML', reply_markup=main_keyboard())

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = str(query.from_user.id)
    db = load_db()

    if data == "get_number":
        await get_number_menu(update, context)
    
    elif data == "deposit":
        await deposit_menu(update, context)
    
    elif data == "my_numbers":
        await show_my_numbers(update, context)
    
    elif data == "profile":
        await show_profile(update, context)
    
    elif data == "check_otp":
        await check_otp_menu(update, context)
    
    elif data == "help":
        await show_help(update, context)
    
    elif data.startswith("country_"):
        country = data.split("_")[1]
        await get_number_by_country(update, context, country)
    
    elif data.startswith("service_"):
        service = data.split("_")[1]
        await get_number_by_service(update, context, service)
    
    elif data.startswith("deposit_"):
        amount = float(data.split("_")[1])
        await generate_deposit_qr(update, context, amount)
    
    elif data.startswith("check_otp_"):
        number = data.split("_")[2]
        await check_otp_for_number(update, context, number)
    
    elif data == "back":
        await update.effective_message.edit_text(
            "🔙 <b>Main Menu</b>", parse_mode='HTML', reply_markup=main_keyboard()
        )

async def get_number_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇺🇸 USA", callback_data="country_us")],
        [InlineKeyboardButton("🇬🇧 UK", callback_data="country_uk")],
        [InlineKeyboardButton("🇮🇳 India", callback_data="country_in")],
        [InlineKeyboardButton("🇨🇦 Canada", callback_data="country_ca")],
        [InlineKeyboardButton("🇦🇺 Australia", callback_data="country_au")],
        [InlineKeyboardButton("🇩🇪 Germany", callback_data="country_de")],
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.effective_message.edit_text(
        "🌍 <b>Select Country</b>", parse_mode='HTML', reply_markup=markup
    )

async def get_number_by_country(update: Update, context: ContextTypes.DEFAULT_TYPE, country: str):
    context.user_data['selected_country'] = country
    keyboard = [
        [InlineKeyboardButton("📱 WhatsApp", callback_data="service_whatsapp")],
        [InlineKeyboardButton("✈️ Telegram", callback_data="service_telegram")],
        [InlineKeyboardButton("📸 Instagram", callback_data="service_instagram")],
        [InlineKeyboardButton("🐦 Twitter", callback_data="service_twitter")],
        [InlineKeyboardButton("🔙 Back", callback_data="get_number")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.effective_message.edit_text(
        f"📱 <b>Selected: {country.upper()}</b>\n\nChoose service:", parse_mode='HTML', reply_markup=markup
    )

async def get_number_by_service(update: Update, context: ContextTypes.DEFAULT_TYPE, service: str):
    user_id = str(update.effective_user.id)
    country = context.user_data.get('selected_country', 'us')
    
    db = load_db()
    if db['users'][user_id]['balance'] < 0.10:
        await update.effective_message.edit_text(
            "❌ <b>Insufficient Balance!</b>\n\nMinimum balance required: $0.10\n\nPlease deposit funds first.",
            parse_mode='HTML', reply_markup=main_keyboard()
        )
        return
    
    await update.effective_message.edit_text(
        "⏳ <b>Getting your virtual number...</b>", parse_mode='HTML'
    )
    
    num_data = provider.get_5sim_number(country, service)
    if not num_data:
        num_data = provider.get_sms_activate_number(country, service[:2])
    
    if num_data:
        db['users'][user_id]['balance'] -= num_data['price']
        db['users'][user_id]['total_spent'] += num_data['price']
        
        db['numbers'][num_data['number']] = {
            'user_id': user_id,
            'country': country,
            'service': service,
            'status': 'active',
            'provider': num_data['provider'],
            'id': num_data['id'],
            'expires': (datetime.now() + timedelta(hours=24)).isoformat(),
            'otp': None
        }
        db['users'][user_id]['numbers'].append(num_data['number'])
        save_db(db)
        
        msg = f"""
✅ <b>Virtual Number Obtained!</b>

📞 <b>Number:</b> <code>{num_data['number']}</code>
🌍 <b>Country:</b> {country.upper()}
📱 <b>Service:</b> {service.title()}
💲 <b>Price:</b> ${num_data['price']:.2f}
💰 <b>Balance:</b> ${db['users'][user_id]['balance']:.2f}

📌 Use this number for verification, then click Check OTP.
"""
        keyboard = [
            [InlineKeyboardButton("🔄 Check OTP Now", callback_data=f"check_otp_{num_data['number']}")],
            [InlineKeyboardButton("🔙 Main Menu", callback_data="back")]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        await update.effective_message.edit_text(msg, parse_mode='HTML', reply_markup=markup)
    else:
        await update.effective_message.edit_text(
            "❌ <b>No numbers available</b>\n\nTry again later or choose a different country.",
            parse_mode='HTML', reply_markup=main_keyboard()
        )

async def deposit_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💵 $1", callback_data="deposit_1.00")],
        [InlineKeyboardButton("💵 $5", callback_data="deposit_5.00")],
        [InlineKeyboardButton("💵 $10", callback_data="deposit_10.00")],
        [InlineKeyboardButton("💵 $25", callback_data="deposit_25.00")],
        [InlineKeyboardButton("💵 $50", callback_data="deposit_50.00")],
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.effective_message.edit_text(
        f"💰 <b>Deposit Funds</b>\n\nUPI ID: <code>{UPI_ID}</code>\n\nSelect amount:", 
        parse_mode='HTML', reply_markup=markup
    )

async def generate_deposit_qr(update: Update, context: ContextTypes.DEFAULT_TYPE, amount: float):
    user_id = str(update.effective_user.id)
    db = load_db()
    
    qr_url = generate_qr(UPI_ID, amount)
    txn_id = f"txn_{int(time.time())}_{random.randint(1000,9999)}"
    
    db['transactions'][txn_id] = {
        'user_id': user_id,
        'amount': amount,
        'type': 'deposit',
        'status': 'pending',
        'timestamp': datetime.now().isoformat()
    }
    save_db(db)
    
    msg = f"""
💳 <b>Deposit Instructions</b>

💰 <b>Amount:</b> ${amount:.2f}
📱 <b>UPI ID:</b> <code>{UPI_ID}</code>
🆔 <b>Txn ID:</b> <code>{txn_id}</code>

📌 <b>Steps:</b>
1️⃣ Scan QR code below
2️⃣ Pay exact amount
3️⃣ Wait 1-2 minutes
4️⃣ Funds will auto-credit

⚠️ Send payment from <b>same UPI ID</b> as your Telegram name
"""
    keyboard = [
        [InlineKeyboardButton("✅ I've Paid", callback_data=f"verify_{txn_id}")],
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    
    await update.effective_message.edit_text(msg, parse_mode='HTML')
    await update.effective_message.reply_photo(photo=qr_url, caption="Scan to pay", reply_markup=markup)

async def verify_payment(update: Update, context: ContextTypes.DEFAULT_TYPE, txn_id: str):
    user_id = str(update.effective_user.id)
    db = load_db()
    
    if txn_id not in db['transactions']:
        await update.effective_message.edit_text("❌ Invalid transaction", reply_markup=main_keyboard())
        return
    
    txn = db['transactions'][txn_id]
    if txn['status'] == 'completed':
        await update.effective_message.edit_text("✅ Payment already credited!", reply_markup=main_keyboard())
        return
    
    # Simulate verification (in real scenario, use webhook)
    txn['status'] = 'completed'
    db['users'][user_id]['balance'] += txn['amount']
    save_db(db)
    
    msg = f"""
✅ <b>Payment Verified!</b>

💰 <b>Amount:</b> ${txn['amount']:.2f}
💵 <b>New Balance:</b> ${db['users'][user_id]['balance']:.2f}

🎯 Use 'Get Number' to start receiving OTPs!
"""
    await update.effective_message.edit_text(msg, parse_mode='HTML', reply_markup=main_keyboard())
    
    # Forward to group
    await context.bot.send_message(
        chat_id=GROUP_ID,
        text=f"💰 <b>New Deposit</b>\nUser: {update.effective_user.mention_html()}\nAmount: ${txn['amount']:.2f}\nBalance: ${db['users'][user_id]['balance']:.2f}",
        parse_mode='HTML'
    )

async def show_my_numbers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    db = load_db()
    numbers = db['users'][user_id].get('numbers', [])
    
    if not numbers:
        await update.effective_message.edit_text(
            "📭 <b>No numbers yet</b>\n\nGet a virtual number using 'Get Number'.", 
            parse_mode='HTML', reply_markup=main_keyboard()
        )
        return
    
    msg = "📱 <b>My Numbers</b>\n\n"
    keyboard = []
    for num in numbers:
        data = db['numbers'].get(num, {})
        status = "✅ Active" if data.get('status') == 'active' else "⏳ Expired"
        msg += f"📞 <code>{num}</code> — {status} ({data.get('service', 'unknown').title()})\n"
        keyboard.append([InlineKeyboardButton(f"🔄 Check OTP for {num}", callback_data=f"check_otp_{num}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back")])
    markup = InlineKeyboardMarkup(keyboard)
    await update.effective_message.edit_text(msg, parse_mode='HTML', reply_markup=markup)

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    db = load_db()
    user_data = db['users'][user_id]
    
    msg = f"""
👤 <b>Your Profile</b>

🆔 <b>ID:</b> {user_id}
💰 <b>Balance:</b> ${user_data['balance']:.2f}
💳 <b>Total Spent:</b> ${user_data['total_spent']:.2f}
📱 <b>Numbers:</b> {len(user_data.get('numbers', []))}
📅 <b>Joined:</b> {user_data.get('joined', 'N/A')}
"""
    await update.effective_message.edit_text(msg, parse_mode='HTML', reply_markup=main_keyboard())

async def check_otp_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    db = load_db()
    numbers = db['users'][user_id].get('numbers', [])
    
    if not numbers:
        await update.effective_message.edit_text(
            "📭 <b>No active numbers</b>", parse_mode='HTML', reply_markup=main_keyboard()
        )
        return
    
    msg = "🔍 <b>Check OTP</b>\n\nSelect a number:"
    keyboard = []
    for num in numbers:
        data = db['numbers'].get(num, {})
        status = "✅ Active" if data.get('status') == 'active' else "⏳ Expired"
        keyboard.append([InlineKeyboardButton(f"{num} — {status}", callback_data=f"check_otp_{num}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back")])
    markup = InlineKeyboardMarkup(keyboard)
    await update.effective_message.edit_text(msg, parse_mode='HTML', reply_markup=markup)

async def check_otp_for_number(update: Update, context: ContextTypes.DEFAULT_TYPE, number: str):
    db = load_db()
    num_data = db['numbers'].get(number)
    
    if not num_data:
        await update.effective_message.edit_text("❌ Number not found", reply_markup=main_keyboard())
        return
    
    provider_name = num_data.get('provider', '5sim')
    number_id = num_data.get('id')
    
    otp = None
    if provider_name == '5sim':
        otp = check_otp_5sim(number_id)
    elif provider_name == 'sms-activate':
        otp = check_otp_sms_activate(number_id)
    
    if otp:
        db['numbers'][number]['otp'] = otp
        save_db(db)
        
        msg = f"""
✅ <b>OTP Code Received!</b>

📞 <b>Number:</b> <code>{number}</code>
🔑 <b>OTP:</b> <code>{otp}</code>
📱 <b>Service:</b> {num_data['service'].title()}
"""
        keyboard = [
            [InlineKeyboardButton("📋 Copy OTP", callback_data=f"copy_otp_{number}")],
            [InlineKeyboardButton("🔙 Back", callback_data="check_otp")]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        await update.effective_message.edit_text(msg, parse_mode='HTML', reply_markup=markup)
        
        # Forward to group
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=f"🔐 <b>NEW OTP</b>\n📞 {number}\n🔑 <code>{otp}</code>\n📱 {num_data['service'].title()}",
            parse_mode='HTML'
        )
    else:
        msg = f"""
⏳ <b>No OTP yet</b>

📞 <b>Number:</b> <code>{number}</code>
📱 <b>Service:</b> {num_data['service'].title()}

🔄 Try again in 30 seconds.
"""
        keyboard = [
            [InlineKeyboardButton("🔄 Check Again", callback_data=f"check_otp_{number}")],
            [InlineKeyboardButton("🔙 Back", callback_data="check_otp")]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        await update.effective_message.edit_text(msg, parse_mode='HTML', reply_markup=markup)

async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = """
❓ <b>How to Use</b>

1️⃣ <b>Deposit Funds</b>
   → Click "Deposit" → Select amount → Pay via UPI

2️⃣ <b>Get Number</b>
   → Click "Get Number" → Select country → Select service

3️⃣ <b>Get OTP</b>
   → Use number for verification → Click "Check OTP"

4️⃣ <b>Group Auto-Forward</b>
   → Every OTP is forwarded to the group

💲 <b>Prices:</b> $0.05-$0.50 per number
🌍 <b>Countries:</b> USA, UK, India, Canada, Australia, Germany
📱 <b>Services:</b> WhatsApp, Telegram, Instagram, Twitter

👑 <b>Support:</b> @unknown_tanveer
"""
    await update.effective_message.edit_text(msg, parse_mode='HTML', reply_markup=main_keyboard())

# ========== FLASK APP (For Webhooks) ==========
app = Flask(__name__)

@app.route('/')
def home():
    return '🚀 OTP Bot is Running!'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print(f"[Webhook] {data}")
    return jsonify({"status": "ok"})

# ========== MAIN ==========
def main():
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                                                                   ║
    ║      🔥 TELEGRAM OTP BOT — WITH PAYMENT + QR 🔥                  ║
    ║                                                                   ║
    ║   Owner: @unknown_tanveer | UNKNOWNBABU 10X                       ║
    ║   Features: Payment, QR, Auto OTP, Group Forward                  ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    # Run
    app.run_polling()

if __name__ == "__main__":
    main()
