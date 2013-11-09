from bottle import mako_view, request, response, redirect
from libs.lib import *
from libs.rank import get_rank, ranks
from libs.maps import get_maps
from libs.teeworldsserver import twms
from libs.achievement import achievement_player_list
from libs.hooks import *


@mako_view('player_stats')
@prepare_context
def player_stats(player=None, context={}, gametype=None):
#    session = request.environ.get('beaker.session')
#    gametype = session.get('gametype', None)
#    context['select_gametype'] = gametype
    if request.method == 'POST':
        player = request.params['player']
    # Test player exists
    if not player in get_player_list():
        context["not_found"] = player
        return context

#    context['fullserverstatus'] = twms.get_server_info()
#    if context['fullserverstatus']:
#        context['playernames'] = ", ".join([x['name'] for x in context['fullserverstatus']['players']])
#        context['gametype'] = context['fullserverstatus']['gametype']

    context['player'] = player
    context['kill_mapping'] = kill_mapping
    context['pickup_mapping'] = pickup_mapping
    context['pstats'] = get_player_items_stats(player)

    player_stats = get_stats(player, gametype)
#    context['kstats'] = player_stats['kills']
#    context['vstats'] = player_stats['victims']
    # TODO integrate weapon stats in get_stat function
    context['kstats'], context['vstats'], context['pstats'] = get_player_stats(player)
    
    context['kills'] = sum(player_stats.get('kills', {None: 0}).values())
    context['suicides'] = player_stats.get('suicides', 0)
    context['rounds'] = player_stats.get('rounds', 0)
    context['teamkills'] = sum(player_stats.get('teamkills', {None: 0}).values())
    context['flaggrab'] = player_stats.get('flaggrab', 0)
    context['flagreturn'] = player_stats.get('flagreturn', 0)
    context['flagcapture'] = player_stats.get('flagcapture', 0)


    context['score'] = player_stats['score']
    context['deaths'] = player_stats['deaths']

    context['ratio'] = context['kills'] / float(context['deaths']) if context['deaths'] > 0 else 0

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
        context['achievement_list'][achievement[0]] = achievement[1](player, gametype)

    if gametype == None:
        context['gametype'] = 'all'
    return context

