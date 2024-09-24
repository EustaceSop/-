import requests
import discord
from discord.ext import commands
import random
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix='!', intents=intents)
#偽裝一下 怕會有速率限制(beta 不確定會不會有用)
class MyGO:
    def __init__(self):
        self.url = "https://mygoapi.miyago9267.com/mygo/all_img"
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36"
        ]
        self.all_img = self.fetch_images()
    
    def fetch_images(self):
        headers = {
            "User-Agent": random.choice(self.user_agents)
        }
        response = requests.get(self.url, headers=headers)
        return response.json()

    def search(self, message_content):
        results = []
        keywords = message_content.split()
        for img in self.all_img['urls']:
            alt_text = img.get('alt', '')
            if any(keyword in alt_text for keyword in keywords):
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

@bot.tree.command(name='mg', description='Search for an image based on a keyword.')
async def mg(interaction: discord.Interaction, query: str):
    message_content = query
    result = mygo.search(message_content)
    if result:
        await interaction.response.send_message(result)
    else:
        await interaction.response.send_message("找不到相關圖片捏 試試看更精準的關鍵詞叭")

@bot.tree.command(name='mglist', description='List all available images.')
async def mglist(interaction: discord.Interaction):
    alt_texts = mygo.get_alt_texts()
    if not alt_texts:
        await interaction.response.send_message("找..不到list內容..")
        return
    
    page_size = 5
    total_pages = (len(alt_texts) + page_size - 1) // page_size
    current_page = 0

    async def send_page(page):
        start = page * page_size
        end = start + page_size
        page_text = "\n".join(alt_texts[start:end])
        msg = await interaction.channel.send(page_text)
        await msg.add_reaction('⬅️')
        await msg.add_reaction('➡️')
        return msg

    msg = await send_page(current_page)

    def check(reaction, user):
        return user == interaction.user and reaction.message.id == msg.id and str(reaction.emoji) in ['⬅️', '➡️']

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
            await interaction.channel.send("timeout了寶貝 請重新打指令來查看list")
            break

# Start the bot and sync commands
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user}!')

bot.run('ur bot token')
