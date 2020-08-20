from services.Container import PartyContainer

async def handle_party(client, message, data_collector, party_caches):
    target = message.content[len('{}party'\
        .format(data_collector[message.guild.id]['prefix'])):].strip()
    channel = client.get_channel(data_collector[message.guild.id]['channels']\
        ['general'])
    partyMessage = await channel.send(content='```...Loading...```', delete_after=1800) 
    party_caches[partyMessage.id] = PartyContainer(partyMessage, target, 
    message.author, data_collector[message.guild.id]['footer'], 
    data_collector[message.guild.id]['icon'])      
    await party_caches[partyMessage.id].setMessage()