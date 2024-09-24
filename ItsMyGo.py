import requests
import discord
from discord.ext import commands
import random
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix='!', intents=intents)

class MyGO:
    def __init__(self):
        self.url = "https://mygoapi.miyago9267.com/mygo/all_img"
        self.all_img = requests.get(self.url).json()
    
    def search(self, message_content):
        results = []
        for img in self.all_img['urls']:
            if any(keyword in message_content for keyword in img.get('alt', '').split()):
                url = img.get('url')
                if url:
                    results.append(url)
        
        if results:
            return random.choice(results)
        return None
    
    def get_alt_texts(self):
        alt_texts = [img.get('alt', '') for img in self.all_img['urls']]
        return alt_texts

mygo = MyGO()

@bot.command(name='mg')
async def mg(ctx, *, query: str):
    message_content = ctx.message.content
    result = mygo.search(message_content)
    if result:
        await ctx.send(result)
    else:
        await ctx.send("找不到相關圖片捏")

@bot.command(name='mglist')
async def mglist(ctx):
    alt_texts = mygo.get_alt_texts()
    if not alt_texts:
        await ctx.send("找..不到list內容..")
        return
    
    page_size = 5
    total_pages = (len(alt_texts) + page_size - 1) // page_size
    current_page = 0

    async def send_page(page):
        start = page * page_size
        end = start + page_size
        page_text = "\n".join(alt_texts[start:end])
        msg = await ctx.send(page_text)
        await msg.add_reaction('⬅️')
        await msg.add_reaction('➡️')

        return msg

    msg = await send_page(current_page)

    def check(reaction, user):
        return user == ctx.author and reaction.message.id == msg.id and str(reaction.emoji) in ['⬅️', '➡️']

    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)

            if str(reaction.emoji) == '➡️' and current_page < total_pages - 1:
                current_page += 1
                await msg.delete()
                msg = await send_page(current_page)
            elif str(reaction.emoji) == '⬅️' and current_page > 0:
                current_page -= 1
                await msg.delete()
                msg = await send_page(current_page)

            await msg.remove_reaction(reaction, user)

        except asyncio.TimeoutError:
            await ctx.send("timeout了寶貝 請重新打指令來查看list")
            break

bot.run('your bot token')
