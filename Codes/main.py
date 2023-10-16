import discord
from discord.ext import *
import defines

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

guild = None
channel = None
idDic = {}

@client.event
async def on_ready():
    print('케이짱 등장')
    await init()
    

@client.event
async def on_message(message):
    if message.content.startswith('//안녕'):
        await message.channel.send('안녕하세요. 케이입니다.')

@client.event
async def on_raw_reaction_add(payload):
    if payload.member.bot:
        return
    if idDic[payload.message_id] == None:
        return
    guild = client.get_guild(payload.guild_id)
    if str(payload.emoji.name) == '✅':
        await channel.get_partial_message(payload.message_id).remove_reaction('✅', payload.member)
        await payload.member.add_roles(guild.get_role(idDic[payload.message_id]))
    elif str(payload.emoji.name) == '❌':
        await channel.get_partial_message(payload.message_id).remove_reaction('❌', payload.member)
        await payload.member.remove_roles(guild.get_role(idDic[payload.message_id]))

async def init():
    global guild, channel, msgId_list, idDic
    guild = client.get_guild(defines.guildId)
    channel = guild.get_channel(defines.channelId)

    idDic[defines.msgId_c] = defines.role_c
    idDic[defines.msgId_cpp] = defines.role_cpp
    idDic[defines.msgId_csharp] = defines.role_csharp
    idDic[defines.msgId_java] = defines.role_java
    idDic[defines.msgId_js] = defines.role_js
    idDic[defines.msgId_python] = defines.role_python
    await channel.get_partial_message(defines.msgId_c).add_reaction('✅')
    await channel.get_partial_message(defines.msgId_c).add_reaction('❌')
    await channel.get_partial_message(defines.msgId_cpp).add_reaction('✅')
    await channel.get_partial_message(defines.msgId_cpp).add_reaction('❌')
    await channel.get_partial_message(defines.msgId_csharp).add_reaction('✅')
    await channel.get_partial_message(defines.msgId_csharp).add_reaction('❌')
    await channel.get_partial_message(defines.msgId_java).add_reaction('✅')
    await channel.get_partial_message(defines.msgId_java).add_reaction('❌')
    await channel.get_partial_message(defines.msgId_js).add_reaction('✅')
    await channel.get_partial_message(defines.msgId_js).add_reaction('❌')
    await channel.get_partial_message(defines.msgId_python).add_reaction('✅')
    await channel.get_partial_message(defines.msgId_python).add_reaction('❌')

client.run(open('TOKEN.txt', "r").read())