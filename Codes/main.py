import discord
from discord.ext import commands
import pandas as pd
import numpy
import defines

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

channel = None
idDic = {}
channelCsv = pd.read_csv('ChannelList.csv', encoding='UTF-8')
reactionMsgCsv = pd.read_csv('ReactionMsgLists.csv', encoding='UTF-8')
keiActivity = discord.Game('점검')


@bot.event
async def on_ready():
    print('케이짱 등장')
    await bot.change_presence(status=discord.Status.do_not_disturb, activity=keiActivity)
    #await init()


@bot.command(name="안녕")
async def hello(ctx):
    await ctx.send('안녕하세요')

async def command_param_count(ctx, len, min, max):
    if (len < min):
        await ctx.send(f'에러. 명령어 인자가 너무 적습니다.')
        return -1
    elif (len > max):
        await ctx.send(f'에러. 명령어 인자가 너무 많습니다.')
        return 1
    return 0


@bot.command(name='역할자판기-채널등록')
async def register_role_channel(ctx, *args):
    global channelCsv
    if (len(args) == 0):
        await ctx.send(f'도움말 추가 예정')
        return
    if (await command_param_count(ctx, len(args), 1, 1) != 0):
        return
    
    if (channelCsv[channelCsv['channel_id']==numpy.int64(args[0][2:-1])]['channel_id'].values[0] != None):
        await ctx.send(f'{args[0]}: 해당 채널은 이미 역할자판기 채널로 등록되어있습니다.')
        return
    channelCsv = pd.concat([channelCsv, pd.DataFrame({'guild_id' : [ctx.guild.id], 'channel_id' : [args[0][2:-1]]})])
    channelCsv.to_csv('ChannelList.csv', mode='w')
    await ctx.send(f'{args[0]}: 해당 채널을 역할자판기 채널로 등록했습니다.')


@bot.command(name='역할자판기-추가')
async def add_role(ctx, *args):
    global reactionMsgCsv, channelCsv
    if (len(args) == 0):
        await ctx.send(f'도움말 추가 예정')
        return
    if (await command_param_count(ctx, len(args), 2, 2) != 0):
        return
    
    guildId = ctx.guild.id
    channelId = channelCsv[channelCsv['guild_id']==numpy.int64(guildId)]['channel_id'].values[0]
    if (channelId == None):
        await ctx.send(f'본 서버에 등록된 역할자판기용 채널이 하나도 존재하지 않습니다. `/역할자판기-채널등록` 명령어를 사용해서 채널 등록을 먼저 진행해주세요.')
        return
    messageId = args[0].split('/')[-1]
    roleId = args[1][3:-1]
    if (reactionMsgCsv[reactionMsgCsv['message_id']==numpy.int64(messageId)]['message_id'].values.size > 0):
        await ctx.send(f'{args[0]}: 해당 메세지는 이미 역할자판기 메세지로 등록되어있습니다.')
        return
    if (reactionMsgCsv[reactionMsgCsv['role_id']==numpy.int64(roleId)]['role_id'].values.size > 0):
        await ctx.send(f'{args[1]}: 해당 역할은 이미 역할자판기에 등록되어있습니다.')
        return
    
    reactionMsgCsv = pd.concat([reactionMsgCsv, pd.DataFrame({'message_id' : [messageId], 'role_id' : [roleId]})])
    reactionMsgCsv.to_csv('ReactionMsgLists.csv', mode='w')
    await ctx.send(f'{args[0]} {args[1]}: 해당 메세지와 역할을 역할자판기에 등록했습니다.')


@bot.event
async def on_raw_reaction_add(ctx):
    if ctx.member.bot:
        return
    if idDic[ctx.message_id] == None:
        return
    guild = bot.get_guild(ctx.guild_id)
    if str(ctx.emoji.name) == '✅':
        await channel.get_partial_message(ctx.message_id).remove_reaction('✅', ctx.member)
        await ctx.member.add_roles(guild.get_role(idDic[ctx.message_id]))
    elif str(ctx.emoji.name) == '❌':
        await channel.get_partial_message(ctx.message_id).remove_reaction('❌', ctx.member)
        await ctx.member.remove_roles(guild.get_role(idDic[ctx.message_id]))


async def init():
    global guild, channel, msgId_list, idDic
    guild = bot.get_guild(defines.guildId)
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

bot.run(open('TOKEN.txt', "r").read())