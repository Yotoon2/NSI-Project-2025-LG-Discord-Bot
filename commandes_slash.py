import discord
import math
from discord.ext import commands
import asyncio

token = 'MTM1OTUxODk0OTA0MTExNTMyMA.GWVATN.B_qihYlFhcYWxI0NMrTVE-sI7-eDvQEKZgz6nM'

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.tree.command()
async def timer(interaction: discord.Message, time: int):
    await interaction.response.send_message(f"Il reste {time} secondes.")
    for i in range(0, time):
        await asyncio.sleep(1)
        await interaction.edit_original_response(content=f"Il reste {time-1-i} secondes.")

@bot.tree.command()
async def multiplication(interaction: discord.Interaction, a: int, b: int):
    await interaction.response.send_message(f'{a} x {b} = {a*b}')

@bot.tree.command()
async def racine_carre(interaction: discord.Interaction, a: int):
    await interaction.response.send_message(f'{math.sqrt(a)}')

@bot.tree.command()
async def ping_user(interaction: discord.Interaction, user: discord.User):
    await interaction.response.send_message(f'<@{user.id}>')

@bot.tree.command()
async def dm(interaction: discord.Interaction, user: discord.User):
    for i in range(100):
        channel = await user.create_dm()
        await channel.send(f'<@{user.id}>')


@bot.event
async def on_ready():
    print(f'Connecté en tant que {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'{len(synced)} commande(s) synchronisée(s)')
    except Exception as e:
        print(e)

def main():
    bot.run(token=token)

if __name__ == '__main__':
    main()

