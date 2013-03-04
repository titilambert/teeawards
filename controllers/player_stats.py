from bottle import mako_view, request, response, redirect
from libs.lib import *
from libs.rank import get_rank, ranks

@mako_view('player_stats')
def player_stats(player=None):
    context = {}
    if request.method == 'POST':
        player = request.params['player']
    # Test player exists

    context['player'] = player
    context['kill_mapping'] = kill_mapping
    context['pickup_mapping'] = pickup_mapping
    context['kstats'], context['vstats'], context['pstats'] = get_player_stats(player)
    context['kills'] = sum(context['kstats']['victim'].values())
    context['suicides'] = context['vstats']['suicide']

    rank_level = get_rank(player, context)
    context['rank'] = (rank_level, ranks[rank_level][0])

    context['favorite_weapon'] = sorted([x for x in context['kstats']['weapon'].items()],
                                 key=lambda x: x[1],
                                 reverse=True)[0]
    context['score'] = context['kills'] - context['suicides']
    context['deaths'] = context['suicides'] + sum(context['vstats']['weapon'].values())
    context['ratio'] = context['kills'] / float(context['deaths'])
    context['favorite_victim'] = sorted([x for x in context['kstats']['victim'].items()], key=lambda x: x[1], reverse=True)[0]
    context['favorite_killer'] = sorted([x for x in context['vstats']['killer'].items()], key=lambda x: x[1], reverse=True)[0]

    return context
