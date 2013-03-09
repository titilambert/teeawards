from bottle import mako_view, request, response, redirect
from libs.lib import *
from libs.rank import get_rank, ranks
from libs.teeworldsserver import twms
from libs.achievement import achievement_list


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
    context['kstats'], context['vstats'], context['pstats'] = get_player_stats(player)
    context['kills'] = sum(context['kstats']['victim'].values())
    context['suicides'] = context['vstats']['suicide']
    context['fullserverstatus'] = twms.get_server_info()
    if context['fullserverstatus']:
        context['playernames'] = ", ".join([x['name'] for x in context['fullserverstatus']['players']])
        context['gametype'] = context['fullserverstatus']['gametype']

    rank_level = get_rank(player, context)
    context['rank'] = (rank_level, ranks[rank_level][0], ranks[rank_level][1])
    context['nextrank'] = (rank_level + 1, ranks[rank_level + 1][0], ranks[rank_level + 1][1])

    context['favorite_weapon'] = sorted([x for x in context['kstats']['weapon'].items()],
                                 key=lambda x: x[1],
                                 reverse=True)[0]
    context['score'] = context['kills'] - context['suicides']
    context['deaths'] = context['suicides'] + sum(context['vstats']['weapon'].values())
    context['ratio'] = context['kills'] / float(context['deaths'])
    context['favorite_victim'] = sorted([x for x in context['kstats']['victim'].items()], key=lambda x: x[1], reverse=True)[0]
    context['favorite_killer'] = sorted([x for x in context['vstats']['killer'].items()], key=lambda x: x[1], reverse=True)[0]

    context['achievement_list'] = {}
    for achievement in achievement_list.items():
        context['achievement_list'][achievement[0]] = achievement[1].has_achievements(player)

    return context

