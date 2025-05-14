import discord
from discord.ext import commands, tasks
import asyncio
import random
from ast import literal_eval
from timer import Timer
from select_menu import SelectView, SelectVote
from cupi_select import SelectViewCupi, SelectLove
from player import Player
from button_menu import ButtonMenu

token = 'MTM1OTUxODk0OTA0MTExNTMyMA.GWVATN.B_qihYlFhcYWxI0NMrTVE-sI7-eDvQEKZgz6nM'

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

threads = {}

dico_lg = {}

# @bot.command() # Create a slash command
async def button(context, potion_vie, cible_lg):
    print('button')
    bouton_soso = ButtonMenu(potion_vie=potion_vie, cible_lg=cible_lg)
    potion_vie = await context.send(content=f"**{cible_lg.name}** est visé(e) par les loups-garous ce soir.",
                                    view=bouton_soso) # Send a message with our View class that contains the button
    #print(bouton_soso.button_callback1)
    print(f'fonction bouton : {bouton_soso.cible_lg}, reste :')
    potion_vie = bouton_soso.potion_vie
    return bouton_soso
    #return potion_vie

async def menu(context, players: list, text: str, player=None): #Select est la classe a afficher, player est le joueur avec un role qui agit de nuit s'il y en a un
    """fonction pour menu deroulant"""
    print("appelle menu")
    vote_menu = await context.send(content=text, view=SelectView(players=players, player=player))
    return vote_menu

async def cupi_menu(context, players: list, dico, text: str):
    """fonction pour menu deroulant du cupi"""
    print("appelle menu cupi")
    menu_cupi = SelectViewCupi(players=players, dico=dico)
    message_menu = await context.send(content=text, view=menu_cupi)
    return message_menu, menu_cupi


async def user_to_player(user, players: list):
    for player in players:
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
    for _ in range(len(members)):
        role = random.choice(roles)
        roles.remove(role)
        member = random.choice(members)
        members.remove(member)
        liste.append(Player(member.name, member.id, role, True, member = member))
    # print(f"liste_player: {liste[0].name}")
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
    threads[f'{name.lower()}_thread'] = thread.id  # Stocker l'ID du thread dans le dictionnaire
    return thread.id

async def reset_votes(context, players: list):
    for player in players:
        player.nvote = 0
        player.previous_vote = None

async def action_cupidon(context, cupi_chat, cupidon, players: list, dico: dict, n_nuits):
    if cupidon == None:
        print("Il n'y a pas de cupidon dans la partie")
    elif cupidon.state == False:
        print("Le cupidon est mort")
    else:
        #await context.send("C'est au tour du **Cupidon**")
        cupi_channel = bot.get_channel(threads.get('cupidon_thread'))
        await cupi_channel.send(f"**C'est au tour du Cupidon**")
        print('cupi')
        message_menu, affichage_menu = await cupi_menu(cupi_chat, players, dico,
                                            text="Choisissez les deux joueurs qui deviendront les membres du couple. Si vous ne choisissez pas, il sera choisi aléatoirement.")
        await cupi_chat.edit(locked=False)
        #await context.channel.set_permissions(cupidon.member, send_messages_in_threads=False)
        cupi_timer = Timer(cupi_chat, 15, n_nuits)
        await cupi_timer.role_timer()
        await message_menu.delete()
        print(f'Couple sélectionné : {affichage_menu.selectlove.couple}')

        if affichage_menu.selectlove.couple == []:
            random_choice = []
            for i in players:
                random_choice.append(i)
            for i in range(2):
                amoureux = random.choice(random_choice)
                affichage_menu.selectlove.couple.append(amoureux)
                random_choice.remove(amoureux)
            print(f'SelectMenu None : {affichage_menu.selectlove.couple}')

        return affichage_menu.selectlove

async def action_voyante(context, vovo_chat, voyante, players, n_nuits):
    if voyante == None:
        print("Il n'y a pas de voyante dans la partie")
    elif voyante.state == False:
        print("La voyante est morte")
    else:
        await context.send("C'est au tour de la **Voyante**.")
        print("vovo")
        bdc = await menu(vovo_chat, players,"Choisissez la personne dont vous voulez révéler le rôle.", voyante)
        await vovo_chat.edit(locked=False)
        #await context.channel.set_permissions(voyante.member, send_messages_in_threads=False)
        vovo_timer = Timer(vovo_chat, 15, n_nuits)
        await vovo_timer.role_timer()
        await bdc.delete()

async def action_lg(context, lg_chat, lgs, players, n_nuits):
    counter = len(lgs)
    for lg in lgs:
        if lg.state == False:
            counter -= 1
    if counter == 0:
        print("Aucun LG en vie")
    else:
        await context.send("C'est au tour des **Loups-Garous**.")
        print("lgs")
        kill_menu = await menu(lg_chat, players,"Choisissez la personne que vous voulez dévorer.", lgs[0])
        await lg_chat.edit(locked=False)
        lg_timer = Timer(lg_chat, 15, n_nuits)
        await lg_timer.role_timer()
        await kill_menu.delete()

async def action_sorciere(context, soso_chat, sorciere, players, n_nuits, potion_vie, potion_mort, cible_lg):
    pdv_menu = None
    if sorciere == None:
        print("Il n'y a pas de sorcière dans la partie")
    elif sorciere.state == False:
        print("La sorcière est morte")
    else:
        await context.send("C'est au tour de la **Sorcière**.")
        print("soso")
        if cible_lg is None:
            await soso_chat.send(f"Aucune personne n'a été ciblé ce soir.")
            print("pas de cible lg")
        else:
            if potion_vie == False:  # potion vie deja utilisé
                print("plus de potion de vie")
                pdv_menu = None
                await soso_chat.send(content=f"Vous avez déjà utilisé la potion de vie.")

            else: #potion vie pas encore utilisé
                pdv_menu = await button(context=soso_chat, potion_vie=potion_vie, cible_lg=cible_lg)
                print(pdv_menu.cible_lg)

        if potion_mort == False: #potion mort deja utilisé
            print("plus de potion de mort")
            pdm_menu = 0
            await soso_chat.send(content=f"Vous avez déjà utilisé la potion de mort.")
        else: #potion mort pas encore utilisé
            pdm_menu = await menu(soso_chat, players, "Selectionnez la personne qui recevra la potion de mort.", sorciere) #potion de mort
            print("pdm")

            await soso_chat.edit(locked=False)
            # await context.channel.set_permissions(sorciere.member, send_messages_in_threads=False)
            soso_timer = Timer(soso_chat, 5, n_nuits)
            await soso_timer.role_timer()
            if pdv_menu is not None:
                return pdv_menu.cible_lg, pdv_menu.potion_vie
            else:
                return cible_lg, False


async def dico_joueurs(context, players):
    dico = {}
    for player in players:
        dico[player.name] = player
    return dico



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


async def cible_vote(context, players, voteur):
    """annonce les résultats des votes ou renvoie la cible selon les cas"""
    cible = []
    maxi = maxi_vote(players)
    counter = 0
    for i in range(len(players)):
        if players[i].nvote == maxi:
            counter += 1
            cible.append(players[i])

    if maxi == 0: #aucun vote
        if voteur == None:
            await context.send(content=f"Le village a décidé de ne pas voter.")
        elif type(voteur) == list:  # LG
            await context.send(content=f"Vous avez décidé de ne rien faire cette nuit.")
        elif voteur.role == "Voyante":
            await context.send(content=f"Vous avez décidé de ne rien faire cette nuit.")
        elif voteur.role == "Sorciere":
            await context.send(content=f"Vous avez décidé conserver votre potion de mort pour une prochaine nuit.")
        elif voteur.role == "Cupidon":
            await context.send(content=f"Vous avez décidé de laisser le hasard choisir votre couple.")
            return cible


    elif counter == 1: #1 personne voté en majorité
        if voteur == None:
            await context.send(content=f"<@{cible[0].id}> a été tué par le village. ({maxi} vote(s))")
            await asyncio.sleep(2)
            await context.send(content=f"Son rôle était **{cible[0].role}**.")
            await asyncio.sleep(1)
            cible[0].state = False
            players.remove(cible[0])
        elif type(voteur) == list:  # LG
            await context.send(content=f"La personne qui va mourir est **{cible[0].name}**.")
            return cible[0]
        elif voteur.role == "Voyante":
            await context.send(content=f"La personne dont vous allez révéler le rôle est **{cible[0].name}**.")
            return cible[0]
        elif voteur.role == "Sorciere":
            await context.send(content=f"La personne qui recevra la potion de mort est **{cible[0].name}**.")
            return cible[0]
        elif voteur.role == "Cupidon":
            await context.send(content=f"Vous n'avez choisi qu'une personne (**{cible[0].name}**), la seconde sera choisi aléatoirement")
            return cible[0] #une des deux personnes du couple


    else: #égalité
        if voteur == None:
            await context.send(content=f"Personne n'est mort. (Égalité)")
        elif type(voteur) == list:  # LG
            tie_breaker = random.choice(cible)
            await context.send(content=f"La personne qui va mourir est **{tie_breaker.name}**.")
            return tie_breaker

async def call(role_chat, player):
    if player == None:
        pass
    elif type(player) == list:
        # if lgs == []:
        #     raise ValueError("Pas de lgs dans la partie")
        for lg in player:
            await role_chat.send(f"<@{lg.id}>")
    else:
        await role_chat.send(f"<@{player.id}>")

async def lock(role_chats):
    for role_chat in role_chats:
        await role_chat.edit(locked=True)


async def ping_couple(couple_chat, select_love):
    if select_love is not None:
        select_love.couple[0].amour = select_love.couple[1]
        select_love.couple[0].camps = 'Couple'
        select_love.couple[1].amour = select_love.couple[0]
        select_love.couple[1].camps = 'Couple'
        for i in range(2):
            print(select_love.couple)
            await call(couple_chat, select_love.couple[i])
        print(f'Amour 1 : {select_love.couple[0].amour}')
        print(f'Amour 2 : {select_love.couple[1].amour}')
        await couple_chat.send(content=f"Le **Cupidon**, vous a choisi pour son **Couple**, vous avez accès à ce chat privé afin de communiquer jour comme nuit.")


async def annonce_jour(context, cible_lg=None, cible_soso=None, players=[], cupidon=None):
    morts = []
    if cible_lg is not None: #cible lg existe
        print(cible_lg)
        cible_lg.state = False
        morts.append(cible_lg)
        await context.send(content=f"<@{cible_lg.id}> s'est fait dévoré(e) par les loups cette nuit.")
        await asyncio.sleep(2)
        await context.send(content=f"Il était **{cible_lg.role}**")
        await cible_lg.member.edit(mute=True)
        players.remove(cible_lg)
        if cible_lg.amour is not None:
            cible_lg.amour.state = False
            morts.append(cible_lg.amour)
            await context.send(content=f"<@{cible_lg.amour.id}> est mort par chagrin d'amour")
            await asyncio.sleep(2)
            await context.send(content=f"Il était **{cible_lg.amour.role}**")
            await cible_lg.amour.member.edit(mute=True)
            players.remove(cible_lg.amour)
            cupidon.camps = 'Village'

    if cible_soso is not None: #cible soso existe
        cible_soso.state = False
        morts.append(cible_soso)
        await context.send(content=f"<@{cible_soso.id}> s'est fait tué(e) par la sorcière cette nuit.")
        await asyncio.sleep(2)
        await context.send(content=f"Il était **{cible_soso.role}**")
        await cible_soso.member.edit(mute=True)
        players.remove(cible_soso)
        if cible_soso.amour is not None:
            cible_soso.amour.state = False
            morts.append(cible_soso.amour)
            await context.send(content=f"<@{cible_soso.amour} est mort par chagrin d'amour")
            await asyncio.sleep(2)
            await context.send(content=f"Il était **{cible_soso.amour.role}**")
            await cible_soso.amour.member.edit(mute=True)
            players.remove(cible_soso.amour)
            cupidon.camps = 'Village'
    if morts == []: #cas où personne n'a été ciblé
        await context.send(content=f"Personne n'est mort cette nuit.")
    else: #cas où au moins une personne a été ciblée
        for mort in morts:
            await mort.member.edit(mute=True)

async def nom_façade(context, lgs):
    noms = ["Loup-Garou Gentil", "Loup-Garou Bourré", "Loup-Garou Affamé"]
    for lg in lgs:
        nom = random.choice(noms)
        noms.remove(nom)
        dico_lg[lg.name] = nom


@bot.command()
async def start(context):
    """Starts the game"""
    print("Starting...")
    dico_lg = {}
    await clear_threads(context)
    vc = await vc_members(context) #liste des personnes présentes dans le voc
    n_players = len(vc) #nombre de joueurs dans la partie

    main_thread = await thread(context, "Le Village") #creation du thread privé et renvoie son id
    cupi_thread = await thread(context, "Cupidon")  # créé thread privé du cupidon
    vovo_thread = await thread(context, "Voyante")  # créé thread privé de la voyante
    lg_thread = await thread(context, "Loups-Garous")  # créé thread privé des loups
    pf_thread = await thread(context, "Petite Fille") #créé thread privé de la PF
    soso_thread = await thread(context, "Sorcière")  # créé thread privé de la sorciere
    couple_thread = await thread(context, "Couple")

    print(threads)

    channel = context
    context = bot.get_channel(main_thread) #changement de context: channel -> thread
    players = await role_assign(context, n_players, vc) #liste de joueur de type class Player
    dico_players = await dico_joueurs(context, players)

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
    roles_nuit = [cupidon, voyante, lgs, pf, sorciere]
    await annonce_role(context, players) #annonce des roles par dm

    await nom_façade(context, lgs)

    cupi_chat = bot.get_channel(cupi_thread) #thread id (cupidon) -> channel (cupidon)
    vovo_chat = bot.get_channel(vovo_thread) #thread id (voyante) -> channel (voyante)
    lg_chat = bot.get_channel(lg_thread) #thread id (loups) -> channel (loups)
    pf_chat = bot.get_channel(pf_thread) #thread id (PF) -> channel (PF)
    soso_chat = bot.get_channel(soso_thread) #thread id (sorciere) -> channel (sorciere)
    couple_chat = bot.get_channel(couple_thread)
    role_chats = [cupi_chat, vovo_chat, lg_chat, pf_chat, soso_chat]
    await lock(role_chats) #lock tous les chats sauf le main

    for i in range(len(role_chats)):
        await call(role_chats[i], roles_nuit[i]) #ajoute les roles a leur thread

    start = Timer(context, 2, None)
    await start.start_timer() # compteur de départ

    dead_ppl = []
    potion_vie = True
    potion_mort = True
    n_jours = 1
    n_nuits = 1
    temps_discussion = 12
    await asyncio.sleep(1)

    #PREMIER ROUND

    #DISCUSSION
    tdiscu = Timer(context, temps_discussion-10, n_jours)
    await tdiscu.discussion()
    n_jours += 1
    n_nuits += 1
    await asyncio.sleep(1)

    #CUPIDON
    select_love = await action_cupidon(channel, cupi_chat, cupidon, players, dico_players, n_nuits) #renvoie l'objet de la class selectviewcupi
    await cupi_chat.edit(locked=True)
    await ping_couple(couple_chat, select_love)

    #NUIT
    await context.edit(locked=True) #lock le chat du village pour la nuit
    await asyncio.sleep(1)
    await context.typing() #event qui va déclencher le timer de nuit
    await asyncio.sleep(1)

    #VOYANTE
    await action_voyante(context, vovo_chat, voyante, players, n_nuits) #vovo choisis cible
    await vovo_chat.edit(locked=True) #lock le chat de la vovo
    cible_vovo = await cible_vote(vovo_chat, players, voyante) #cible est récup ici (type class player)
    await reset_votes(context, players) #vote reset

    #LOUP GAROU
    await action_lg(context, lg_chat, lgs, players, n_nuits) #lgs choisissent cible
    await lg_chat.edit(locked=True) #lock chat des lgs
    cible_lg = await cible_vote(lg_chat, players, lgs)
    await reset_votes(context, players) #vote reset

    #SORCIERE
    if sorciere is not None:
        cible_lg, potion_vie = await action_sorciere(context=context, soso_chat=soso_chat, sorciere=sorciere, players=players, n_nuits=n_nuits,
                                         potion_vie=potion_vie, potion_mort=potion_mort, cible_lg=cible_lg)
    cible_soso = await cible_vote(soso_chat, players, sorciere)
    await soso_chat.edit(locked=True)

    #ANNONCE DES MORTS
    await annonce_jour(context, cible_lg, cible_soso, players, cupidon)
    if cible_vovo is not None:
        await vovo_chat.send(f"La personne que vous avez espionné est **{cible_vovo.role}**.")

    game_state = True  # True = le jeu est en cours, False = le jeu est fini
    #BOUCLE DE JEU
    while game_state == True:

        #DISCUSSION
        tdiscu = Timer(context, temps_discussion-10, n_jours)
        await tdiscu.discussion()
        n_jours += 1
        await asyncio.sleep(1)

        #VOTE
        vote = Timer(context, 1, n_jours=0)
        await vote.vote_village(players=players) #commence le vote du village
        await asyncio.sleep(1)
        await cible_vote(context, players, None) #annonce les résultats et la mort de la personne voté
        await reset_votes(context, players) #remet les compteurs de vote a 0

        #NUIT
        await context.edit(locked=True) #lock le chat du village pour la nuit
        await asyncio.sleep(1)
        await context.typing() #event qui va déclencher le timer de nuit
        await asyncio.sleep(1)

        #VOYANTE
        await action_voyante(context, vovo_chat, voyante, players, n_nuits) #vovo choisis cible
        await vovo_chat.edit(locked=True) #lock le chat de la vovo
        cible_vovo = await cible_vote(vovo_chat, players, voyante) #cible est récup ici (type class player)
        await reset_votes(context, players) #vote reset

        #LOUP GAROU
        await action_lg(context, lg_chat, lgs, players, n_nuits) #lgs choisissent cible
        await lg_chat.edit(locked=True) #lock chat des lgs
        cible_lg = await cible_vote(lg_chat, players, lgs)
        await reset_votes(context, players) #vote reset

        #SORCIERE
        if sorciere is not None:
            cible_lg, potion_vie = await action_sorciere(context=context, soso_chat=soso_chat, sorciere=sorciere, players=players, n_nuits=n_nuits,
                                           potion_vie=potion_vie, potion_mort=potion_mort, cible_lg=cible_lg)
        cible_soso = await cible_vote(soso_chat, players, sorciere)
        await soso_chat.edit(locked=True)

        #ANNONCE DES MORTS
        await annonce_jour(context, cible_lg, cible_soso, players, cupidon)
        if cible_vovo is not None:
            await vovo_chat.send(f"La personne que vous avez espionné est **{cible_vovo.role}**.")

        n_nuits += 1

        game_state = await is_game_over(context, players, lgs)
    print("Program has ended without errors.")

async def is_game_over(context, players, lgs):
    lgs_vivants = 0
    players_vivants = 0
    for lg in lgs:
        if lg.state == True:
            lgs_vivants += 1
    for player in players:
        if player.state == True:
            players_vivants += 1

    if players_vivants - lgs_vivants == lgs_vivants:
        await context.send("La partie est terminée!")
        await context.send("Les Loups-Garous ont gagné!")
        return False

    elif lgs_vivants == 0:
        await context.send("La partie est terminée!")
        await context.send("Les Villageois ont gagné!")
        return False

    else:
        return True




@bot.event
async def on_typing(context, user, when): #night timer
    bot_id = 1359518949041115320
    if user.id == bot_id:
        night = Timer(context, 30, 1)
        await night.night_timer()

@bot.command(aliases=["ct", "cleart", "clear"])
async def clear_threads(context):
    print("Clearing Threads...")
    l_threads = context.channel.threads
    threads = {}
    n_jours = 1
    print(l_threads)
    for thread in l_threads:
        try:
            print(f"Deleting thread: {thread.name} (ID: {thread.id})")
            await thread.delete()
        except discord.errors.NotFound:
            print(f"Thread {thread.id} not found, skipping...")
        except discord.errors.Forbidden:
            print(f"Permission denied for thread {thread.id}, skipping...")
        except Exception as e:
            print(f"Error deleting thread {thread.id}: {e}")
    print("Cleared.")




@bot.command()
async def mut(context, member: discord.Member):
    await member.edit(mute=True)

@bot.command(pass_context = True)
async def mute(ctx, member: discord.Member):
    if ctx.message.author.server_permissions.administrator:
        role = discord.utils.get(member.server.roles, name='Muted')
        await ctx.add_roles(member, role)
        embed=discord.Embed(title="User Muted!", description="**{0}** was muted by **{1}**!".format(member, ctx.message.author), color=0xff00f6)
        await ctx.send(embed=embed)
    else:
        embed=discord.Embed(title="Permission Denied.", description="You don't have permission to use this command.", color=0xff00f6)
        await ctx.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Vérifiez si le message est une commande
    if message.content.startswith('!start') or message.content.startswith('!ct') or message.content.startswith('!compo'):
        await bot.process_commands(message)
        return

    # Vérifiez si le message provient du thread "lg"
    if message.channel.id == threads['loups-garous_thread']:
        # Retransmettre le message dans le thread "pf"
        pf_channel = bot.get_channel(threads.get('petite fille_thread'))
        print(pf_channel)
        if pf_channel:
            await pf_channel.send(f"**{dico_lg[message.author.name]}**: \n {message.content} \n ‎ ")


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