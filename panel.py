import asyncio
import json
import os
import random
import time
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import logging

# ---------------------------
# CONFIG
# ---------------------------
TOKENS_FILE = "tokens.txt"
TOKENS = []
if os.path.exists(TOKENS_FILE):
    with open(TOKENS_FILE, "r") as f:
        TOKENS = [line.strip() for line in f if line.strip()]
    if not TOKENS:
        print("⚠️ tokens.txt is empty. Please add at least one token.")
        exit(1)
else:
    print(f"❌ {TOKENS_FILE} not found. Create it with one token per line.")
    exit(1)

OWNER_ID = 6241108918
SUDO_FILE = "sudo.json"

# ---------------------------
# RAID TEXTS
# ---------------------------
RAID_TEXTS = [
    "Kya kehrha teri maa randy 😂😂🔥",
    "ꪶ  𝗟𝗨𝗡 𝗧𝗘 𝗩𝗔𝗝 ꪻ♡😂👏🏻",
    "𝘾𝙃𝙐𝙋 𝙏𝙀𝙍𝙄 𝘽𝘼𝙃𝙀𝙉 𝙆𝙄 बोस्𝘿𝙞🤢",
    "Tmkc pe chppl hi chppl marunga !!🔥😂🩴",
    "TERI MAAA RANDIII CHUPPP BANKLODE 🔥🔥👍🏻",
    "Cusmudai wala moment enjoy kr apna 🤢😂😂🤢🤢🥱💘💘😂😂💘",
    "तेरी बहन का भोसड़ा 😂🤸🏻‍♂️😂🤸🏻‍♂️😂🤸🏻‍♂️😂🤸🏻‍♂️",
    "Teri ma ko चोदू  ghachar ghachar 😂⚡️😂⚡️😂⚡️😂⚡️😎😎👌👌🏼🙏🏼🤣🗿🙏🏼🤣🗿🙏🏼🗿🗿",
    "𝙏𝙚𝙧𝙞 𝙢𝙖𝙖 𝙠𝙚 𝙗𝙝𝙤𝙨𝙙𝙚 𝙢𝙚 𝙡𝙖𝙩 𝙥𝙙𝙚𝙣𝙜𝙚 𝙗𝙝𝙤𝙩 𝙩𝙚𝙯 👻 😂👯😂👯😂👯 😂👯😂👯😂👯 😂👯😂👯😂👯",
    "🩴Le teri ma ke bhosde m chappal fasadi ab nikalke dikha😹💪🏿",
    "Sᴜɴ ᵃᵍᵃʳ ᴛᴇʀɪ माँ ᴄʜᴏᴅᴜ ᴛᴏ कोई ʀᴏᴋʟᴇɢᴀ क्या mujhe ? 🤔🔥",     
    "𝙉𝙀𝙆𝘼𝘼𝘼𝙇 𝙈𝘼𝘿𝘼𝘼𝙍𝘾𝙃𝘿👍🏼👍🏼👍🏼👍🏼👍🏼",
    "Cʜʟ🦧🔥 Tᴇʀɪ 🦧🔥Mᴀᴀ 🦧🔥Rɴᴅɪ 🔥🦧",
    "Tri bhn ki cht me tata ratan ayega neno lekr 🚙🔥🚙🔥🚙🔥",
    "Nepal 🇳🇵se lekar japan 🇯🇵 tak तेरी 𝙧𝙖𝙣𝙙𝙞 माँ 𝙠𝙚 𝙠𝙞𝙨𝙨𝙚𝙮 मशहूर है 😂🔥😂🔥",
    "𝘢𝘣𝘦 𝘩𝘢𝘵𝘵 सस्ती Rᴀɴᴅɪ ᴋᴀ काला 𝘉𝘢𝘤𝘤𝘩𝘢🤢",
    "𝘿𝙐𝘽𝙄 𝘿𝙐𝘽𝙄 𝘿𝘼𝙋𝙋 𝘿𝘼𝙋𝙋 👶🏻 𝙏𝙀𝙍𝙄 𝘽𝙃𝙀𝙉 𝘾𝙊𝘿𝙀𝙉𝙂𝙀 𝙂𝘼𝙋𝙋 𝙂𝘼𝙋𝙋 🤤😂😹🔥",
    "𝙏𝙀𝙍𝙄 𝙍𝘼𝙉𝘿𝙄  𝙈𝘼𝘼 𝙆𝙄 𝘾𝙃𝙊𝙊𝙏 𝘽𝘼𝙅𝘼𝙐🥁🔥🥁🔥🥁🔥🥁🔥",
    "ᴜɴ ᵃᵍᵃʳ ᴛᴇʀɪ माँ ᴄʜᴏᴅᴜ ᴛᴏ कोई ʀᴏᴋʟᴇɢᴀ क्या mujhe ? 🤔🔥",
    "teri maa chudte time roti h aur ghr Jake soti h😂🩷🔥😂🩷🔥😂🩷🔥🔥",
    "Kaan kholke sunn 👂🏻👂🏻👂🏻👂🏻👂🏻👂🏻 तेरी माँ महा रंडी है 😂😂😂🔥🔥🔥",
    "इधर 🤢 आ tujhe cp फ़ाइटर banau Langdi रंडीके 🤢 chuda😂🔥कमजोर pillla🎀",
    "Tmkc pe chppl hi chppl marunga !!🔥😂🩴",
    "abe mere lode se utar ja 😹😹",
    "𝗚𝗖 𝗟𝗘𝗔𝗩𝗘 𝗟𝗘 𝗥𝗔𝗡𝗗𝗜 𝗕𝗔𝗟𝗔🤭🥻🤭🥻🤭🥻",
    "𝐂ʜʟ 𝐇ᴀʀᴍᴢᴀᴅ𝐈 𝐊ᴇ लड़के 💛🤍🩵",
    "teri ma chodunga patak patak ke 🤣🤙🏻🔥",
    "Apki बातें sunke lgta h apki माँ bhot बड़ी रंडी h👍🏻👍🏻 😹😹🔥🔥🖕🏻🖕🏻",
    "𝙄𝙉𝘿𝙄𝘼 𝙄𝙎 𝙈𝙔 𝘾𝙊𝙐𝙉𝙏𝙍𝙔 🇮🇳🇮🇳𝘼𝙉𝘿 𝘼𝙇𝙇 𝙄🇳𝘿𝙄𝘼𝙉𝙎 𝙁𝘾𝙆𝙄𝙉𝙂 𝙔𝙊𝙐𝙍 𝙈𝙊𝙏𝙃𝙀𝙍 𝙅𝙊𝙍 𝙎𝙀 𝘼𝙃 𝘼𝙃 𝘼𝙃 😇😇😇😇",
    "घिनौनी रण्डी के बच्चे उड़ कबूतर मादार चोद 🗿🖕🏻तू बात बात पर अपनी मां क्यों चूदवाता ह 🤔🤔",
    "This message couldn't be displayed on your device because तेरी मां टकली रांड.",
    "तेरी मां ki ¢hut ka ₹239 ka recharge karke saare रात unlimited चोदूंगा dost 🥴🥴👅👅👅💨💨😘",
    "𝙏𝙚𝙧𝙞 𝙢𝙖𝙖 𝙠𝙚 𝙗𝙝𝙤𝙨𝙙𝙚 𝙢𝙚 𝙡𝙖𝙩 𝙥𝙙𝙚𝙣𝙜𝙚 𝙗𝙝𝙤𝙩 𝙩𝙚𝙯 👻 😂👯😂👯😂👯 😂👯😂👯😂👯 😂👯😂👯😂👯",
    "Teri maa ko neechi jaati ke dalito ka kaala lund chuswake randi ki izzat neelam krdu 😝👌🏻",
    "teri ma chudgyi balle balle 😃🔥😃🔥🤣🔥🤣",
    "ये 𝙎𝙇𝙄𝘿𝙀 करके तू 𝘼𝙋𝙉𝙄 मां नहीं Bᴀᴄʜ𝐀 पाएगा ~ 🤪👌🏻",
    "ᗷOOᖇ ᖴᗩTGYᗩ  KYᗩ Tᑌᗰᕼᗩᖇᗩ😹😹🤡👉🏻👌🏻 🤤🤤🤤",
    "𝙏𝙪𝙟𝙚 𝙘𝙪𝙙𝙣𝙚 𝙢 𝙠𝙤𝙞 𝙣𝙞 𝙝𝙖𝙧𝙖 𝙨𝙠𝙩𝙖 🥇𝙡𝙚 𝙢𝙚𝙙𝙖𝙡 𝙤𝙧 𝙘𝙝𝙡𝙩𝙖 𝙗𝙣",
    "𝘼𝙖𝙟 𝙠𝙞 𝙍𝙖𝙖𝙩 𝙏𝙚𝙧𝙞 𝙢𝙖𝙖 𝙢𝙚𝙧𝙚 𝙨𝙖𝙩𝙝 😁😁👯",
    "𝙏𝙚𝙧𝙞 𝙢𝙖𝙖 𝙠𝙝𝙖𝙮𝙚 𝙛𝙧𝙞𝙚𝙙 𝙧𝙞𝙘𝙚 𝙘𝙝𝙪𝙙𝙠𝙚 𝗯𝙤𝙡𝙚 𝙬𝙤𝙬 𝙣𝙞𝙘𝙚 🤣🤣🤣🔪🔪",
    "𝙏𝙚𝙧𝙞 𝙢𝙖 𝙠𝙚 𝙘𝙝𝙪𝙩 𝙠𝙞 𝙝𝙖𝙙𝙙𝙞 𝙩𝙤𝙙 𝙙𝙪𝙣𝙜𝙖 𝙗𝙖𝙘𝙝𝙖 𝙥𝙖𝙞𝙙𝙖 𝙠𝙧𝙣𝙖 𝙗𝙝𝙪𝙡 𝙟𝙖𝙮𝙚𝙜𝙞 😂😂"
]

# ---------------------------
# NCEMO EMOJIS
# ---------------------------
NCEMO_EMOJIS = [
    "😋","😝","😜","🤪","😑","🤫","🤭","🥱","🤗","😡","😠","😤",
    "😮‍💨","🙄","😒","🥶","🥵","🤢","😎","🥸",
    "😹","💫","😼","😽","🙀","😿","😾",
    "🙈","🙉","🙊",
    "⭐","🕣","✨","⚡","💥","💨",
    "💛","💙","💜","🤎","🤍","💘","💝"
]

# ---------------------------
# GLOBAL STATE
# ---------------------------
if os.path.exists(SUDO_FILE):
    try:
        with open(SUDO_FILE, "r") as f:
            _loaded = json.load(f)
            SUDO_USERS = set(int(x) for x in _loaded)
    except Exception:
        SUDO_USERS = {OWNER_ID}
else:
    SUDO_USERS = {OWNER_ID}
with open(SUDO_FILE, "w") as f: json.dump(list(SUDO_USERS), f)

def save_sudo():
    with open(SUDO_FILE, "w") as f: json.dump(list(SUDO_USERS), f)

group_tasks = {}         
slide_targets = set()    
slayspam_targets = set()
slay_mode = {}
apps, bots = [], []
delay = 0.1

logging.basicConfig(level=logging.INFO)

# ---------------------------
# FLASK WEB APP (KILLER DASHBOARD)
# ---------------------------
app_flask = Flask(__name__)

@app_flask.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ADHARMI BOTS - Control Center</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                background-color: #0b0b0b;
                color: #ffffff;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                overflow: hidden;
            }
            .container {
                text-align: center;
                background: rgba(20, 20, 20, 0.85);
                border: 2px solid #ff1e1e;
                padding: 40px 60px;
                border-radius: 20px;
                box-shadow: 0 0 30px rgba(255, 30, 30, 0.4);
            }
            h1 {
                font-family: 'Georgia', serif;
                font-size: 2.8rem;
                font-weight: 900;
                font-style: italic;
                color: #ff3333;
                text-shadow: 0 0 15px rgba(255, 0, 0, 0.8);
                letter-spacing: 2px;
                margin-bottom: 25px;
            }
            /* Red Rotating Chakra */
            .chakra-loader {
                width: 90px;
                height: 90px;
                border: 6px dashed #ff1e1e;
                border-top: 6px solid transparent;
                border-radius: 50%;
                margin: 0 auto 25px auto;
                animation: spin 1.2s linear infinite;
                box-shadow: 0 0 20px rgba(255, 0, 0, 0.6);
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .status {
                font-size: 1.1rem;
                color: #00ff66;
                font-weight: bold;
                letter-spacing: 1px;
                background: rgba(0, 255, 102, 0.1);
                padding: 8px 15px;
                border-radius: 8px;
                display: inline-block;
                border: 1px solid rgba(0, 255, 102, 0.3);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="chakra-loader"></div>
            <h1><i>ADHARMI BOTS ARE SLAYING</i></h1>
            <div class="status">⚡ Status: Live & Active (24/7 Running)</div>
        </div>
    </body>
    </html>
    """

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app_flask.run(host="0.0.0.0", port=port)

# ---------------------------
# DECORATORS
# ---------------------------
def only_sudo(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id
        if uid not in SUDO_USERS:
            return await update.message.reply_text("❌ You are not ADMIN.")
        return await func(update, context)
    return wrapper

def only_owner(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id
        if uid != OWNER_ID:
            return await update.message.reply_text("❌ Only Rᴇʜᴀɴ can do this.")
        return await func(update, context)
    return wrapper

# ---------------------------
# LOOP FUNCTION
# ---------------------------
async def bot_loop(bot, chat_id, base, mode):
    i = 0
    while True:
        try:
            if mode == "raid":
                text = f"{base} {RAID_TEXTS[i % len(RAID_TEXTS)]}"
            else:
                text = f"{base} {NCEMO_EMOJIS[i % len(NCEMO_EMOJIS)]}"
            await bot.set_chat_title(chat_id, text)
            i += 1
            await asyncio.sleep(delay)
        except Exception as e:
            print(f"[WARN] Bot error in chat {chat_id}: {e}")
            await asyncio.sleep(2)

# ---------------------------
# COMMANDS
# ---------------------------
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("welcome to the kazz slay bot⋆ 𝜗᭪!\nUse /assist to see all commands.")

async def assist_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Rᴇʜᴀɴ Sʟᴀʏ Bᴏᴛ Mᴇɴᴜ⋆ 𝜗᭪\n\n"
        "ɢʀᴏᴜᴘ ʀᴇɴᴀᴍᴇ:\n"
        "/gcnc <text>\n/ncemo <text>\n/pausegcnc\n/pauseall\n/delay <sec>\n/condition\n\n"
        "ꜱʟᴀʏ:\n"
        "/slayfire (reply)\n/slayend (reply)\n/slayspam (reply)\n/slayendspam (reply)\n\n"
        "ꜱʟᴀʏ ᴍᴏᴅᴇ:\n"
        "/slay <name>\n/stopslay\n\n"
        "ᴀᴅᴍɪɴ ᴍᴏᴅᴇ:\n"
        "/addadmin (reply)\n/deladmin (reply)\n/adminlist\n\n"
        "ᴜꜱᴇʀꜱ:\n/myid\n/ping"
    )

async def ping_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.time()
    msg = await update.message.reply_text("🏓 Pinging...")
    end_time = time.time()
    latency = int((end_time - start_time) * 1000)
    await msg.edit_text(f"🏓 Pong! ✅ {latency} ms")

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🆔 Your ID: {update.effective_user.id}")

# --- GC Loops ---
@only_sudo
async def gcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("⚠️ Usage: /gcnc <text>")
    base = " ".join(context.args)
    chat_id = update.message.chat_id
    group_tasks.setdefault(chat_id, {})
    for bot in bots:
        if bot.id not in group_tasks[chat_id]:
            task = asyncio.create_task(bot_loop(bot, chat_id, base, "raid"))
            group_tasks[chat_id][bot.id] = task
    await update.message.reply_text("🔄 GC name loop started with raid texts.")

@only_sudo
async def ncemo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("⚠️ Usage: /ncemo <text>")
    base = " ".join(context.args)
    chat_id = update.message.chat_id
    group_tasks.setdefault(chat_id, {})
    for bot in bots:
        if bot.id not in group_tasks[chat_id]:
            task = asyncio.create_task(bot_loop(bot, chat_id, base, "emoji"))
            group_tasks[chat_id][bot.id] = task
    await update.message.reply_text("🔄 Emoji loop started with all bots.")

@only_sudo
async def pausegcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in group_tasks:
        for task in group_tasks[chat_id].values():
            task.cancel()
        group_tasks[chat_id] = {}
        await update.message.reply_text("⏹ Loop stopped in this GC.")

@only_sudo
async def pauseall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for chat_id in list(group_tasks.keys()):
        for task in group_tasks[chat_id].values():
            task.cancel()
        group_tasks[chat_id] = {}
    await update.message.reply_text("⏹ All loops stopped.")

@only_sudo
async def delay_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global delay
    if not context.args: return await update.message.reply_text(f"⏱ Current delay: {delay}s")
    try:
        delay = max(0.5, float(context.args[0]))
        await update.message.reply_text(f"✅ Delay set to {delay}s")
    except: await update.message.reply_text("⚠️ Invalid number.")

@only_sudo
async def condition_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "📊 Active Loops:\n"
    for chat_id, tasks in group_tasks.items():
        msg += f"Chat {chat_id}: {len(tasks)} bots running\n"
    await update.message.reply_text(msg)

# --- SUDO ---
@only_owner
async def addadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        uid = update.message.reply_to_message.from_user.id
        SUDO_USERS.add(uid); save_sudo()
        await update.message.reply_text(f"✅ {uid} added as sudo.")

@only_owner
async def deladmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        uid = update.message.reply_to_message.from_user.id
        if uid in SUDO_USERS:
            SUDO_USERS.remove(uid); save_sudo()
            await update.message.reply_text(f"🗑 {uid} removed from sudo.")

@only_sudo
async def adminlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👑 SUDO USERS:\n" + "\n".join(map(str, SUDO_USERS)))

# --- Slide / Spam / slay ---
@only_sudo
async def slayfire(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        slide_targets.add(update.message.reply_to_message.from_user.id)
        await update.message.reply_text("Target to slay added.")

@only_sudo
async def slayend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        uid = update.message.reply_to_message.from_user.id
        slide_targets.discard(uid)
        await update.message.reply_text("🛑 Target slay stopped.")

@only_sudo
async def slayspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        slayspam_targets.add(update.message.reply_to_message.from_user.id)
        await update.message.reply_text("💥 Slay spam started.")

@only_sudo
async def slayendspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        slayspam_targets.discard(update.message.reply_to_message.from_user.id)
        await update.message.reply_text("🛑 slay spam stopped.")

@only_sudo
async def slay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("⚠️ Usage: /slay <name>")
    slay_mode[update.message.chat_id] = " ".join(context.args)
    await update.message.reply_text(f"⚡ slay mode ON with name: {slay_mode[update.message.chat_id]}")

@only_sudo
async def stopslay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    slay_mode.pop(update.message.chat_id, None)
    await update.message.reply_text("🛑 slay mode stopped.")

# --- Auto Replies ---
async def auto_replies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid, chat_id = update.message.from_user.id, update.message.chat_id
    if uid in slide_targets:
        for text in RAID_TEXTS: await update.message.reply_text(text)
    if uid in slayspam_targets:
        for text in RAID_TEXTS: await update.message.reply_text(text)
    if chat_id in slay_mode:
        for text in RAID_TEXTS: await update.message.reply_text(f"{slay_mode[chat_id]} {text}")

# ---------------------------
# BUILD APP & RUN
# ---------------------------
def build_app(token):
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("assist", assist_cmd))
    app.add_handler(CommandHandler("ping", ping_cmd))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CommandHandler("gcnc", gcnc))
    app.add_handler(CommandHandler("ncemo", ncemo))
    app.add_handler(CommandHandler("pausegcnc", pausegcnc))
    app.add_handler(CommandHandler("pauseall", pauseall))
    app.add_handler(CommandHandler("delay", delay_cmd))
    app.add_handler(CommandHandler("condition", condition_cmd))
    app.add_handler(CommandHandler("addadmin", addadmin))
    app.add_handler(CommandHandler("deladmin", deladmin))
    app.add_handler(CommandHandler("adminlist", adminlist))
    app.add_handler(CommandHandler("slayfire", slayfire))
    app.add_handler(CommandHandler("slayend", slayend))
    app.add_handler(CommandHandler("slayspam", slayspam))
    app.add_handler(CommandHandler("slayendspam", slayendspam))
    app.add_handler(CommandHandler("slay", slay))
    app.add_handler(CommandHandler("stopslay", stopslay))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_replies))
    return app

async def run_all_bots():
    global apps, bots
    for token in TOKENS:
        if token.strip():
            try:
                app = build_app(token)
                apps.append(app); bots.append(app.bot)
            except Exception as e:
                print("Failed building app:", e)

    for app in apps:
        try:
            await app.initialize(); await app.start(); await app.updater.start_polling()
        except Exception as e:
            print("Failed starting app:", e)

    print("Rᴇʜᴀɴ ʙᴏᴛꜱ ᴀʀᴇ ʀᴇᴀᴅʏ ᴛO ꜱʟᴀʏ (all bots started).")
    await asyncio.Event().wait()

if __name__ == "__main__":
    # Start Flask Web Server in a separate background thread (for Enzoic / Render / Koyeb web service mapping)
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Run Telegram Bots via Asyncio Loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_all_bots())
