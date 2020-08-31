from discord import Embed
from difflib import get_close_matches

COMMANDS = {'drop', 'price', 'help', 'riven', 'party', 'fissure', 'build'}

async def handle_help(client, message, data_collector):
    channel = client.get_channel(data_collector[message.guild.id]['channels']['botcommands'])
    embed = Embed(title='Hello {}'.format(message.author.name), 
    description = 'สามารถใช้คำสั่งต่าง ๆ ต่อไปนี้ได้ที่ห้อง {}'.format(channel.name), 
    url = data_collector[message.guild.id]['url'], color=0x00ff00)
    embed.add_field(name= '{}price <item>'.format(data_collector[message.guild.id]['prefix']), 
    value='บอทจะ search ราคา item ตามชื่อ (จาก Warframe Market)', inline=False)
    embed.add_field(name= '{}drop <item>'.format(data_collector[message.guild.id]['prefix']), 
    value='บอทจะ search ตำแหน่งที่ดรอป ตามชื่อ (จาก Warframe Wiki)', inline=False)
    embed.add_field(name= '{}party <message>'.format(data_collector[message.guild.id]['prefix']), 
    value='บอทจะสร้างข้อความเพื่อหา Squad Member', inline=False)
    embed.add_field(name= '{}fissure'.format(data_collector[message.guild.id]['prefix']), 
    value='บอทจะแสดง mission void fissure ปัจจุบัน', inline=False)
    embed.add_field(name= '{}build <item>'.format(data_collector[message.guild.id]['prefix']), 
    value='บอทจะ search build จาก overframe.gg', inline=False)
    embed.add_field(name= '{}riven <weapon> <+stat +stat +stat -stat> <price>'\
        .format(data_collector[message.guild.id]['prefix']), 
    value='บอทจะ live search riven', inline=False)
    embed.set_footer(text=data_collector[message.guild.id]['footer'], 
    icon_url=data_collector[message.guild.id]['icon'])
    await message.author.send(embed=embed)
    await message.add_reaction('✅')

async def predict_command(message, data_collector):
    if message.content.startswith(data_collector[message.guild.id]['prefix']):
        command = message.content[len(data_collector[message.guild.id]['prefix']):].split()[0]
        predicted = get_close_matches(command, COMMANDS, len(COMMANDS))
        if len(predicted) > 0:
            embed = Embed(title='The most similar commands', 
            description = 'คำสั่ง {}{} ไม่มีในระบบ คำสั่งที่คล้าย ได้แก่'.format(\
                data_collector[message.guild.id]['prefix'], command), color=0x00ff00)
            for pred in predicted:
                embed.add_field(name='[Suggested Command]',value='{}{}'\
                    .format(data_collector[message.guild.id]['prefix'], pred), inline=False)
            embed.set_footer(text=data_collector[message.guild.id]['footer'], 
            icon_url=data_collector[message.guild.id]['icon']) 
            await message.channel.send(embed=embed)