from bottle import mako_view, request, response, redirect
from libs.lib import *
from libs.teeworldsserver import twms
from libs.hooks import *


@mako_view('index')
@prepare_context
def index(context={}, gametype=None):
    context['page'] = 'home'
    context['server_alive'] = twms.is_alive()
    context['fullserverstatus'] = twms.get_server_info()
    
    # Get score
    stats_by_players = get_stats(selected_gametype=gametype)
    # Get old stats TODO use only get_stats
    #import pdb;pdb.set_trace()
    #stats_by_players = get_general_players_stats()
    stats_by_players = [(p, {'kills': sum(data['kills'].values()),
                             'suicides': data['suicides'],
                             'deaths': data['deaths'],
                             'score': data['score'],
                             'ratio': sum(data['kills'].values()) / float(data['deaths']) if data['deaths'] else 0,
                              }
                        )
                        for p, data in stats_by_players.items()]
    try:
        context['best_killer'] = sorted([(x, data['kills']) for x, data in stats_by_players],
                                    key=lambda x: x[1],
                                    reverse=True)[0]
    except:
        context['best_killer'] = ("Nostat", 0)
    if context['best_killer'][1] == 0:
        context['best_killer'] = ("Nostat", 0)

    try:
        context['best_score'] = sorted([(x, data['score']) for x, data in stats_by_players],
                                   key=lambda x: x[1],
                                   reverse=True)[0]
    except:
        context['best_score'] = ("Nostat", 0)
    if context['best_score'][1] == 0:
        context['best_score'] = ("Nostat", 0)

    try:
        context['best_ratio'] = sorted([(x, data['ratio']) for x, data in stats_by_players],
                                   key=lambda x: x[1],
                                   reverse=True)[0]
    except:
        context['best_ratio'] = ("Nostat", 0)
    if context['best_ratio'][1] == 0:
        context['best_ratio'] = ("Nostat", 0)

    try:
        context['best_suicider'] = sorted([(x, data['suicides']) for x, data in stats_by_players],
                                      key=lambda x: x[1],
                                      reverse=True)[0]
    except:
        context['best_suicider'] = ("Nostat", 0)
    if context['best_suicider'][1] == 0:
        context['best_suicider'] = ("Nostat", 0)

    try:
        context['best_victim'] = sorted([(x, data['deaths']) for x, data in stats_by_players],
                                    key=lambda x: x[1],
                                    reverse=True)[0]
    except:
        context['best_victim'] = ("Nostat", 0)
    if context['best_victim'][1] == 0:
        context['best_victim'] = ("Nostat", 0)


    try:
        hammer_victims = get_item_stats('hammer', gametype)['dead by Hammer']
        context['best_hammer_victim'] = sorted([(x, data) for x, data in hammer_victims.items()],
                                           key=lambda x: x[1],
                                           reverse=True)[0]
    except:
        context['best_hammer_victim'] = ("Nostat", 0)
    if context['best_hammer_victim'][1] == 0:
        context['best_hammer_victim'] = ("Nostat", 0)

    return context



def set_gametype():
    session = request.environ.get('beaker.session')
    gametype = request.params.get('gametype', None)
    session['gametype'] = gametype
    session.save()
    next_page = request.headers.get('Referer', '/')
    redirect(next_page) 
