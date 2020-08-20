from json import dumps
from services.Guild import Guild

def set_on_guild_join(client, conn, data_collector, guilds, world_stat, TABLE_NAME):

    @client.event
    async def on_guild_join(guild):
        data = {'prefix':'!', 'footer':'created by MisterKeng', 
        'icon':'https://img.icons8.com/cute-clipart/64/000000/discord-logo.png', 'url': None, 'invite': None,
        'channels':
            {
                'alert': None, 
                'botcommands': None, 
                'intro': None, 
                'general': None, 
                'ally': None, 
                'clan': None,
                'share': []
            },
        'clan': {},
        'roles': {
            'arbitration': {
                'Interception': None, 
                'Survival': None, 
                'Defense': None,
                'Excavation': None,
                'Defection': None, 
                'Infested Salvage': None, 
                'Disruption': None
                }, 
            'waitingIntro': None, 
            'checkedIntro': None,
            'checkedAlly': None, 
            'VIP': None, 
            'admins': [],
            'notifications': []
        }}
        data_collector[guild.id] = data
        guilds[guild.id] = Guild(client, client.get_guild(guild.id), 
        data_collector, world_stat, conn, TABLE_NAME)
        async with conn.cursor() as cursor:
            sql = 'INSERT INTO {} (serverID, data) VALUES (%s, %s)'.format(TABLE_NAME)
            val = (guild.id, dumps(data))
            await cursor.execute(sql, val)
            await conn.commit()
            await cursor.close()