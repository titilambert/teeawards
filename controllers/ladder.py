from bottle import mako_view, request, response, redirect

from libs.lib import get_player_list
from libs.lib import job_list

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

    stats_by_players = []
    players = get_player_list()
    for player in players:
        tmp_dict = {}
        # Killer
        killjob = getattr(job_list['KillsJob'], 'KillsJob')()
        killjob.set_gametype(gametype)
        killjob.set_player_name(player)
        kills = killjob.get_results()
        tmp_dict['kills'] = kills
        # Ratio
        ratiojob = getattr(job_list['RatiosJob'], 'RatiosJob')()
        ratiojob.set_gametype(gametype)
        ratiojob.set_player_name(player)
        ratio = ratiojob.get_results()
        tmp_dict['ratio'] = ratio
        # Victim
        deathjob = getattr(job_list['DeathsJob'], 'DeathsJob')()
        deathjob.set_gametype(gametype)
        deathjob.set_player_name(player)
        deaths = deathjob.get_results()
        tmp_dict['deaths'] = deaths
        # Suicider
        suicidejob = getattr(job_list['SuicidesJob'], 'SuicidesJob')()
        suicidejob.set_gametype(gametype)
        suicidejob.set_player_name(player)
        suicides = suicidejob.get_results()
        tmp_dict['suicides'] = suicides
        # Score
        tmp_dict['score'] = 0
        # Rank
        tmp_dict['rank'] = get_rank(player, tmp_dict['score'])
        # Save stats
        stats_by_players.append((player, tmp_dict))

    if sort == 'nickname':
        context['stats_by_players'] = sorted([x for x in stats_by_players],
                                         key=lambda x: x[0])
    else:
        context['stats_by_players'] = sorted([x for x in stats_by_players],
                                         key=lambda x: x[1][sort],
                                         reverse=True)

    return context

