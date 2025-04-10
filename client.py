import discord

token = 'MTM1OTUxODk0OTA0MTExNTMyMA.GWVATN.B_qihYlFhcYWxI0NMrTVE-sI7-eDvQEKZgz6nM'

client = discord.Client(intents=discord.Intents.all())

client.run(token=token)