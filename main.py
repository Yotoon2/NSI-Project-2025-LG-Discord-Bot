import discord
from discord.ext import commands
import asyncio
import random
from ast import literal_eval

token = 'MTM1OTUxODk0OTA0MTExNTMyMA.GWVATN.B_qihYlFhcYWxI0NMrTVE-sI7-eDvQEKZgz6nM'

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

class Player():
    """Classe joueur"""
    def __init__(self, name, role, state):
        self.name = name
        self.role = role
        self.state = state

    def is_alive(self):
        return self.state

@bot.command(aliases=["compo"])
async def composition(context, nb_players, *, compo: literal_eval = []):
    """Commande pour afficher ou changer une composition de rôles"""
    nb_players = int(nb_players)
    compo = list(compo)
    if compo == []:
        with open(f"compo{nb_players}.txt", "r") as f:
            await context.send(f"Composition actuelle pour {nb_players} joueurs: {f.read()}")
    elif nb_players < 6 or nb_players > 12:
        await context.send('Veuillez choisir un chiffre entre 6 et 12')
        raise IndexError("6 <= int <= 12")
    elif len(compo) != nb_players:
        await context.send("Il faut le même nombre de rôles que de joueurs")
        raise IndexError("n players don't match n roles")
    else:
        open(f"compo{nb_players}.txt").close()
        with open(f"compo{nb_players}.txt", "w") as f:
            f.write(str(compo))
        await context.send(f"{compo}")
        return compo

async def start_timer(context, time: int):
    """Timer de début de partie"""
    msg = await context.send(f"Il reste {time} secondes avant le début de la partie.")
    for i in range(0, time):
        await asyncio.sleep(1)
        await msg.edit(content=f"Il reste {time - 1 - i} secondes avant le début de la partie.")
    await asyncio.sleep(3/4)
    for i in range(1):
        await msg.edit(content="La partie commence")
        await asyncio.sleep(3/4)
        await msg.edit(content="La partie commence.")
        await asyncio.sleep(3/4)
        await msg.edit(content="La partie commence..")
        await asyncio.sleep(3/4)
        await msg.edit(content="La partie commence...")
        await asyncio.sleep(3/4)


async def day_timer(context, time: int):
    """Timer du jour"""
    msg = await context.send(f"Il reste {time} secondes.")
    for i in range(0, time):
        await asyncio.sleep(1)
        await msg.edit(content=f"Il reste {time-1-i} secondes.")
    await msg.edit(content=f"La nuit tombe...")
    await asyncio.sleep(1)

async def night_timer(context, time: int):
    """Timer de nuit"""
    msg = await context.send(f"Il reste {time} secondes.")
    for i in range(0, time):
        await asyncio.sleep(1)
        await msg.edit(content=f"Il reste {time-1-i} secondes.")
    await msg.edit(content=f"Le jour se lève...")
    await asyncio.sleep(1)

async def get_compo(context, nb_players):
    """Récupère une composition de rôles dont on a besoin"""
    # if nb_players < 6 or nb_players > 12:
    #     raise IndexError("6 <= int <= 12")
    with open(f"compo{nb_players}.txt", "r") as f:
        return literal_eval(f.read())
async def role_assign(context, nb_players, members: literal_eval):
    """Assigne un role au hasard pour chaque joueur de la partie"""
    liste = []
    roles = await get_compo(context, nb_players)
    # print("roles_type:", type(roles))
    for i in range(len(members)):
        role = random.choice(roles)
        roles.remove(role)
        member = random.choice(members)
        members.remove(member)
        liste.append(Player(member, role, True))
    return liste


async def vc_members(context):
    """Renvoie tous les membres présents dans le vocal de la personne qui a lancé la commande"""
    vc = []
    for guild in bot.guilds:
        if guild.id == context.author.guild.id:
            # print(guild.members)
            for member in guild.members:
                # print(member)
                if member.voice == None:
                    continue
                elif member.voice.channel.id == context.author.voice.channel.id:
                    # print(member)
                    vc.append(member.id)
    # print(type(vc))
    return vc

async def thread(context, name):
    """Créer un thread privée et renvoie son ID"""
    channel = context.channel
    thread = await channel.create_thread(name=f"{name}", auto_archive_duration=60)
    # print(thread.id)
    return thread.id


@bot.command()
async def start(context):
    """Starts the game"""
    vc = await vc_members(context) #liste des personnes présentes dans le voc
    nb_players = len(vc) #nombre de joueurs dans la partie
    game_thread = await thread(context, "Village") #creation du thread privé et renvoie son id
    context = bot.get_channel(game_thread) #changement de channel: channel -> thread
    await start_timer(context, 1) #compteur de départ
    # print(nb_players)
    players = await role_assign(context, nb_players, vc) #liste de joueur de type class Player
    for player in players:
        await asyncio.sleep(1/4)
        id = player.name
        await context.send(f"<@{id}>") #mentions des joueurs dans le thread privé
        user = await bot.fetch_user(f"{id}")
        channel = await user.create_dm()
        await channel.send(f"Ton rôle est: {player.role}")
    await asyncio.sleep(3/4)
   # print(f"<@{players[0].name}>")
    await context.send("Jour 1")
    await asyncio.sleep(1)
    await day_timer(context, 10)
    await night_timer(context, 10)

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





