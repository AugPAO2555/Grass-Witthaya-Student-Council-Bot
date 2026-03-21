# main.py
import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime
from flask import Flask
from threading import Thread
import requests
from dotenv import load_dotenv

# ========================
# Load .env
# ========================
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")

# ========================
# Keep Alive (Flask)
# ========================
app = Flask('')

@app.route('/')
def health():
    return {
        "status": "online",
        "bot": str(bot.user) if 'bot' in globals() and bot.user else "starting",
        "time": datetime.now().strftime("%d/%m/%Y %H:%M")
    }

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ========================
# Webhook log
# ========================
def send_log(msg):
    if WEBHOOK:
        try:
            requests.post(WEBHOOK, json={"content": msg})
        except:
            pass

# ========================
# Bot Setup
# ========================
POINTS_FILE = "points.json"
LOG_CHANNEL_ID = 1484754409740173343
APPROVED = "<:approved:1370751335695126678>"
THUMBNAIL_URL = "https://cdn.discordapp.com/attachments/1369835971092156508/1484790068953481216/153_20260321124312.png"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# ========================
# Load/Save Points
# ========================
def load_points():
    if not os.path.exists(POINTS_FILE):
        return {}
    with open(POINTS_FILE, "r") as f:
        return json.load(f)

def save_points(data):
    with open(POINTS_FILE, "w") as f:
        json.dump(data, f)

points = load_points()

# ========================
# Permission
# ========================
def is_admin(member: discord.Member):
    if member.guild_permissions.administrator:
        return True
    allowed_roles = ["Admin", "Mod"]
    return any(role.name in allowed_roles for role in member.roles)

# ========================
# Time Helper
# ========================
def now_time():
    return datetime.now().strftime("%d/%m/%Y %H:%M")

# ========================
# Embed Helper
# ========================
def make_embed(action:str, member: discord.Member, amount: int, approve=True):
    color = 0x2ecc71 if approve else 0xe74c3c
    embed = discord.Embed(
        title="❮ Work Points | แต้มการทำงาน ❯",
        description=f"{APPROVED} | {action} {amount} Work Points {'ให้กับ' if approve else 'ออกจาก'} {member.mention} สำเร็จ !\nขณะนี้มีจำนวนแต้มทั้งหมด {points[str(member.id)]} Work Points",
        color=color
    )
    embed.set_thumbnail(url=THUMBNAIL_URL)
    embed.set_footer(text=f"ข้อมูล ณ วันที่ {now_time()}")
    return embed

# ========================
# /points & !points
# ========================
@bot.tree.command(name="points", description="ดูแต้มของสมาชิก")
@app_commands.describe(member="สมาชิก (ปล่อยว่างเพื่อดูของตัวเอง)")
async def points_cmd(interaction: discord.Interaction, member: discord.Member=None):
    target = member or interaction.user
    user_id = str(target.id)
    if user_id not in points:
        points[user_id] = 0
    embed = discord.Embed(
        title="❮ Work Points | แต้มการทำงาน ❯",
        description=f"{APPROVED} | คุณ {target.mention} !\nขณะนี้มีจำนวนแต้มทั้งหมด {points[user_id]} Work Points",
        color=0x2f3136
    )
    embed.set_footer(text=f"ข้อมูล ณ วันที่ {now_time()}")
    await interaction.response.send_message(embed=embed)

@bot.command(name="points")
async def points_prefix(ctx, member: discord.Member=None):
    await points_cmd.callback(await ctx.interaction if hasattr(ctx, "interaction") else ctx, member or ctx.author)

# ========================
# /add & !add
# ========================
async def add_points_logic(ctx_or_interaction, member: discord.Member, amount: int):
    user_check = ctx_or_interaction.user if hasattr(ctx_or_interaction, "user") else ctx_or_interaction.author
    if not is_admin(user_check):
        await (ctx_or_interaction.response.send_message if hasattr(ctx_or_interaction, "response") else ctx_or_interaction.send)(
            f"{APPROVED} | คุณไม่มีสิทธิ์ใช้คำสั่งนี้!", ephemeral=True
        )
        return
    user_id = str(member.id)
    if user_id not in points:
        points[user_id] = 0
    points[user_id] += amount
    save_points(points)
    embed = make_embed("เพิ่ม", member, amount, approve=True)
    await (ctx_or_interaction.response.send_message if hasattr(ctx_or_interaction, "response") else ctx_or_interaction.send)(embed=embed)

@bot.tree.command(name="add", description="เพิ่มแต้มให้สมาชิก")
@app_commands.describe(member="สมาชิก", amount="จำนวนแต้ม")
async def add_cmd(interaction: discord.Interaction, member: discord.Member, amount: int):
    await add_points_logic(interaction, member, amount)

@bot.command(name="add")
async def add_prefix(ctx, member: discord.Member, amount: int):
    await add_points_logic(ctx, member, amount)

# ========================
# /remove & !remove
# ========================
async def remove_points_logic(ctx_or_interaction, member: discord.Member, amount: int):
    user_check = ctx_or_interaction.user if hasattr(ctx_or_interaction, "user") else ctx_or_interaction.author
    if not is_admin(user_check):
        await (ctx_or_interaction.response.send_message if hasattr(ctx_or_interaction, "response") else ctx_or_interaction.send)(
            f"{APPROVED} | คุณไม่มีสิทธิ์ใช้คำสั่งนี้!", ephemeral=True
        )
        return
    user_id = str(member.id)
    if user_id not in points:
        points[user_id] = 0
    points[user_id] -= amount
    save_points(points)
    embed = make_embed("ลบ", member, amount, approve=False)
    await (ctx_or_interaction.response.send_message if hasattr(ctx_or_interaction, "response") else ctx_or_interaction.send)(embed=embed)

@bot.tree.command(name="remove", description="ลดแต้มสมาชิก")
@app_commands.describe(member="สมาชิก", amount="จำนวนแต้ม")
async def remove_cmd(interaction: discord.Interaction, member: discord.Member, amount: int):
    await remove_points_logic(interaction, member, amount)

@bot.command(name="remove")
async def remove_prefix(ctx, member: discord.Member, amount: int):
    await remove_points_logic(ctx, member, amount)

# ========================
# Bot Events
# ========================
@bot.event
async def on_ready():
    print(f"✅ Bot online: {bot.user}")
    send_log(f"🟢 Bot ONLINE: {bot.user}")
    await bot.tree.sync()

@bot.event
async def on_disconnect():
    print("❌ Bot disconnected")
    send_log("🔴 Bot DISCONNECTED")

@bot.event
async def on_resumed():
    print("✅ Bot reconnected")
    send_log("🟢 Bot RECONNECTED")

# ========================
# Run Bot
# ========================
keep_alive()
bot.run(TOKEN)