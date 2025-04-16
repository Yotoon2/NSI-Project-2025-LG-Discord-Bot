import discord
from discord.ext import commands, tasks
import asyncio
import random
from ast import literal_eval

token = 'MTM1OTUxODk0OTA0MTExNTMyMA.GWVATN.B_qihYlFhcYWxI0NMrTVE-sI7-eDvQEKZgz6nM'

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

class SelectVote(discord.ui.Select):
    """menu deroulant (25 options max)"""
    print("Bonjour6")
    def __init__(self, players, player = None):
        self.players = players
        self.player = player
        options = []
        for player in self.players:
            options.append(discord.SelectOption(label=f"{player.name}"))
        # options=[
        #     discord.SelectOption(label="Yotoon",emoji="✨",description="This is option 2!"),
       # ]
        super().__init__(placeholder="Select an option",max_values=1,min_values=1,options=options)
    async def callback(self, interaction: discord.Interaction):
        """renvoie une réponse à la selection d'un choix """
        await interaction.response.defer()
        print(f"self.player: {self.player}, type: {type(self.player)}")
        choice = self.values[0] #type str
        voteur = await user_to_player(interaction.user, self.players) #type player
        # print(f"auteur: {interaction.user} type: {type(interaction.user)}")
        # print(f"voteur: {voteur} type: {type(voteur)}")
        for personne_votee in self.players: #type player et type liste
            if self.player == None:
                if choice == f"{personne_votee.name}" and voteur.previous_vote != None:
                    author = interaction.user.id
                    voteur.previous_vote.nvote -= 1
                    voteur.previous_vote = personne_votee
                    personne_votee.nvote += 1
                    await interaction.followup.send(f"<@{author}> a voté pour <@{personne_votee.id}>. **{personne_votee.nvote}** vote(s)")
                elif interaction.response.is_done() == False:
                    if choice == f"{personne_votee.name}" and personne_votee.previous_vote == None:
                        author = interaction.user.id
                        voteur.previous_vote = personne_votee
                        personne_votee.nvote += 1
                        await interaction.response.send_message(f"<@{author}> a voté pour <@{personne_votee.id}>. **{personne_votee.nvote}** vote(s)", ephemeral=False)
                else:
                    if choice == f"{personne_votee.name}" and personne_votee.previous_vote == None:
                        author = interaction.user.id
                        voteur.previous_vote = personne_votee
                        personne_votee.nvote += 1
                        await interaction.followup.send(f"<@{author}> a voté pour <@{personne_votee.id}>. **{personne_votee.nvote}** vote(s)")

            elif self.player[0].role == "Loup Garou":
                if choice == f"{personne_votee.name}" and voteur.previous_vote != None:
                    author = interaction.user.id
                    voteur.previous_vote.nvote -= 1
                    voteur.previous_vote = personne_votee
                    personne_votee.nvote += 1
                    await interaction.followup.send(f"<@{author}> veut dévorer **{personne_votee.name}**. **{personne_votee.nvote}** vote(s)")
                elif interaction.response.is_done() == False:
                    if choice == f"{personne_votee.name}" and personne_votee.previous_vote == None:
                        author = interaction.user.id
                        voteur.previous_vote = personne_votee
                        personne_votee.nvote += 1
                        await interaction.response.send_message(f"<@{author}> veut dévorer **{personne_votee.name}**. **{personne_votee.nvote}** vote(s)", ephemeral=False)
                else:
                    if choice == f"{personne_votee.name}" and personne_votee.previous_vote == None:
                        author = interaction.user.id
                        voteur.previous_vote = personne_votee
                        personne_votee.nvote += 1
                        await interaction.followup.send(f"<@{author}> veut dévorer **{personne_votee.name}**. **{personne_votee.nvote}** vote(s)")

            elif self.player.role == "Voyante":
                if choice == f"{personne_votee.name}" and voteur.previous_vote != None:
                    voteur.previous_vote.nvote -= 1
                    voteur.previous_vote = personne_votee
                    personne_votee.nvote += 1
                    await interaction.followup.send(f"Vous avez décidé d'espionner **{personne_votee.name}**.")
                elif interaction.response.is_done() == False:
                    if choice == f"{personne_votee.name}" and personne_votee.previous_vote == None:
                        voteur.previous_vote = personne_votee
                        personne_votee.nvote += 1
                        await interaction.response.send_message(f"Vous avez décidé d'espionner **{personne_votee.name}**.", ephemeral=False)
                else:
                    if choice == f"{personne_votee.name}" and personne_votee.previous_vote == None:
                        voteur.previous_vote = personne_votee
                        personne_votee.nvote += 1
                        await interaction.followup.send(f"Vous avez décidé d'espionner **{personne_votee.name}**.")



class SelectView(discord.ui.View):
    """permet d'afficher le menu deroulant"""
    print("Bonjour5")
    def __init__(self, players, player=None, *, timeout = 180): #Select est la classe a afficher
        super().__init__(timeout=timeout)
        self.add_item(SelectVote(players, player))


async def menu(context, players: list, text: str, player=None): #Select est la classe a afficher, player est le joueur avec un role qui agit de nuit s'il y en a un
    """commande pour menu deroulant"""
    print("Bonjour4")
    vote_menu = await context.send(content=text, view=SelectView(players=players, player=player))
    return vote_menu

class Player():
    """Classe joueur"""
    def __init__(self, name, id: int, role, state: bool, member: discord.Member, nvote: int = 0, previous_vote = None, amour : bool = False):
        self.name = name
        self.id = id
        self.role = role
        self.state = state
        self.member = member
        self.nvote = nvote
        self.previous_vote = previous_vote
        self.amour = amour


    async def is_alive(self):
        if self.state:
            return self.state
        else:
            await self.name.edit(mute=True)

async def user_to_player(user, players: list):
    # print(f"user: {user} type: {type(user)}")
    for player in players:
        # print(f"player: {player.name} type: {type(player.name)}")
        if player.name == str(user):
            return player


@bot.command(aliases=["compo"])
async def composition(context, nb_players: int, *, compo: literal_eval = []):
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


async def role_timer(context, time: int, n_nuits: int):
    """Timer de nuit"""
    await context.send(content=f"## Nuit {n_nuits}")
    msg = await context.send(f"Il vous reste {time} secondes pour faire un choix.")
    for i in range(0, time):
        await asyncio.sleep(1)
        await msg.edit(content=f"Il vous reste {time-1-i} secondes pour faire un choix.")
    await asyncio.sleep(1)
    await msg.delete()
    await context.send("## Fin de votre tour.")

async def vote_village(context, time: int, players: list):
    """Timer de début de jour et de phase de discussion"""
    await context.send(f"Phase de vote")
    msg = await context.send(content=f"Il vous reste {time} secondes pour voter.")
    vote_menu = await menu(context, players, "Vote du Jour")
    for i in range(0, time):
        await asyncio.sleep(1)
        await msg.edit(content=f"Il vous reste {time-1-i} secondes pour voter.")
    await msg.delete()
    await vote_menu.delete()
    await context.send(content=f"La phase de vote est terminée.")
    await asyncio.sleep(1)

async def get_compo(context, nb_players: int):
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
        member = random.choice(members)
        members.remove(member)
        liste.append(Player(member.name, member.id, role, True, member = member))
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
                    vc.append(member)
    return vc

async def thread(context, name: str):
    """Créé un thread privé et renvoie son ID"""
    channel = context.channel
    thread = await channel.create_thread(name=f"{name}", auto_archive_duration=60)
    await thread.edit(invitable=False)
    return thread.id

async def reset_votes(context, players: list):
    for player in players:
        player.nvote = 0

async def action_cupidon(cupi_chat, cupidon): #a terminer
    """a terminer"""
    if cupidon == None:
        pass
    else:
        pass

async def action_voyante(context, vovo_chat, voyante, players, n_nuits):
    if voyante == None:
        print("Il n'y a pas de voyante dans la partie")
    elif voyante.state == False:
        print("La voyante est morte")
    else:
        print("Bonjour3")
        bdc = await menu(vovo_chat, players,"Choisissez la personne dont vous voulez révéler le rôle.", voyante)
        await vovo_chat.edit(locked=False)
        await context.channel.set_permissions(voyante.member, send_messages_in_threads=False)
        await role_timer(vovo_chat, 20, n_nuits)
        await bdc.delete()

async def action_lg(context, lg_chat, lgs, players, n_nuits):
    counter = len(lgs)
    for lg in lgs:
        if lg.state == False:
            counter -= 1
    if counter == 0:
        print("Aucun LG en vie")
    else:
        print("Bonjour lg")
        kill_menu = await menu(lg_chat, players,"Choisissez la personne que vous voulez dévorer.", lgs)
        await lg_chat.edit(locked=False)
        await role_timer(lg_chat, 30, n_nuits)
        await kill_menu.delete()


async def annonce_role(context, players: list):
    """Envoie le role de chacun des joueurs par dm et ajoute les joueurs au thread privé"""
    for player in players: #parcours de tous les joueurs en jeu
        await context.send(f"<@{player.id}>") #mentions des joueurs dans le thread privé
        user = await bot.fetch_user(f"{player.id}") #trouve l'utilisateur discord du joueur a partir de l'ID
        channel = await user.create_dm() #créé le dm avec le joueur
        await channel.send(f"Ton rôle est: {player.role}") #envoie du role au joueur par dm

def maxi_vote(players: list):
    """trouve le maximum d'un vote"""
    maxi = 0
    for player in players:
        if player.nvote > maxi:
            maxi = player.nvote
    return maxi

async def resultat_vote(context, players: list, personne=None): #pendre, personne = class player
    """annonce les résultats des votes"""
    cible = None
    if personne == None:
        maxi = maxi_vote(players)
        counter = 0
        for i in range(len(players)):
            if players[i].nvote == maxi:
                counter += 1
                cible = players[i]
        if maxi == 0:
            await context.send(content=f"Personne n'a voté.")
        elif counter == 1:
            await context.send(content=f"<@{cible.id}> a été tué par le village. ({maxi} votes)")
            await asyncio.sleep(2)
            await context.send(content=f"Il était **{cible.role}**.")
            await asyncio.sleep(1)
            cible.state = False
            players.remove(cible)
        else:
            await context.send(content=f"Personne n'est mort. (Égalité)")

    elif type(personne) == list: #LG
        maxi = maxi_vote(players)
        counter = 0
        cible = []
        for i in range(len(players)):
            if players[i].nvote == maxi:
                counter += 1
                cible.append(players[i])
        if maxi == 0:
            await context.send(content=f"Vous avez décidé de ne rien faire cette nuit.")
        elif counter == 1:
            await context.send(content=f"La personne qui va mourir est **{cible[0].name}**.")
            return cible[0]
        else:
            tie_breaker = random.choice(cible)
            await context.send(content=f"La personne qui va mourir est **{tie_breaker.name}**.")
            return tie_breaker


    elif personne.role == "Voyante" and personne.state == True:
        maxi = maxi_vote(players)
        if maxi == 0:
            await context.send(content=f"Vous avez décidé de ne rien faire cette nuit.")
        else:
            for player in players:
                if player.nvote == 1:
                    cible = player
                    return cible

async def cupi_call(cupi_chat, cupidon):
    if cupidon == None:
        pass
    else:
        await cupi_chat.send(f"<@{cupidon.id}>")

async def vovo_call(vovo_chat, voyante):
    if voyante == None:
        pass
    else:
        await vovo_chat.send(f"<@{voyante.id}>")
async def lg_call(lg_chat, lgs):
    """Ajoute les lgs a leur thread""" #enlever commentaire pour vrai test
    # if lgs == []:
    #     raise ValueError("Pas de lgs dans la partie")
    for lg in lgs:
        await lg_chat.send(f"<@{lg.id}>")

async def pf_call(pf_chat, pf):
    if pf == None:
        pass
    else:
        pf_chat.send(f"<@{pf.id}>")

async def soso_call(soso_chat, sorciere):
    if sorciere == None:
        pass
    else:
        soso_chat.send(f"<@{sorciere.id}>")

async def resultat_jour(context, cible_lg, cible_soso, cible_salva, choix_soso):
    cible_lg.state = False
    await context.send(content=f"{cible_lg.id} s'est fait dévoré(e) par les loups cette nuit.")
    await asyncio.sleep(2)
    await context.send(content=f"Il était **{cible_lg.role}**")


@bot.command(aliases=["ct", "cleart"])
async def clear_threads(context):
    print("Clearing Threads...")
    threads = context.channel.threads
    for thread in threads:
        await thread.delete()
    print("Cleared.")

@bot.command()
async def start(context):
    """Starts the game"""
    vc = await vc_members(context) #liste des personnes présentes dans le voc
    n_players = len(vc) #nombre de joueurs dans la partie
    channel = context
    main_thread = await thread(context, "Le Village") #creation du thread privé et renvoie son id
    cupi_thread = await thread(context, "Cupidon")  # créé thread privé du cupidon
    vovo_thread = await thread(context, "Voyante")  # créé thread privé de la voyante
    lg_thread = await thread(context, "Loups-Garous")  # créé thread privé des loups
    pf_thread = await thread(context, "Petite Fille") #créé thread privé de la PF
    soso_thread = await thread(context, "Sorcière")  # créé thread privé de la sorciere

    context = bot.get_channel(main_thread) #changement de context: channel -> thread
    players = await role_assign(context, n_players, vc) #liste de joueur de type class Player
    cupidon, voyante, lgs, pf, sorciere = None, None, [], None, None
    for player in players:
        if player.role == "Cupidon":
            cupidon = player
        if player.role == "Voyante":
            voyante = player
        if player.role == "Loup Garou":
            lgs.append(player)
        if player.role == "Petite Fille":
            pf = player
        if player.role == "Sorciere":
            sorciere = player

    await annonce_role(context, players) #annonce des roles par dm

    cupi_chat = bot.get_channel(cupi_thread) #thread id (cupidon) -> channel (cupidon)
    vovo_chat = bot.get_channel(vovo_thread) #thread id (voyante) -> channel (voyante)
    lg_chat = bot.get_channel(lg_thread) #thread id (loups) -> channel (loups)
    pf_chat = bot.get_channel(pf_thread) #thread id (PF) -> channel (PF)
    soso_chat = bot.get_channel(soso_thread) #thread id (sorciere) -> channel (sorciere)

    await cupi_chat.edit(locked=True)  # vérrouille le chat du cupidon
    await vovo_chat.edit(locked=True)  # vérrouille le chat de la voyante
    await lg_chat.edit(locked=True) #vérrouille le chat des loups
    await pf_chat.edit(locked=True) #vérrouille le chat de la PF
    await soso_chat.edit(locked=True)  # vérrouille le chat de la sorciere

    await cupi_call(cupi_chat, cupidon) #ajoute le cupi a son thread privé
    await vovo_call(vovo_chat, voyante)#ajoute la voyante a son thread privé
    await lg_call(lg_chat, lgs) #ajoute les loups a leur thread privé
    await pf_call(pf_chat, pf) #ajoute la pf a son thread privé
    await soso_call(soso_chat, sorciere) #ajoute la sorciere a son thread privé

    await start_timer(context, 1)  # compteur de départ
    game_state = True #True = le jeu est en cours, False = le jeu est fini

    n_jours = 1
    n_nuits = 1
    await asyncio.sleep(1)
    while game_state == True: #boucle du jeu
        await discussion(context, 1, n_jours)
        n_jours += 1
        await asyncio.sleep(1)
        await vote_village(context, 4, players) #commence le vote du village
        await asyncio.sleep(1)
        await resultat_vote(context, players) #annonce les résultats et la mort de la personne voté
        await reset_votes(context, players) #remet les compteurs de vote a 0
        await context.edit(locked=True) #lock le chat du village pour la nuit
        await asyncio.sleep(1)
        await context.typing() #event qui va déclencher le timer de nuit
        print("Bonjour1")

        await action_voyante(channel, vovo_chat, voyante, players, n_nuits)
        cible_vovo = await resultat_vote(vovo_chat, players, voyante)
        await reset_votes(context, players)
        await vovo_chat.edit(locked=True)

        await context.send("C'est au tour des **Loups-Garous**.")
        await action_lg(channel, lg_chat, lgs, players, n_nuits)
        cible_lg = await resultat_vote(lg_chat, players, lgs)
        await reset_votes(context, players)
        await lg_chat.edit(locked=True)
        if cible_vovo is not None:
            await vovo_chat.send(f"La personne que vous avez espionné est **{cible_vovo.role}**.")
        n_nuits += 1
        game_state = False
    await context.send("Le jeu est terminé !")

@bot.event
async def on_typing(context, user, when):
    bot_id = 1359518949041115320
    if user.id == bot_id:
        time = 51
        await context.send(content=f"## La nuit tombe.")
        msg = await context.send(content=f"### Il reste {time} secondes.")
        for i in range(0, time):
            await asyncio.sleep(1)
            await msg.edit(content=f"### Il reste {time - 1 - i} secondes.")
        await msg.edit(content=f"## Le jour se lève.")
        await asyncio.sleep(1)


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




