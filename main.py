import discord
from discord.ext import commands
import asyncio
import random
from ast import literal_eval

token = 'MTM1OTUxODk0OTA0MTExNTMyMA.GWVATN.B_qihYlFhcYWxI0NMrTVE-sI7-eDvQEKZgz6nM'

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
async def start_timer(context, time: int):
    msg = await context.send(f"Il reste {time} secondes.")
    for i in range(0, time):
        await asyncio.sleep(1)
        await msg.edit(content=f"Il reste {time - 1 - i} secondes.")
    await asyncio.sleep(1)
    for i in range(5):
        await msg.edit(content="La partie commence")
        await asyncio.sleep(3/4)
        await msg.edit(content="La partie commence.")
        await asyncio.sleep(3/4)
        await msg.edit(content="La partie commence..")
        await asyncio.sleep(3/4)
        await msg.edit(content="La partie commence...")
        await asyncio.sleep(3/4)

async def day_timer(context, time: int):
    time = 150
    msg = await context.send(f"Il reste {time} secondes.")
    for i in range(0, time):
        await asyncio.sleep(1)
        await msg.edit(content=f"Il reste {time-1-i} secondes.")
    await msg.edit(content=f"La nuit tombe...")

async def night_timer(context, time: int):
    time = 150
    msg = await context.send(f"Il reste {time} secondes.")
    for i in range(0, time):
        await asyncio.sleep(1)
        await msg.edit(content=f"Il reste {time-1-i} secondes.")
    await msg.edit(content=f"Le jour se lève...")

@bot.command()
async def dm(context, user: discord.User):
    channel = await user.create_dm()
    await channel.send(f'<@{user.id}>')
    
@bot.command()
async def thread(context, name):
    message = context.message
    thread = await message.create_thread(name=f"{name}")
    
@bot.command()
async def role_assign(context,*, members: literal_eval):
    dict = {}
    roles = ["Loup Garou", "Simple Villageois", "Voyante", "Sorcière"]
    for i in range(len(members)):
        role = random.choice(roles)
        roles.remove(role)
        member = random.choice(members)
        members.remove(member)
        dict[member] = role
    await context.send(f"{dict}")
    print(dict)
    
@bot.command()
async def vc_members(context):
    vc = []
    for guild in bot.guilds:
        if guild.id == context.author.guild.id:
            for member in guild.members:
                if member.voice.channel.id == context.author.voice.channel.id:
                    await context.send(f"{member} is connected to {context.author.voice.channel.name}.")
                    vc.append(member.name)
                await context.send(vc)
            return vc

@bot.command()
async def get_members(context):
    members = []
    print(vc)
    for guild in bot.guilds:
        if guild.id == context.author.guild.id:
            for member in guild.members:
                members.append(member.name)
            await context.send(f"Membres:{members}")
            return members

@bot.command()
async def composition(context, nb_joueurs, *, compo: literal_eval = []):
    nb_joueurs = int(nb_joueurs)
    compo = list(compo)
    if compo == []:
        with open(f"compo{nb_joueurs}.txt", "r") as f:
            await context.send(f"Composition actuelle pour {nb_joueurs} joueurs: {f.read()}")
    elif nb_joueurs < 6 or nb_joueurs > 12:
        await context.send('Veuillez choisir un chiffre entre 6 et 12')
        raise IndexError("6 <= int <= 12")
    elif len(compo) != nb_joueurs:
        await context.send("Il faut le même nombre de rôles que de joueurs")
        raise IndexError("n players don't match n roles")
    else:
        open(f"compo{nb_joueurs}.txt").close()
        with open(f"compo{nb_joueurs}.txt", "w") as f:
            f.write(str(compo))
        await context.send(f"{compo}")
        return compo
    
@bot.command()
async def start(context):
    start_timer(context, 20)
    vc = vc_members(context)
    print(type(vc))
    nb_players = len(vc)
    print(nb_players)
    players = role_assign(context, vc)
    print(type(players))
    thread = thread(context, "Village")

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

