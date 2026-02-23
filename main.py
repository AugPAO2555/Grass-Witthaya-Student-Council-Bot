import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime
import pytz

# ========================
# TOKEN
# ========================
TOKEN = os.getenv("DISCORD_TOKEN")

# ========================
# SETTINGS
# ========================
DATA_FILE = "points.json"
LOG_CHANNEL_ID = 1475448056160849971
POINT_GIVER_ROLE_ID = 1430508523321688145
COUNCIL_ROLE_ID = 1369286013230252089

APPROVED = "<:approved:1370751335695126678>"
DENIED = "<:denied:1370751020845764671>"
WAITING = "<:Waiting_for_approved:1370752766183735306>"
LOGO = "<:Grass_Witthaya_Student_Council:1372353118024765440>"

LINE = "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"

# ========================
# intents
# ========================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ========================
# load/save data
# ========================
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ========================
# time footer
# ========================
def get_footer():
    tz = pytz.timezone("Asia/Bangkok")
    now = datetime.now(tz)
    return f"Reborn | Grass Witthaya Student Council | สภานักเรียนกราซวิทยา | {now.strftime('%d/%m/%Y %H:%M')}"

# ========================
# permissions
# ========================
def is_point_giver(member):
    return any(role.id == POINT_GIVER_ROLE_ID for role in member.roles)

def is_admin_or_mod(member):
    if member.guild_permissions.administrator:
        return True

    allowed = ["Admin", "Mod", "Moderator", "Staff"]
    return any(role.name in allowed for role in member.roles)

# ========================
# send log
# ========================
async def send_log(embed, guild):
    channel = guild.get_channel(LOG_CHANNEL_ID)
    if channel:
        await channel.send(embed=embed)

# ========================
# ready
# ========================
@bot.event
async def on_ready():
    print(f"Bot online: {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands")
    except Exception as e:
        print(e)

# ========================
# points
# ========================
@bot.command()
async def points(ctx, member: discord.Member = None):

    if member is None:
        member = ctx.author

    data = load_data()
    pts = data.get(str(member.id), 0)

    embed = discord.Embed(
        description=(
            f"{LINE}\n\n"
            f"{APPROVED} | {member.mention} มี **{pts} Work Points**\n\n"
            f"{LINE}"
        ),
        color=0x2ecc71
    )

    embed.set_footer(text=get_footer())

    await ctx.send(embed=embed)

# ========================
# add
# ========================
@bot.command()
async def add(ctx, member: discord.Member, amount: int):

    if not is_point_giver(ctx.author):

        embed = discord.Embed(
            description=f"{DENIED} | You dont have permission to run this command!",
            color=0xe74c3c
        )

        await ctx.send(embed=embed)
        return

    data = load_data()

    uid = str(member.id)
    current = data.get(uid, 0)
    new = current + amount

    data[uid] = new
    save_data(data)

    embed = discord.Embed(
        description=(
            f"{LINE}\n\n"
            f"{APPROVED} | มอบ {amount} Points ให้ {member.mention} เรียบร้อย\n\n"
            f"{LINE}"
        ),
        color=0x2ecc71
    )

    embed.set_footer(text=get_footer())

    await ctx.send(embed=embed)
    await send_log(embed, ctx.guild)

# ========================
# remove
# ========================
@bot.command()
async def remove(ctx, member: discord.Member, amount: int):

    if not is_point_giver(ctx.author):

        embed = discord.Embed(
            description=f"{DENIED} | You dont have permission to run this command!",
            color=0xe74c3c
        )

        await ctx.send(embed=embed)
        return

    data = load_data()

    uid = str(member.id)
    current = data.get(uid, 0)
    new = current - amount

    if new < 0:
        new = 0

    data[uid] = new
    save_data(data)

    embed = discord.Embed(
        description=(
            f"{LINE}\n\n"
            f"{APPROVED} | ลบ {amount} Points จาก {member.mention} เรียบร้อย\n"
            f"คงเหลือ {new} Points\n\n"
            f"{LINE}"
        ),
        color=0xe74c3c
    )

    embed.set_footer(text=get_footer())

    await ctx.send(embed=embed)
    await send_log(embed, ctx.guild)

# ========================
# leaderboard
# ========================
@bot.command()
async def leaderboard(ctx):

    data = load_data()
    ranking = []

    for uid, pts in data.items():

        member = ctx.guild.get_member(int(uid))

        if member and any(role.id == COUNCIL_ROLE_ID for role in member.roles):
            ranking.append((member, pts))

    ranking.sort(key=lambda x: x[1], reverse=True)

    text = ""

    for i, (member, pts) in enumerate(ranking[:10], 1):
        text += f"{i}. {member.mention} — {pts} Points\n"

    embed = discord.Embed(
        title="🏆 Leaderboard | สภานักเรียน",
        description=text if text else "ไม่มีข้อมูล",
        color=0xf1c40f
    )

    embed.set_footer(text=get_footer())

    await ctx.send(embed=embed)

# ========================
# announce
# ========================
@bot.tree.command(name="announce", description="สร้างประกาศ")
@app_commands.describe(
    topic="หัวข้อ",
    date="วันที่",
    content="เนื้อหา"
)
async def announce(interaction: discord.Interaction, topic: str, date: str, content: str):

    if not is_admin_or_mod(interaction.user):

        await interaction.response.send_message(
            f"{DENIED} | เฉพาะ Admin / Mod เท่านั้น",
            ephemeral=True
        )

        return

    embed = discord.Embed(
        description=(
            f"ㅤㅤㅤㅤㅤㅤㅤ❮ ประชาสัมพันธ์ {LOGO} ❯ㅤㅤㅤㅤㅤㅤㅤ\n\n"
            f"{LINE}\n\n"
            f"( Topic | หัวข้อ ) : {topic}\n"
            f"( Date | วันที่ ) : {date}\n\n"
            f"{content}\n\n"
            f"{LINE}"
        ),
        color=0x2f3136
    )

    embed.set_footer(text=get_footer())

    await interaction.response.send_message(embed=embed)

# ========================
# run
# ========================
bot.run(TOKEN)