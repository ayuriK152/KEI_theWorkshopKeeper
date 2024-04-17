import discord
from discord.ext import commands
import pandas as pd
import numpy
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

channelCsv = pd.read_csv('ChannelList.csv', encoding='UTF-8')
reactionMsgCsv = pd.read_csv('ReactionMsgLists.csv', encoding='UTF-8')
watingRoleCsv = pd.read_csv('WaitingRoleList.csv', encoding='UTF-8')
keiActivity = discord.Game('정상작동')


async def command_param_count(ctx, len, min, max):
    if len < min:
        await ctx.send(f'에러. 명령어 인자가 너무 적습니다.')
        return -1
    elif len > max:
        await ctx.send(f'에러. 명령어 인자가 너무 많습니다.')
        return 1
    return 0


@bot.event
async def on_ready():
    print('케이짱 등장')
    await bot.change_presence(status=discord.Status.online, activity=keiActivity)
    await init()


# 도움말 (추가 예정)
@bot.command(name="명령어")
async def help(ctx):
    await ctx.send('안녕이나 치세요')


# 잡다한 명령어는 다 여기다가
@bot.command(name="안녕")
async def hello(ctx):
    await ctx.send('안녕하세요')


# 여기부터 어드민 전용 기능들, 도움말에 사용법이 노출되어선 안됨
# 명령어 입력한 사람이 어드민인지 확인하는 기능도 있어야할듯
@bot.command(name='역할자판기-채널등록')
async def register_role_channel(ctx, *args):
    global channelCsv
    if len(args) == 0:
        await ctx.send(f'도움말 추가 예정')
        return
    
    if await command_param_count(ctx, len(args), 1, 1) != 0:
        return
    
    if channelCsv[channelCsv['channel_id'] == numpy.int64(args[0][2:-1])]['channel_id'].values.size != 0:
        await ctx.send(f'{args[0]}: 해당 채널은 이미 역할자판기 채널로 등록되어있습니다.')
        return
    
    channelCsv = pd.concat([channelCsv, pd.DataFrame({'guild_id' : [ctx.guild.id], 'channel_id' : [args[0][2:-1]]})])
    channelCsv.to_csv('ChannelList.csv', mode='w', index=None)
    await ctx.send(f'{args[0]}: 해당 채널을 역할자판기 채널로 등록했습니다.')


# 역할자판기 메세지 할당 메소드
@bot.command(name='역할자판기-추가')
async def add_role(ctx, *args):
    global reactionMsgCsv, channelCsv

    if len(args) == 0:
        await ctx.send(f'도움말 추가 예정')
        return
    
    if await command_param_count(ctx, len(args), 2, 2) != 0:
        return
    
    guildId = ctx.guild.id
    channelId = channelCsv[channelCsv['guild_id'] == numpy.int64(guildId)]['channel_id'].values[0]

    if channelId is None:
        await ctx.send(f'본 서버에 등록된 역할자판기용 채널이 하나도 존재하지 않습니다. `/역할자판기-채널등록` 명령어를 사용해서 채널 등록을 먼저 진행해주세요.')
        return
    
    inputMsgId = args[0].split('/')[-1]
    inputRoleId = args[1][3:-1]

    if reactionMsgCsv[reactionMsgCsv['message_id'] == numpy.int64(inputMsgId)]['message_id'].values.size > 0:
        await ctx.send(f'{args[0]}: 해당 메세지는 이미 역할자판기 메세지로 등록되어있습니다.')
        return
    
    if reactionMsgCsv[reactionMsgCsv['role_id'] == numpy.int64(inputRoleId)]['role_id'].values.size > 0: 
        await ctx.send(f'{args[1]}: 해당 역할은 이미 역할자판기에 등록되어있습니다.')
        return
    
    print(reactionMsgCsv)
    pd.concat([reactionMsgCsv, pd.DataFrame({'channel_id' : [channelId], 'message_id' : [inputMsgId], 'role_id' : [inputRoleId]})]).to_csv('ReactionMsgLists.csv', mode='w', index=None)
    reactionMsgCsv = pd.read_csv('ReactionMsgLists.csv', encoding='UTF-8')
    print(reactionMsgCsv)

    guild = bot.get_guild(guildId)
    channel = guild.get_channel(channelId)

    print(channel.get_partial_message(inputMsgId))
    
    await channel.get_partial_message(inputMsgId).add_reaction('✅')
    await channel.get_partial_message(inputMsgId).add_reaction('❌')
    await ctx.send(f'{args[0]} {args[1]}: 해당 메세지와 역할을 역할자판기에 등록했습니다.')


# 이모지 반응 역할 부여 메소드
@bot.event
async def on_raw_reaction_add(ctx):
    if ctx.member.bot:
        return
    
    guild = bot.get_guild(ctx.guild_id)
    channelId = channelCsv[channelCsv['guild_id']==numpy.int64(ctx.guild_id)]['channel_id'].values
    messageId = reactionMsgCsv[reactionMsgCsv['message_id']==numpy.int64(ctx.message_id)]['message_id'].values

    if channelId.size == 0:
        print('channel.size == 0')
        return
    if messageId.size == 0:
        print('messageId.size == 0')
        return
    
    for i in range(channelId.size):
        try:
            channel = guild.get_channel(channelId[i])
            role = guild.get_role(reactionMsgCsv[reactionMsgCsv['message_id'] == numpy.int64(ctx.message_id)]['role_id'].values[0])

            if str(ctx.emoji.name) == '✅':
                await channel.get_partial_message(ctx.message_id).remove_reaction('✅', ctx.member)
                await ctx.member.add_roles(role)
            elif str(ctx.emoji.name) == '❌':
                await channel.get_partial_message(ctx.message_id).remove_reaction('❌', ctx.member)
                await ctx.member.remove_roles(role)
                
            if guild.id in watingRoleCsv['guild_id'].values:
                watingRoleId = watingRoleCsv[watingRoleCsv['guild_id'] == numpy.int64(guild.id)]['role_id'].values[0]
                if guild.get_role(watingRoleId) in ctx.member.roles:
                    await ctx.member.remove_roles(guild.get_role(watingRoleId))
            break
        except:
            continue


# 봇 초기화 메소드, 시작할 때 한 번 실행
async def init():
    channelIds = channelCsv['channel_id'].values
    for i in range(channelIds.size):
        guild = bot.get_guild(channelCsv[channelCsv['channel_id']==numpy.int64(channelIds[i])]['guild_id'].values[0])
        channel = guild.get_channel(channelIds[i])
        msgIds = reactionMsgCsv[reactionMsgCsv['channel_id']==numpy.int64(channelIds[i])]['message_id'].values
        for j in range(msgIds.size):
            await channel.get_partial_message(msgIds[j]).add_reaction('✅')
            await channel.get_partial_message(msgIds[j]).add_reaction('❌')

bot.run(open('TOKEN.txt', "r").read())