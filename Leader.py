# -*- coding: utf-8 -*-
import re
import time

LeaderStat = False
Leader = None
here_user = 0


def on_info(server, info):
    global LeaderStat
    if info.is_player:
        if info.content == '!!leader':
            if not LeaderStat:
                onLeader(server, info)
            else:
                server.reply(info, "已经存在引领者了，引领失败")
        if info.content == '!!unleader':
            if LeaderStat and Leader == info.player:
                unLeader(server, info)
            else:
                server.reply(info, "你不是引领者或目前不存在引领者，取消引领失败")


def onLeader(server, info):
    global LeaderStat
    global Leader
    LeaderStat = True
    Leader = info.player
    if hasattr(server, 'MCDR') and server.is_rcon_running():
        name = info.player
        position = process_coordinate(re.search(r'\[.*\]', server.rcon_query('data get entity {} Pos'.format(name))).group())
        dimension = process_dimension(server.rcon_query('data get entity {} Dimension'.format(name)))
    else:
        global here_user
        here_user += 1
        server.execute('data get entity ' + info.player)
    if not info.is_player and here_user > 0 and re.match(r'\w+ has the following entity data: ', info.content) is not None:
        name = info.content.split(' ')[0]
        dimension = int(re.search(r'(?<=Dimension: )-?\d', info.content).group())
        position_str = re.search(r'(?<=Pos: )\[.*?\]', info.content).group()
        position = process_coordinate(position_str)
        here_user -= 1
    server.say("已标记玩家：" + info.player + "为引领者，快跟随他吧！")
    server.reply(info, '引领者每60秒公布一次坐标，使用!!unleader取消引领')
    display(server, name, position, dimension)
    server.execute('effect give ' + info.player + ' minecraft:glowing 1000000')
    while LeaderStat:
        time.sleep(60)
        if not LeaderStat:
            break
        else:
            server.reply(info, '引领者每60秒公布一次坐标，使用!!unleader取消引领')
            display(server, name, position, dimension)


def unLeader(server, info):
    global LeaderStat
    global Leader
    LeaderStat = False
    Leader = None
    server.execute('effect clear ' + info.player + ' minecraft:glowing')
    server.say("玩家：" + info.player + "已经取消引领，不要再打扰他了！")


def process_coordinate(text):
    data = text[1:-1].replace('d', '').split(', ')
    data = [(x + 'E0').split('E') for x in data]
    return tuple([int(float(e[0]) * 10 ** int(e[1])) for e in data])


def process_dimension(text):
    return int(text.lstrip(re.match(r'[\w ]+:', text).group()))


def display(server, name, position, dimension):
    dimension_display = {0: '§2主世界', -1: '§4地狱', 1: '§5末地'}
    position_show = '[x:{}, y:{}, z:{}]'.format(*position)
    server.say("引领者现在在：")
    server.say('§e{}§r @ {} §r{}'.format(name, dimension_display[dimension], position_show))
    server.say("快跟上他吧！")


def on_load(server, old_module):
    server.add_help_message('!!leader', '标记自己为引领者')

