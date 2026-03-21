import discord
from discord.ext import commands
import os

# 1. ตั้งค่า Intents ให้บอทอ่านข้อความได้
intents = discord.Intents.default()
intents.message_content = True  # ต้องเปิดอันนี้ใน Developer Portal ด้วย!
intents.members = True

# 2. ตั้งค่าบอท (Prefix คือ !)
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# สีเขียวประจำบอท (THAITUNRATH Green)
BOT_COLOR = discord.Color.dark_green()

@bot.event
async def on_ready():
    print(f"✅ บอทระบบ Prefix ออนไลน์แล้ว: {bot.user}")
    # ตรวจสอบว่าเปิด Intent สำเร็จไหม
    if not bot.intents.message_content:
        print("⚠️ คำเตือน: คุณยังไม่ได้เปิด Message Content Intent ใน Developer Portal!")

# --- 1. คำสั่ง !help ---
@bot.command()
async def help(ctx):
    await ctx.message.delete()
    embed = discord.Embed(
        description=(
            "_ _ _ _ _ _ _ _ _ _ ﹒ㆍ__**Help-desk**__ ﹒ㆍ﹒ _ _\n"
            "~~                                 ~~\n"
            "\n**• !news [หัวข้อ] | [วันที่] | [เนื้อหา]**\n"
            "**• !image** (แนบรูปหรือใส่ลิงก์)\n"
            "**• !embed [หัวข้อ] | [เนื้อหา]**\n"
            "**• !ping** - Tag ทุกคน (@everyone)"
        ),
        color=BOT_COLOR
    )
    await ctx.send(embed=embed)

# --- 2. คำสั่ง !news (หัวข้อ | วันที่ | เนื้อหา) ---
@bot.command()
@commands.has_permissions(administrator=True)
async def news(ctx, *, args=None):
    await ctx.message.delete()
    if not args: return
    
    parts = args.split("|")
    if len(parts) < 3:
        return await ctx.send("❌ รูปแบบผิด! ใช้: `!news หัวข้อ | วันที่ | เนื้อหา`", delete_after=5)
    
    topic, date, content = [p.strip() for p in parts[:3]]
    
    news_desc = (
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n"
        f"** ( Topic | หัวข้อ ) :** {topic}\n"
        f"** ( Date | วันที่ ) :** {date}\n\n"
        f"{content}\n\n"
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
    )
    
    embed = discord.Embed(title="ㅤㅤㅤㅤㅤㅤㅤ❮ THAITUNRATH News ❯", description=news_desc, color=BOT_COLOR)
    embed.set_footer(text=f"ประกาศโดย {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

# --- 3. คำสั่ง !image (แนบรูป หรือ ใส่ลิงก์) ---
@bot.command()
@commands.has_permissions(administrator=True)
async def image(ctx, url: str = None):
    await ctx.message.delete()
    img_url = url
    if ctx.message.attachments:
        img_url = ctx.message.attachments[0].url
    
    if img_url:
        embed = discord.Embed(color=BOT_COLOR)
        embed.set_image(url=img_url)
        await ctx.send(embed=embed)

# --- 4. คำสั่ง !embed (หัวข้อ | เนื้อหา) ---
@bot.command()
@commands.has_permissions(administrator=True)
async def embed(ctx, *, args=None):
    await ctx.message.delete()
    if not args: return
    parts = args.split("|")
    title = parts[0].strip()
    desc = parts[1].strip() if len(parts) > 1 else ""
    
    e = discord.Embed(title=title, description=desc, color=BOT_COLOR)
    await ctx.send(embed=e)

# --- 5. คำสั่ง !ping ---
@bot.command()
@commands.has_permissions(administrator=True)
async def ping(ctx):
    await ctx.message.delete()
    await ctx.send("-# @everyone @here - sorry for ping!")

# รันบอท
bot.run(os.getenv('DISCORD_TOKEN'))
