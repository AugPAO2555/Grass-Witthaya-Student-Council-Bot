import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime
import requests
from dotenv import load_dotenv

# ========================
# Load ENV
# ========================
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")

print("TOKEN:", "SET" if TOKEN else "❌ NOT SET")

# ========================
# Webhook Log
# ========================
def send_log(msg):
    if WEBHOOK:
        try:
            requests.post(WEBHOOK, json={"content": msg}, timeout=5)
        except Exception as e:
            print("Webhook Error:", e)

# ========================
# Bot Setup
# ========================
POINTS_FILE = "points.json"
APPROVED = "<:approved:1370751335695126678>"
THUMBNAIL_URL = "https://cdn.discordapp.com/attachments/1369835971092156508/1484790068953481216/153_20260321124312.png"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ========================
# Data
# ========================
def load_points():
    if not os.path.exists(POINTS_FILE):
        return {}
    try:
        with open(POINTS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_points(data):
    with open(POINTS_FILE, "w") as f:
        json.dump(data, f, indent=4)

points = load_points()

# ========================
# Utils
# ========================
def is_admin(member):
    return member.guild_permissions.administrator

def now():
    return datetime.now().strftime("%d/%m/%Y %H:%M")

def embed_msg(desc, color=0x2f3136):
    embed = discord.Embed(
        title="❮ Work Points | แต้มการทำงาน ❯",
        description=desc,
        color=color
    )
    embed.set_thumbnail(url=THUMBNAIL_URL)
    embed.set_footer(text=f"ข้อมูล ณ วันที่ {now()}")
    return embed

# ========================
# EVENTS
# ========================
@bot.event
async def on_ready():
    print(f"✅ Bot online: {bot.user}")
    send_log(f"🟢 Bot ONLINE: {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"🔁 Synced {len(synced)} commands")
    except Exception as e:
        print("Sync Error:", e)

# ========================
# ERROR HANDLER (สำคัญมาก)
# ========================
@bot.event
async def on_command_error(ctx, error):
    print("ERROR:", error)
    await ctx.send("❌ เกิดข้อผิดพลาด (ดู console)")

# ========================
# POINTS
# ========================
@bot.tree.command(name="points")
async def points_slash(interaction: discord.Interaction, member: discord.Member=None):
    target = member or interaction.user
    uid = str(target.id)

    points[uid] = points.get(uid, 0)

    await interaction.response.send_message(
        embed=embed_msg(
            f"{APPROVED} | คุณ {target.mention}\n"
            f"มี {points[uid]} Work Points"
        )
    )

@bot.command()
async def points_cmd(ctx, member: discord.Member=None):
    target = member or ctx.author
    uid = str(target.id)

    points[uid] = points.get(uid, 0)

    await ctx.send(
        embed=embed_msg(
            f"{APPROVED} | คุณ {target.mention}\n"
            f"มี {points[uid]} Work Points"
        )
    )

# ========================
# ADD
# ========================
@bot.tree.command(name="add")
async def add_slash(interaction: discord.Interaction, member: discord.Member, amount: int):

    if not is_admin(interaction.user):
        return await interaction.response.send_message("❌ ไม่มีสิทธิ์", ephemeral=True)

    if amount <= 0:
        return await interaction.response.send_message("❌ จำนวนต้องมากกว่า 0", ephemeral=True)

    uid = str(member.id)
    points[uid] = points.get(uid, 0) + amount
    save_points(points)

    send_log(f"➕ {member} +{amount} โดย {interaction.user}")

    await interaction.response.send_message(
        embed=embed_msg(
            f"{APPROVED} | เพิ่ม {amount} ให้ {member.mention}\n"
            f"ตอนนี้มี {points[uid]} Work Points",
            0x2ecc71
        )
    )

@bot.command()
async def add_cmd(ctx, member: discord.Member, amount: int):

    if not is_admin(ctx.author):
        return await ctx.send("❌ ไม่มีสิทธิ์")

    if amount <= 0:
        return await ctx.send("❌ จำนวนต้องมากกว่า 0")

    uid = str(member.id)
    points[uid] = points.get(uid, 0) + amount
    save_points(points)

    send_log(f"➕ {member} +{amount} โดย {ctx.author}")

    await ctx.send(
        embed=embed_msg(
            f"{APPROVED} | เพิ่ม {amount} ให้ {member.mention}\n"
            f"ตอนนี้มี {points[uid]} Work Points",
            0x2ecc71
        )
    )

# ========================
# REMOVE
# ========================
@bot.tree.command(name="remove")
async def remove_slash(interaction: discord.Interaction, member: discord.Member, amount: int):

    if not is_admin(interaction.user):
        return await interaction.response.send_message("❌ ไม่มีสิทธิ์", ephemeral=True)

    if amount <= 0:
        return await interaction.response.send_message("❌ จำนวนต้องมากกว่า 0", ephemeral=True)

    uid = str(member.id)
    points[uid] = max(0, points.get(uid, 0) - amount)
    save_points(points)

    send_log(f"➖ {member} -{amount} โดย {interaction.user}")

    await interaction.response.send_message(
        embed=embed_msg(
            f"{APPROVED} | ลบ {amount} จาก {member.mention}\n"
            f"ตอนนี้มี {points[uid]} Work Points",
            0xe74c3c
        )
    )

@bot.command()
async def remove_cmd(ctx, member: discord.Member, amount: int):

    if not is_admin(ctx.author):
        return await ctx.send("❌ ไม่มีสิทธิ์")

    if amount <= 0:
        return await ctx.send("❌ จำนวนต้องมากกว่า 0")

    uid = str(member.id)
    points[uid] = max(0, points.get(uid, 0) - amount)
    save_points(points)

    send_log(f"➖ {member} -{amount} โดย {ctx.author}")

    await ctx.send(
        embed=embed_msg(
            f"{APPROVED} | ลบ {amount} จาก {member.mention}\n"
            f"ตอนนี้มี {points[uid]} Work Points",
            0xe74c3c
        )
    )

# ========================
# RUN
# ========================
if not TOKEN:
    print("❌ TOKEN ไม่ถูกตั้งค่า")
else:
    bot.run(TOKEN)