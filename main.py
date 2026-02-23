import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "points.json"

APPROVED = "<:approved:1370751335695126678>"
LINE = "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
LOGO = "<:Grass_Witthaya_Student_Council:1372353118024765440>"

# role permissions
POINTS_ROLE_ID = 1430508523321688145
ADMIN_ROLE_ID = 1369286013255422048
MOD_ROLE_ID = 1369286013134045184


# ===== โหลดข้อมูล =====
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)


# ===== บันทึกข้อมูล =====
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ===== เช็ค role points =====
def has_points_permission(member):
    return any(role.id == POINTS_ROLE_ID for role in member.roles)


# ===== เช็ค role announce =====
def has_announce_permission(member):
    return any(role.id in [ADMIN_ROLE_ID, MOD_ROLE_ID] for role in member.roles)


# ===== เมื่อบอทออนไลน์ =====
@bot.event
async def on_ready():
    print(f"Student Council Bot Online: {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands")
    except Exception as e:
        print(e)


# =========================
# POINT SYSTEM
# =========================

@bot.command()
async def checkpoint(ctx, member: discord.Member = None):

    if member is None:
        member = ctx.author

    data = load_data()
    points = data.get(str(member.id), 0)

    embed = discord.Embed(
        description=(
            f"{LINE}\n\n"
            f"❮ {APPROVED} ❯ | {member.name} ขณะนี้คุณมี **{points} Work Points** !\n\n"
            f"{LINE}"
        ),
        color=0x2ecc71
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    await ctx.send(embed=embed)


@bot.command()
async def add(ctx, member: discord.Member, amount: int):

    if not has_points_permission(ctx.author):
        await ctx.send("❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้")
        return

    data = load_data()
    user_id = str(member.id)

    new = data.get(user_id, 0) + amount

    data[user_id] = new
    save_data(data)

    embed = discord.Embed(
        description=(
            f"{LINE}\n\n"
            f"❮ {APPROVED} ❯ | เพิ่ม {amount} Work Points ให้กับ **{member.name}** สำเร็จ !\n\n"
            f"{LINE}"
        ),
        color=0x2ecc71
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    await ctx.send(embed=embed)


@bot.command()
async def remove(ctx, member: discord.Member, amount: int):

    if not has_points_permission(ctx.author):
        await ctx.send("❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้")
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
            f"❮ {APPROVED} ❯ | ลบ {amount} Work Points จาก **{member.name}** สำเร็จ !\n"
            f"ขณะนี้มี {new} Work Points\n\n"
            f"{LINE}"
        ),
        color=0xe74c3c
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    await ctx.send(embed=embed)


# =========================
# ANNOUNCE SYSTEM (SLASH)
# =========================

@bot.tree.command(name="announce", description="สร้างประกาศประชาสัมพันธ์")
@app_commands.describe(
    topic="หัวข้อประกาศ",
    date="วันที่",
    content="เนื้อหาประกาศ"
)
async def announce(interaction: discord.Interaction, topic: str, date: str, content: str):

    if not has_announce_permission(interaction.user):
        await interaction.response.send_message(
            "❌ เฉพาะ Admin หรือ Mod เท่านั้น",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        description=(
            f"ㅤㅤㅤㅤㅤㅤㅤ❮ ประชาสัมพันธ์ {LOGO} ❯ㅤㅤㅤㅤㅤㅤㅤ\n"
            f"{LINE}\n\n"
            f"( Topic | หัวข้อ ) : {topic}\n"
            f"( Date | วันที่ ) : {date}\n\n"
            f"{content}\n\n"
            f"{LINE}"
        ),
        color=0xe74c3c
    )

    embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)

    embed.set_footer(
        text=f"ประกาศโดย {interaction.user.name}",
        icon_url=interaction.user.display_avatar.url
    )

    await interaction.response.send_message(embed=embed)


# =========================

bot.run(TOKEN)