from bottle import mako_view, request, response, redirect
from libs.lib import kill_mapping, pickup_mapping
from libs.lib import get_player_list
from libs.lib import job_list


from libs.rank import get_rank, ranks
from libs.maps import get_maps
from libs.teeworldsserver import twms
from libs.achievement import achievement_player_list
from libs.hooks import *

# old
from libs.lib import get_stats, get_player_stats

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

    # Kills
    killjob = getattr(job_list['KillsJob'], 'KillsJob')()
    killjob.set_gametype(gametype)
    killjob.set_player_name(player)
    context['kills'] = killjob.get_results()
    # Ratio
    ratiojob = getattr(job_list['RatiosJob'], 'RatiosJob')()
    ratiojob.set_gametype(gametype)
    ratiojob.set_player_name(player)
    context['ratio'] = ratiojob.get_results()
    # Deaths
    deathjob = getattr(job_list['DeathsJob'], 'DeathsJob')()
    deathjob.set_gametype(gametype)
    deathjob.set_player_name(player)
    context['deaths'] = deathjob.get_results()
    # Suicides
    suicidejob = getattr(job_list['SuicidesJob'], 'SuicidesJob')()
    suicidejob.set_gametype(gametype)
    suicidejob.set_player_name(player)
    context['suicides'] = suicidejob.get_results()
    # Played rounds
    played_roundjob = getattr(job_list['Played_roundsJob'], 'Played_roundsJob')()
    played_roundjob.set_gametype(gametype)
    played_roundjob.set_player_name(player)
    context['rounds'] = played_roundjob.get_results()
    # Flag Grab
    flaggrabjob = getattr(job_list['FlaggrabsJob'], 'FlaggrabsJob')()
    flaggrabjob.set_gametype(gametype)
    flaggrabjob.set_player_name(player)
    context['flaggrab'] = flaggrabjob.get_results()
    # Flag Return
    flagreturnsjob = getattr(job_list['FlagreturnsJob'], 'FlagreturnsJob')()
    flagreturnsjob.set_gametype(gametype)
    flagreturnsjob.set_player_name(player)
    context['flagreturn'] = flagreturnsjob.get_results()   
    # Flag captupre
    flagcapturesjob = getattr(job_list['FlagcapturesJob'], 'FlagcapturesJob')()
    flagcapturesjob.set_gametype(gametype)
    flagcapturesjob.set_player_name(player)
    context['flagcapture'] = flagcapturesjob.get_results()
    # TeamKills
    teamkillsjob = getattr(job_list['TeamkillsJob'], 'TeamkillsJob')()
    teamkillsjob.set_gametype(gametype)
    teamkillsjob.set_player_name(player)
    context['teamkills'] = teamkillsjob.get_results()




    # Weapon Deaths
    hammer_deathsjob = getattr(job_list['Deaths_by_weaponsJob'], 'Deaths_by_weaponsJob')()
    hammer_deathsjob.set_gametype(gametype)
    hammer_deathsjob.set_player_name(player)
    hammer_deathsjob.set_weapon(kill_mapping['hammer'])
    hammer_deaths = hammer_deathsjob.get_results()



    player_stats = get_stats(player, gametype)
#    context['kstats'] = player_stats['kills']
#    context['vstats'] = player_stats['victims']
    # TODO integrate weapon stats in get_stat function
    context['kstats'], context['vstats'], context['pstats'] = get_player_stats(player)
    
    print context['kstats']
    print context['vstats']
    print context['pstats'] 

    context['score'] = player_stats['score']
#    context['deaths'] = player_stats['deaths']

#    context['ratio'] = context['kills'] / float(context['deaths']) if context['deaths'] > 0 else 0

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

