import hug


from teeawards.const import R_PICKUP_MAPPING
from teeawards.libs.stats import get_stats_by_items
from teeawards.web.directives import mako_template


@hug.get('/items', output=hug.output_format.html)
def ladder(body=None, request=None, mako_tpl:mako_template='item_stats'):
    ctx = request.context['tpl_ctx']

    ctx = {}
    ctx['page'] = 'items'
    ctx['items'] = {}


    influx_client = request.context['influx_client']

    ctx['itemlist'] = ['heart', 'shield', 'hammer', 'gun',
             'shotgun', 'grenade', 'laser', 'ninja',]
#    for item in ctx['itemlist']:


    ret = get_stats_by_items(influx_client)
    print(ret)
    for key, value in ret.items():
        if key in ctx['itemlist']:
            ctx['items'][key] = value
#        import ipdb;ipdb.set_trace()
#    ctx['items'] = ret

    return mako_tpl.render(**ctx)
