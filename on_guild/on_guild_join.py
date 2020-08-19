from json import dumps

def set_on_guild_join(client, conn, data_collector, TABLE_NAME):

    @client.event
    async def on_guild_join(guild):
        data = {'prefix':'!', 'footer':None, 'icon':None, 'url': None, 
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
        async with conn.cursor() as cursor:
            sql = 'INSERT INTO {} (serverID, data) VALUES (%s, %s)'.format(TABLE_NAME)
            val = (guild.id, dumps(data))
            await cursor.execute(sql, val)
            await conn.commit()
            await cursor.close()