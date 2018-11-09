import hug

from teeawards.const import KILL_MAPPING, PICKUP_MAPPING, RANKS
from teeawards.libs.stats import (
    get_kills_for_player, get_rank_for_player, get_score_for_player,
    get_ratio_for_player, get_deaths_for_player, get_suicides_for_player,
    get_rounds_for_player
)
from teeawards.web.directives import mako_template


#@hug.get('/player_stats/{player}/{gametype}', output=hug.output_format.html)
@hug.get('/player_stats/{player}', output=hug.output_format.html)
@hug.post('/player_stats/', output=hug.output_format.html)
#def ladder(player, gametype='all', body=None, request=None, mako_tpl:mako_template='player_stats'):
def ladder(player, body=None, request=None, mako_tpl:mako_template='player_stats'):
    ctx = request.context['tpl_ctx']

    ctx = {}

    influx_client = request.context['influx_client']

    ctx['kill_mapping'] = KILL_MAPPING
    ctx['pickup_mapping'] = PICKUP_MAPPING

    ctx['player'] = player

    rank_level = get_rank_for_player(influx_client, player)
#    import ipdb; ipdb.set_trace()
    ctx['rank'] = (rank_level, RANKS[rank_level][0], RANKS[rank_level][1])
    ctx['nextrank'] = (rank_level + 1, RANKS[rank_level + 1][0], RANKS[rank_level + 1][1])
    ctx['score'] = get_score_for_player(influx_client, player)
    ctx['ratio'] = get_ratio_for_player(influx_client, player)
    ctx['kills'] = get_kills_for_player(influx_client, player)
    ctx['deaths'] = get_deaths_for_player(influx_client, player)
    ctx['suicides'] = get_suicides_for_player(influx_client, player)
    ctx['rounds'] = get_rounds_for_player(influx_client, player)



    return mako_tpl.render(**ctx)
