import requests
import discord
from discord.ext import commands
import random

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

class MyGO:
    def __init__(self):
        self.url = "https://mygoapi.miyago9267.com/mygo/all_img"
        self.all_img = requests.get(self.url).json()
    
    def search(self, query):
        results = []
        for img in self.all_img['urls']:
            if query in img.get('alt', ''):
                url = img.get('url')
                if url:
                    results.append(url)
        
        if results:
            return random.choice(results)
        return None

mygo = MyGO()

@bot.command(name='mg')
async def mg(ctx, *, query: str):
    result = mygo.search(query)
    if result:
        await ctx.send(result)
    else:
        await ctx.send("找不到相關圖片捏")

bot.run('token')
