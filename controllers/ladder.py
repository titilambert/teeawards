from bottle import mako_view, request, response, redirect
from libs.lib import *
from libs.rank import get_rank
from libs.teeworldsserver import twms


@mako_view('ladder')
def ladder(sort='score'):
    context = {}
    context['page'] = 'ladder'
    context['sort'] = sort
    context['fullserverstatus'] = twms.get_server_info()
    if context['fullserverstatus']:
        context['playernames'] = ", ".join([x['name'] for x in context['fullserverstatus']['players']])
        context['gametype'] = context['fullserverstatus']['gametype']


    if sort not in ['kills', 'suicides', 'deaths', 'score', 'ratio', 'nickname']:
        redirect("/ladder")

    stats_by_players = get_general_players_stats()

    stats_by_players = [(p, {'kills': data['kills'],
                             'suicides': data['suicides'],
                             'deaths': data['deaths'],
                             'rank': get_rank(p, data),
                             'score': data['kills'] - data['suicides'],
                             'ratio': data['kills'] / float(data['deaths']),
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

