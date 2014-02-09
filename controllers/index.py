from bottle import mako_view, request, response, redirect
from libs.teeworldsserver import twms
from libs.lib import get_player_list
from libs.lib import job_list
from libs.lib import kill_mapping
#### BAD !!!
from libs.hooks import *
from libs.lib import *

@mako_view('index')
@prepare_context
def index(context={}, gametype=None):
    context['page'] = 'home'
    context['server_alive'] = twms.is_alive()
    context['fullserverstatus'] = twms.get_server_info()
    
    # Get score
    stats_by_players = get_stats(selected_gametype=gametype)
    # Get old stats TODO use only get_stats

    # Prepare list
    best_killers = []
    best_ratios = []
    best_victims = []
    best_suiciders = []
    best_hammer_victims = []
    
    players = get_player_list()
    for player in players:
        # Best Killer
        killjob = getattr(job_list['KillsJob'], 'KillsJob')()
        killjob.set_gametype(gametype)
        killjob.set_player_name(player)
        kills = killjob.get_results()
        best_killers.append((player, kills))
        # Best Ratio
        ratiojob = getattr(job_list['RatiosJob'], 'RatiosJob')()
        ratiojob.set_gametype(gametype)
        ratiojob.set_player_name(player)
        ratio = ratiojob.get_results()
        best_ratios.append((player, ratio))
        # Best Victim
        deathjob = getattr(job_list['DeathsJob'], 'DeathsJob')()
        deathjob.set_gametype(gametype)
        deathjob.set_player_name(player)
        deaths = deathjob.get_results()
        best_victims.append((player, deaths))
        # Best Suicider
        suicidejob = getattr(job_list['SuicidesJob'], 'SuicidesJob')()
        suicidejob.set_gametype(gametype)
        suicidejob.set_player_name(player)
        suicides = suicidejob.get_results()
        best_suiciders.append((player, suicides))
        # Hammer Deaths
        hammer_deathsjob = getattr(job_list['Deaths_by_weaponsJob'], 'Deaths_by_weaponsJob')()
        hammer_deathsjob.set_gametype(gametype)
        hammer_deathsjob.set_player_name(player)
        hammer_deathsjob.set_weapon(kill_mapping['hammer'])
        hammer_deaths = hammer_deathsjob.get_results()
        best_hammer_victims.append((player, hammer_deaths))
        
    # Best Killer
    context['best_killer'] = sorted(best_killers, key=lambda x: x[1], reverse=True)[0]
    if context['best_killer'][1] == 0:
        context['best_killer'] = ("Nostat", 0)

    # Best Ratio
    context['best_ratio'] = sorted(best_ratios, key=lambda x: x[1], reverse=True)[0]
    if context['best_ratio'][1] == 0:
        context['best_ratio'] = ("Nostat", 0)

    # Best Victim
    context['best_victim'] = sorted(best_victims, key=lambda x: x[1], reverse=True)[0]
    if context['best_victim'][1] == 0:
        context['best_victim'] = ("Nostat", 0)

    # Best Suicider
    context['best_suicider'] = sorted(best_suiciders, key=lambda x: x[1], reverse=True)[0]
    if context['best_suicider'][1] == 0:
        context['best_suicider'] = ("Nostat", 0)

    # Best hammer_victim
    context['best_hammer_victim'] = sorted(best_hammer_victims, key=lambda x: x[1], reverse=True)[0]
    if context['best_hammer_victim'][1] == 0:
        context['best_hammer_victim'] = ("Nostat", 0)



    ############# OLD CODES 
#    import pdb;pdb.set_trace()
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
        context['best_score'] = sorted([(x, data['score']) for x, data in stats_by_players],
                                   key=lambda x: x[1],
                                   reverse=True)[0]
    except:
        context['best_score'] = ("Nostat", 0)
    if context['best_score'][1] == 0:
        context['best_score'] = ("Nostat", 0)

    ############# OLD CODES 

    return context



def set_gametype():
    session = request.environ.get('beaker.session')
    gametype = request.params.get('gametype', None)
    session['gametype'] = gametype
    session.save()
    next_page = request.headers.get('Referer', '/')
    redirect(next_page) 
