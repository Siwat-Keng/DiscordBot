from json import dumps

def set_on_guild(bot):

    @bot.client.event
    async def on_guild_join(guild):
        data = {"prefix":None, "footer":None, "icon":None, "url": None, 
        "channels":
            {
                "alert": None, 
                "botcommands": None, 
                "intro": None, 
                "general": None, 
                "ally": None, 
                "clan": None,
                "share": []
            },
            "clan": {},
        "roles": {
            "arbitration": {
                "Interception": None, 
                "Survival": None, 
                "Defense": None,
                "Excavation": None,
                "Defection": None, 
                "Infested Salvage": None, 
                "Disruption": None
                }, 
            "waitingIntro": None, 
            "checkedIntro": None,
            "checkedAlly": None, 
            "VIP": None, 
            "admins": [],
            "notifications": []
        }}
        bot.data_collector[guild.id] = data
        sql = "INSERT INTO {} (serverID, data) VALUES (%s, %s)".format(bot.TABLE_NAME)
        val = (guild.id, dumps(data))
        bot.cursor.execute(sql, val)
        bot.db.commit()

    @bot.client.event
    async def on_guild_remove(guild):
        del bot.data_collector[guild.id]
        sql = "DELETE FROM {} WHERE serverID = %s".format(bot.TABLE_NAME)
        val = (guild.id,)
        bot.cursor.execute(sql, val)                   
        bot.db.commit()
