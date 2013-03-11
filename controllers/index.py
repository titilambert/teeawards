from bottle import mako_view, request, response, redirect
from libs.lib import *
from libs.teeworldsserver import twms


@mako_view('index')
def index():
    context = {}
    context['page'] = 'home'
    context['server_alive'] = twms.is_alive()
    context['fullserverstatus'] = twms.get_server_info()
    if context['fullserverstatus']: 
        context['playernames'] = ", ".join([x['name'] for x in context['fullserverstatus']['players']])
        context['gametype'] = context['fullserverstatus']['gametype']


    stats_by_players = get_general_players_stats()
    stats_by_players = [(p, {'kills': data['kills'],
                             'suicides': data['suicides'],
                             'deaths': data['deaths'],
                             'score': data['kills'] - data['suicides'],
                             'ratio': data['kills'] / float(data['deaths']),
                              }
                        )
                        for p, data in stats_by_players.items()]
    try:
        context['best_killer'] = sorted([(x, data['kills']) for x, data in stats_by_players],
                                    key=lambda x: x[1],
                                    reverse=True)[0]
    except:
        context['best_killer'] = ("Nostat", 0)

    try:
        context['best_score'] = sorted([(x, data['score']) for x, data in stats_by_players],
                                   key=lambda x: x[1],
                                   reverse=True)[0]
    except:
        context['best_score'] = ("Nostat", 0)

    try:
        context['best_ratio'] = sorted([(x, data['ratio']) for x, data in stats_by_players],
                                   key=lambda x: x[1],
                                   reverse=True)[0]
    except:
        context['best_ratio'] = ("Nostat", 0)

    try:
        context['best_suicider'] = sorted([(x, data['suicides']) for x, data in stats_by_players],
                                      key=lambda x: x[1],
                                      reverse=True)[0]
    except:
        context['best_suicider'] = ("Nostat", 0)

    try:
        context['best_victim'] = sorted([(x, data['deaths']) for x, data in stats_by_players],
                                    key=lambda x: x[1],
                                    reverse=True)[0]
    except:
        context['best_victim'] = ("Nostat", 0)


    try:
        hammer_victims = get_item_stats('hammer')['dead by Hammer']
        context['best_hammer_victim'] = sorted([(x, data) for x, data in hammer_victims.items()],
                                           key=lambda x: x[1],
                                           reverse=True)[0]
    except:
        context['best_hammer_victim'] = ("Nostat", 0)
    return context

