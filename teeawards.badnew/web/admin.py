import os
import time

import hug
from falcon import HTTP_404

from teeawards.web.directives import mako_template
from teeawards.server.const import ENGINE_SETTINGS, GAME_SETTINGS, OTHER_SETTINGS


@hug.get('/admin', output=hug.output_format.html)
def admin(request=None, mako_tpl:mako_template='admin'):
    ctx = request.context['tpl_ctx']
    ctx['page'] = 'admin'
    ctx['engine_settings'] = None
    ctx['game_settings'] = None
    ctx['config_list'] = request.context['cfg_mgr'].list_conf()
    ctx['map_list'] = request.context['map_mgr'].get_maps()
    ctx['fullserverstatus'] = request.context['server_mgr'].get_server_info()
    if ctx['fullserverstatus']:
        ctx['playernames'] = ", ".join([x['name'] for x in ctx['fullserverstatus']['players']])
        ctx['gametype'] = ctx['fullserverstatus']['gametype']
        ctx['server_alive'] = True
    else:
        ctx['server_alive'] = False

    return mako_tpl.render(**ctx)

@hug.post('/admin/toggle_server')
def toggle_server(body, request=None, mako_tpl:mako_template='admin'):
    if body.get('toggle_server') == 'start':
        conf_name = body['config']
        request.context['server_mgr'].start(conf_name)
    elif body.get('toggle_server') == 'stop':
        request.context['server_mgr'].stop()
    time.sleep(2)
    hug.redirect.found('/admin')
