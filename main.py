import discord
from discord.ext import commands
import asyncio
import random
from ast import literal_eval

token = 'MTM1OTUxODk0OTA0MTExNTMyMA.GWVATN.B_qihYlFhcYWxI0NMrTVE-sI7-eDvQEKZgz6nM'

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

class Select(discord.ui.Select):
    """menu deroulant (25 options max)"""
    def __init__(self, players):
        self.players = players
        options = []
        for player in self.players:
            options.append(discord.SelectOption(label=f"{player.name}"))
        # options=[
        #     discord.SelectOption(label="Yotoon",emoji="✨",description="This is option 2!"),
       # ]
        super().__init__(placeholder="Select an option",max_values=1,min_values=1,options=options)
    async def callback(self, interaction: discord.Interaction):
        """renvoie une réponse à la selection d'un choix """
        choice = self.values[0]
        voteur = await user_to_player(interaction.user, self.players)
        for personne_votee in self.players:

            if choice == f"{personne_votee.name}" and voteur.previous_vote != None:
                voteur.previous_vote.nvote -= 1
                voteur.previous_vote = personne_votee
                personne_votee.nvote += 1
                author = interaction.user.id
                await interaction.response.defer()
                await interaction.followup.send(f"<@{author}> a voté pour <@{personne_votee.id}>. **{personne_votee.nvote}** vote(s)")

            if choice == f"{personne_votee.name}" and personne_votee.previous_vote == None:
                voteur.previous_vote = personne_votee
                personne_votee.nvote += 1
                author = interaction.user.id
                await interaction.response.send_message(f"<@{author}> a voté pour <@{personne_votee.id}>. **{personne_votee.nvote}** vote(s)", ephemeral=False)





        # if self.values[0] == "Option 1":
        #     await interaction.response.edit_message(content="This is the first option from the entire list!")
        # elif self.values[0] == "Option 2":
        #     await interaction.response.send_message("This is the second option from the list entire wooo!",ephemeral=False)
        # elif self.values[0] == "Option 3":
        #     await interaction.response.send_message("Third One!",ephemeral=True)

class SelectView(discord.ui.View):
    """permet d'afficher le menu deroulant"""
    def __init__(self, players, *, timeout = 180):
        super().__init__(timeout=timeout)
        self.add_item(Select(players))


async def menu(context, players):
    """commande pour menu deroulant"""
    await context.send("Vote du village",view=SelectView(players))

class Player():
    """Classe joueur"""
    def __init__(self, name, id, role, state, nvote: int = 0, previous_vote = None, amour = False, victime = False):
        self.name = name
        self.id = id
        self.role = role
        self.state = state
        self.nvote = nvote
        self.previous_vote = previous_vote
        self.amour = amour
        self.victime = victime

    async def is_alive(self):
        if self.state:
            return self.state
        else:
            await self.name.edit(mute=True)

async def user_to_player(user, players):
    for player in players:
        if player.name == user:
            return player


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
    for i in range(0):
        await msg.edit(content="La partie commence")
        await asyncio.sleep(3/4)
        await msg.edit(content="La partie commence.")
        await asyncio.sleep(3/4)
        await msg.edit(content="La partie commence..")
        await asyncio.sleep(3/4)
        await msg.edit(content="La partie commence...")
        await asyncio.sleep(3/4)


async def discussion(context, time: int, n_jours: int):
    """Timer de début de jour et de phase de discussion"""
    await context.send(content=f"# Jour {n_jours}")
    await context.send(content=f"## Phase de discussion")
    msg = await context.send(content=f"### Il vous reste {time} secondes pour discuter.")
    for i in range(0, time):
        await asyncio.sleep(1)
        await msg.edit(content=f"### Il vous reste {time-1-i} secondes pour discuter.")
    await msg.edit(content=f"## La phase de discussion est terminée.")
    await asyncio.sleep(1)

async def vote_village(context, time: int, players):
    """Timer de début de jour et de phase de discussion"""
    await context.send(f"Phase de vote")
    msg = await context.send(content=f"Il vous reste {time} secondes pour voter.")
    menu_vote = await menu(context, players)
    for i in range(0, time):
        await asyncio.sleep(1)
        await msg.edit(content=f"Il vous reste {time-1-i} secondes pour voter.")
    await msg.delete()
    await context.send(content=f"La phase de vote est terminée.")
    await asyncio.sleep(1)

async def night(context, time: int, n_nuits: int):
    """Timer de nuit"""
    await context.send(content=f"Nuit {n_nuits}")
    msg = await context.send(f"Il reste {time} secondes.")
    for i in range(0, time):
        await asyncio.sleep(1)
        await msg.edit(content=f"Il reste {time-1-i} secondes.")
    await asyncio.sleep(1)

async def get_compo(context, nb_players):
    """Récupère une composition de rôles dont on a besoin"""
    # if nb_players < 6 or nb_players > 12: #enlever commentaire pour vrai test
    #     raise IndexError("6 <= int <= 12")
    with open(f"compo{nb_players}.txt", "r") as f:
        return literal_eval(f.read())
async def role_assign(context, nb_players, members: literal_eval):
    """Assigne un role au hasard pour chaque joueur de la partie"""
    liste = []
    roles = await get_compo(context, nb_players)
    for i in range(len(members)):
        role = random.choice(roles)
        roles.remove(role)
        member_id = random.choice(members)
        members.remove(member_id)
        name = await bot.fetch_user(member_id)
        liste.append(Player(name, member_id, role, True))
    return liste


async def vc_members(context):
    """Renvoie tous les membres présents dans le vocal de la personne qui a lancé la commande"""
    vc = []
    for guild in bot.guilds:
        if guild.id == context.author.guild.id:
            for member in guild.members:
                if member.voice == None:
                    continue
                elif member.voice.channel.id == context.author.voice.channel.id:
                    vc.append(member.id)
    return vc

async def thread(context, name):
    """Créé un thread privé et renvoie son ID"""
    channel = context.channel
    thread = await channel.create_thread(name=f"{name}", auto_archive_duration=60)
    await thread.edit(invitable=False)
    return thread.id

async def reset_votes(context, players):
    for player in players:
        player.nvote = 0

async def ordre_roles(context, players):
    cupi, vovo, lg, soso = None, None, None, None
    for player in players:
        if player.role == "Cupidon":
            cupi = player.id
        if player.role == "Voyante":
            vovo = player.id
        if player.role == "Loup Garou":
            lg = player.id
        if player.role == "Sorciere":
            soso = player.id
    liste = [cupi, vovo, lg, soso]
    return liste


async def annonce_role(context, players):
    """Envoie le role de chacun des joueurs par dm et ajoute les joueurs au thread privé"""
    for player in players: #parcours de tous les joueurs en jeu
        await context.send(f"<@{player.id}>") #mentions des joueurs dans le thread privé
        user = await bot.fetch_user(f"{player.id}") #trouve l'utilisateur discord du joueur a partir de l'ID
        channel = await user.create_dm() #créé le dm avec le joueur
        await channel.send(f"Ton rôle est: {player.role}") #envoie du role au joueur par dm

async def action_nuit(context, ordre_nuit): #a terminer
    """a terminer"""
    for role in ordre_nuit:
        if role == None:
            continue
        await context.send("C'est au tour du Cupidon")
        await night_timer(context, 20)

async def pendre(context, players):
    maxi = 0
    max_i = 0
    for i in range(len(players)):
        if players[i].nvote > maxi:
            maxi = players[i].nvote
            max_i = i
    await context.send(f"{players[max_i].name} a été tué par le village. ({maxi} votes)")
    await asyncio.sleep(1)
    players[max_i].state = False

async def lg_call(lg_chat, players):
    for player in players:
        if player.role == "Loup Garou":
            await lg_chat.send(f"<@{player.id}>")





@bot.command()
async def start(context):
    """Starts the game"""
    vc = await vc_members(context) #liste des personnes présentes dans le voc
    nb_players = len(vc) #nombre de joueurs dans la partie
    main_thread = await thread(context, "Le Village") #creation du thread privé et renvoie son id
    lg_thread = await thread(context, "Loups-Garous")  # créé thread privé des loups
    pf_thread = await thread(context, "Petite-Fille")
    context = bot.get_channel(main_thread) #changement de context: channel -> thread
    players = await role_assign(context, nb_players, vc) #liste de joueur de type class Player
    await annonce_role(context, players) #annonce des roles par dm
    lg_chat = bot.get_channel(lg_thread)
    await lg_chat.edit(locked=True)
    pf_chat = bot.get_channel(pf_thread)
    await pf_chat.edit(locked=True)
    await lg_call(lg_chat, players)
    await start_timer(context, 1)  # compteur de départ
    game_state = True #True = le jeu est en cours, False = le jeu est fini
    ordre_nuit = await ordre_roles(context, players)
    n_jours = 0
    n_nuits = 0
    await asyncio.sleep(1)
    while game_state == True: #boucle du jeu
        n_jours += 1
        await discussion(context, 1, n_jours)
        await asyncio.sleep(1)
        await vote_village(context, 33, players)
        await asyncio.sleep(1)
        await pendre(context, players)
        await reset_votes(context, players)
        await asyncio.sleep(1)
        n_nuits += 1
        await night(context, 1, n_nuits)
        game_state = False
    await context.send("Le jeu est terminé !")


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




