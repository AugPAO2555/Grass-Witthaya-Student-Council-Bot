import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

TOKEN = os.getenv("DISCORD_TOKEN")

POINTS_FILE = "points.json"
LOG_CHANNEL_ID = 1475448056160849971

APPROVED = "<:approved:1370751335695126678>"
WAITING = "<:Waiting_for_approved:1370752766183735306>"
DENIED = "<:denied:1370751020845764671>"

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# ========================
# โหลดข้อมูลแต้ม
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
# permission
# ========================

def is_admin(member: discord.Member):
    if member.guild_permissions.administrator:
        return True

    allowed_roles = ["Admin", "Mod"]
    return any(role.name in allowed_roles for role in member.roles)

# ========================
# เวลา
# ========================

def now_time():
    return datetime.now().strftime("%d/%m/%Y %H:%M")

# ========================
# Bot Ready
# ========================

@bot.event
async def on_ready():
    print(f"Bot online: {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

# ========================
# /points ดูแต้ม
# ========================

@bot.tree.command(name="points", description="ดูแต้มของสมาชิก")
@app_commands.describe(member="สมาชิกที่ต้องการดู")
async def points_cmd(interaction: discord.Interaction, member: discord.Member):

    user_id = str(member.id)

    if user_id not in points:
        points[user_id] = 0

    embed = discord.Embed(
        description=f"{APPROVED} | {member.mention} มี **{points[user_id]} แต้ม**",
        color=0x2f3136
    )

    embed.set_author(
        name="Work Points | แต้มการทำงาน"
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    embed.set_footer(
        text=f"Reborn | Grass Witthaya Student Council | {now_time()}"
    )

    await interaction.response.send_message(embed=embed)

# ========================
# /add เพิ่มแต้ม
# ========================

@bot.tree.command(name="add", description="เพิ่มแต้มให้สมาชิก")
@app_commands.describe(member="สมาชิก", amount="จำนวนแต้ม")
async def add_points(interaction: discord.Interaction, member: discord.Member, amount: int):

    if not is_admin(interaction.user):
        await interaction.response.send_message(
            f"{DENIED} | You don't have permission to run this command!",
            ephemeral=True
        )
        return

    user_id = str(member.id)

    if user_id not in points:
        points[user_id] = 0

    points[user_id] += amount
    save_points(points)

    embed = discord.Embed(
        description=f"{APPROVED} | เพิ่ม **{amount} แต้ม** ให้ {member.mention}",
        color=0x2ecc71
    )

    embed.set_author(
        name="Work Points | แต้มการทำงาน"
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    embed.set_footer(
        text=f"Reborn | Grass Witthaya Student Council | {now_time()}"
    )

    await interaction.response.send_message(embed=embed)

    log = bot.get_channel(LOG_CHANNEL_ID)

    if log:
        log_embed = discord.Embed(
            description=f"""
{APPROVED} | Point Update

Admin : {interaction.user.mention}
Target : {member.mention}
Points : +{amount}

Current Points : {points[user_id]}
""",
            color=0x2ecc71
        )

        log_embed.set_thumbnail(url=member.display_avatar.url)

        log_embed.set_footer(
            text=f"Reborn | Grass Witthaya Student Council | {now_time()}"
        )

        await log.send(embed=log_embed)

# ========================
# /remove ลดแต้ม
# ========================

@bot.tree.command(name="remove", description="ลดแต้มสมาชิก")
@app_commands.describe(member="สมาชิก", amount="จำนวนแต้ม")
async def remove_points(interaction: discord.Interaction, member: discord.Member, amount: int):

    if not is_admin(interaction.user):
        await interaction.response.send_message(
            f"{DENIED} | You don't have permission to run this command!",
            ephemeral=True
        )
        return

    user_id = str(member.id)

    if user_id not in points:
        points[user_id] = 0

    points[user_id] -= amount
    save_points(points)

    embed = discord.Embed(
        description=f"{APPROVED} | ลด **{amount} แต้ม** จาก {member.mention}",
        color=0xe74c3c
    )

    embed.set_author(
        name="Work Points | แต้มการทำงาน"
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    embed.set_footer(
        text=f"Reborn | Grass Witthaya Student Council | {now_time()}"
    )

    await interaction.response.send_message(embed=embed)

    log = bot.get_channel(LOG_CHANNEL_ID)

    if log:
        log_embed = discord.Embed(
            description=f"""
{APPROVED} | Point Update

Admin : {interaction.user.mention}
Target : {member.mention}
Points : -{amount}

Current Points : {points[user_id]}
""",
            color=0xe74c3c
        )

        log_embed.set_thumbnail(url=member.display_avatar.url)

        log_embed.set_footer(
            text=f"Reborn | Grass Witthaya Student Council | {now_time()}"
        )

        await log.send(embed=log_embed)

# ========================
# Run Bot
# ========================

bot.run(TOKEN)