from bottle import mako_view, request, response, redirect
from libs.lib import *
from libs.rank import get_rank
from libs.teeworldsserver import twms
from libs.hooks import *


@mako_view('ladder')
@prepare_context
def ladder(sort='score', context={}, gametype=None):
    context['page'] = 'ladder'
    context['sort'] = sort

    if sort not in ['kills', 'suicides', 'deaths', 'score', 'ratio', 'nickname']:
        redirect("/ladder")

    stats_by_players = get_stats()

    stats_by_players = [(p, {'kills': sum(data['kills'].values()),
                             'suicides': data['suicides'],
                             'deaths': data['deaths'],
                             'rank': get_rank(p,  data['score']),
                             'score': data['score'],
                             'ratio': sum(data['kills'].values()) / float(data['deaths']),
                              }
                        )
                        for p, data in stats_by_players.items()]

    if sort == 'nickname':
        context['stats_by_players'] = sorted([x for x in stats_by_players],
                                         key=lambda x: x[0])
    else:
        context['stats_by_players'] = sorted([x for x in stats_by_players],
                                         key=lambda x: x[1][sort],
                                         reverse=True)

    return context

