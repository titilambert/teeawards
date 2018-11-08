import hug


from teeawards.libs.stats import get_stats_by_players
from teeawards.web.directives import mako_template


@hug.get('/ladder', output=hug.output_format.html)
def ladder(body=None, request=None, mako_tpl:mako_template='ladder'):
    ctx = request.context['tpl_ctx']

    ctx = {}
    ctx['page'] = 'ladder'

    influx_client = request.context['influx_client']

    ctx['stats_by_players'] = get_stats_by_players(influx_client)

    return mako_tpl.render(**ctx)
