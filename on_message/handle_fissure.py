from services.Container import FissureContainer

async def handle_fissure(message, data_collector, world_stat, fissure_caches):
    fissureMessage = await message.channel.send('```Loading...```', delete_after=300)
    fissure_caches[fissureMessage.id] = FissureContainer(fissureMessage, 
    data_collector[message.guild.id]['icon'], 
    data_collector[message.guild.id]['footer'], world_stat.fissures)
    await fissure_caches[fissureMessage.id].setMessage()
    await message.add_reaction('✅')