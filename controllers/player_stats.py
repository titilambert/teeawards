from bottle import mako_view, request, response, redirect
from libs.lib import *
from libs.rank import get_rank, ranks
from libs.maps import get_maps
from libs.teeworldsserver import twms
from libs.achievement import achievement_player_list


@mako_view('player_stats')
def player_stats(player=None):
    context = {}
    if request.method == 'POST':
        player = request.params['player']
    # Test player exists
    if not player in get_player_list():
        context["not_found"] = player
        return context

    context['player'] = player
    context['kill_mapping'] = kill_mapping
    context['pickup_mapping'] = pickup_mapping
    context['pstats'] = get_player_items_stats(player)

    player_stats = get_stats(player)
#    context['kstats'] = player_stats['kills']
#    context['vstats'] = player_stats['victims']
    # TODO integrate weapon stats in get_stat function
    context['kstats'], context['vstats'], context['pstats'] = get_player_stats(player)
    
    context['kills'] = sum(player_stats['kills'].values())
    context['suicides'] = player_stats['suicides']
    context['fullserverstatus'] = twms.get_server_info()
    if context['fullserverstatus']:
        context['playernames'] = ", ".join([x['name'] for x in context['fullserverstatus']['players']])
        context['gametype'] = context['fullserverstatus']['gametype']

    context['score'] = player_stats['score']
    context['deaths'] = player_stats['deaths']
    context['ratio'] = context['kills'] / float(context['deaths'])

    rank_level = get_rank(player, context['score'])
    context['rank'] = (rank_level, ranks[rank_level][0], ranks[rank_level][1])
    context['nextrank'] = (rank_level + 1, ranks[rank_level + 1][0], ranks[rank_level + 1][1])

    context['map_list'] = dict([(x['name'], x['map']) for x in get_maps()])
    # Favorite
    try:
        context['favorite_map'] = sorted([x for x in player_stats['maps'].items()], key=lambda x: x[1], reverse=True)[0]
    except:
        context['favorite_map'] = ("No data", 0)
    try:
        context['favorite_victim'] = sorted([x for x in context['kstats']['victim'].items()], key=lambda x: x[1], reverse=True)[0]
    except:
        context['favorite_victim'] = ("No data", 0)
    try:
        context['favorite_killer'] = sorted([x for x in context['vstats']['killer'].items()], key=lambda x: x[1], reverse=True)[0]
    except:
        context['favorite_killer'] = ("No data", 0)
    try:
        context['favorite_weapon'] = sorted([x for x in context['kstats']['weapon'].items()],
                                 key=lambda x: x[1],
                                 reverse=True)[0]
    except:
        context['favorite_weapon'] = ("No data", 0)
    # Places
    context['first_place'] = player_stats.get('first_place', 0)
    context['second_place'] = player_stats.get('second_place', 0)
    context['third_place'] = player_stats.get('third_place', 0)
    context['last_place'] = player_stats.get('last_place', 0)

    context['achievement_list'] = {}
    for achievement in achievement_player_list.items():
        context['achievement_list'][achievement[0]] = achievement[1](player)

    return context

