import discord
from discord.ext import commands
import json
import os
from dotenv import load_dotenv
from datetime import datetime
import pytz

# ========================
# LOAD TOKEN
# ========================
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ========================
# TIMEZONE (THAILAND)
# ========================
thai_tz = pytz.timezone("Asia/Bangkok")

def time_now():
    return datetime.now(thai_tz).strftime("%d/%m/%Y %H:%M")

# ========================
# INTENTS
# ========================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# ========================
# CONFIG
# ========================
DATA_FILE = "points.json"

LOG_CHANNEL_ID = 1475448056160849971

COUNCIL_ROLE_ID = 1369286013230252089

ALLOWED_ROLE_ID = 1430508523321688145

APPROVED = "<:approved:1370751335695126678>"
WAITING = "<:Waiting_for_approved:1370752766183735306>"
DENIED = "<:denied:1370751020845764671>"

LINE = "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"

# ========================
# LOAD DATA
# ========================
def load_data():

    if not os.path.exists(DATA_FILE):
        return {}

    with open(DATA_FILE, "r") as f:
        return json.load(f)

# ========================
# SAVE DATA
# ========================
def save_data(data):

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ========================
# FOOTER
# ========================
def footer(embed):

    embed.set_footer(
        text=f"Reborn Grass Witthaya Student Council | สภานักเรียนกราซวิทยา | {time_now()}"
    )

# ========================
# CHECK PERMISSION
# ========================
def has_permission(member):

    return any(role.id == ALLOWED_ROLE_ID for role in member.roles)

# ========================
# SEND LOG
# ========================
async def send_log(embed):

    channel = bot.get_channel(LOG_CHANNEL_ID)

    if channel:
        await channel.send(embed=embed)

# ========================
# READY
# ========================
@bot.event
async def on_ready():

    print(f"Bot Online: {bot.user}")

# ========================
# POINTS
# ========================
@bot.command()
async def points(ctx, member: discord.Member = None):

    if member is None:
        member = ctx.author

    data = load_data()

    points = data.get(str(member.id), 0)

    embed = discord.Embed(

        description=(
            f"{LINE}\n\n"
            f"{APPROVED} | {member.mention}\n"
            f"📊 Points : {points} Work Points\n\n"
            f"{LINE}"
        ),

        color=0x2ecc71

    )

    embed.set_author(
        name="Work Points | แต้มการทำงาน"
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    footer(embed)

    await ctx.send(embed=embed)

# ========================
# ADD
# ========================
@bot.command()
async def add(ctx, member: discord.Member, amount: int):

    if not has_permission(ctx.author):

        embed = discord.Embed(
            description=f"{DENIED} | You dont have permission to run this command!",
            color=0xe74c3c
        )

        footer(embed)

        await ctx.send(embed=embed)

        return

    data = load_data()

    user_id = str(member.id)

    new = data.get(user_id, 0) + amount

    data[user_id] = new

    save_data(data)

    embed = discord.Embed(

        description=(
            f"{LINE}\n\n"
            f"{APPROVED} | เพิ่ม {amount} Work Points ให้กับ {member.mention}\n"
            f"📊 Points Now : {new}\n\n"
            f"{LINE}"
        ),

        color=0x2ecc71

    )

    embed.set_author(name="Work Points | แต้มการทำงาน")

    embed.set_thumbnail(url=member.display_avatar.url)

    footer(embed)

    await ctx.send(embed=embed)

    log = discord.Embed(

        description=(
            f"{LINE}\n\n"
            f"{APPROVED} Point Added\n\n"
            f"👤 Admin : {ctx.author.mention}\n"
            f"🎯 Target : {member.mention}\n"
            f"📊 Points Now : {new}\n\n"
            f"{LINE}"
        ),

        color=0x2ecc71

    )

    footer(log)

    await send_log(log)

# ========================
# REMOVE
# ========================
@bot.command()
async def remove(ctx, member: discord.Member, amount: int):

    if not has_permission(ctx.author):

        embed = discord.Embed(
            description=f"{DENIED} | You dont have permission to run this command!",
            color=0xe74c3c
        )

        footer(embed)

        await ctx.send(embed=embed)

        return

    data = load_data()

    user_id = str(member.id)

    new = data.get(user_id, 0) - amount

    if new < 0:
        new = 0

    data[user_id] = new

    save_data(data)

    embed = discord.Embed(

        description=(
            f"{LINE}\n\n"
            f"{APPROVED} | ลบ {amount} Work Points จาก {member.mention}\n"
            f"📊 Points Now : {new}\n\n"
            f"{LINE}"
        ),

        color=0xe74c3c

    )

    embed.set_author(name="Work Points | แต้มการทำงาน")

    embed.set_thumbnail(url=member.display_avatar.url)

    footer(embed)

    await ctx.send(embed=embed)

    log = discord.Embed(

        description=(
            f"{LINE}\n\n"
            f"{DENIED} Point Removed\n\n"
            f"👤 Admin : {ctx.author.mention}\n"
            f"🎯 Target : {member.mention}\n"
            f"📊 Points Now : {new}\n\n"
            f"{LINE}"
        ),

        color=0xe74c3c

    )

    footer(log)

    await send_log(log)

# ========================
# DUTY (minutes → points)
# ========================
@bot.command()
async def duty(ctx, member: discord.Member, minutes: int):

    if not has_permission(ctx.author):

        embed = discord.Embed(
            description=f"{DENIED} | You dont have permission to run this command!",
            color=0xe74c3c
        )

        footer(embed)

        await ctx.send(embed=embed)

        return

    points = minutes // 6

    data = load_data()

    user_id = str(member.id)

    new = data.get(user_id, 0) + points

    data[user_id] = new

    save_data(data)

    embed = discord.Embed(

        description=(
            f"{LINE}\n\n"
            f"{APPROVED} | Duty Completed\n"
            f"🎯 Target : {member.mention}\n"
            f"⏱️ Minutes : {minutes}\n"
            f"📊 Points Earned : {points}\n"
            f"📊 Points Now : {new}\n\n"
            f"{LINE}"
        ),

        color=0x3498db

    )

    embed.set_author(name="Work Points | แต้มการทำงาน")

    embed.set_thumbnail(url=member.display_avatar.url)

    footer(embed)

    await ctx.send(embed=embed)

    await send_log(embed)

# ========================
# LEADERBOARD
# ========================
@bot.command()
async def leaderboard(ctx):

    data = load_data()

    role = ctx.guild.get_role(COUNCIL_ROLE_ID)

    members = []

    for member in role.members:

        points = data.get(str(member.id), 0)

        members.append((member, points))

    members.sort(key=lambda x: x[1], reverse=True)

    text = ""

    for i, (member, points) in enumerate(members[:10], 1):

        text += f"{i}. {member.mention} — {points} Points\n"

    embed = discord.Embed(

        description=(
            f"{LINE}\n\n"
            f"🏆 Work Points Leaderboard\n\n"
            f"{text if text else 'ไม่มีข้อมูล'}\n"
            f"{LINE}"
        ),

        color=0xf1c40f

    )

    footer(embed)

    await ctx.send(embed=embed)

# ========================
# RUN
# ========================
bot.run(TOKEN)
