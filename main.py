import discord
from discord.ext import commands
import json
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "points.json"

# โหลดข้อมูล
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# บันทึกข้อมูล
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ===== เมื่อบอทออนไลน์ =====
@bot.event
async def on_ready():
    print(f"Student Council Bot Online: {bot.user}")
    
APPROVED = "<:approved:1370751335695126678>"
LINE = "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"


# ===== checkpoint =====
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

    await ctx.send(embed=embed)


# ===== add =====
@bot.command()
@commands.has_permissions(administrator=True)
async def add(ctx, member: discord.Member, amount: float):

    data = load_data()
    user_id = str(member.id)

    current = data.get(user_id, 0)
    new = round(current + amount, 2)

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

    await ctx.send(embed=embed)


# ===== remove =====
@bot.command()
@commands.has_permissions(administrator=True)
async def remove(ctx, member: discord.Member, amount: float):

    data = load_data()
    user_id = str(member.id)

    current = data.get(user_id, 0)
    new = round(current - amount, 2)

    if new < 0:
        new = 0

    data[user_id] = new
    save_data(data)

    embed = discord.Embed(
        description=(
            f"{LINE}\n\n"
            f"❮ {APPROVED} ❯ | ลบจำนวน {amount} Work Points ออกจาก **{member.name}** สำเร็จ !\n"
            f"ขณะนี้มีจำนวนแต้มทั้งหมด {new} Work Points !\n\n"
            f"{LINE}"
        ),
        color=0x2ecc71
    )

    await ctx.send(embed=embed)    

bot.run("TOKEN")