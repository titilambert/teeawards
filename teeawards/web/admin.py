import time

import hug

from teeawards.libs.teeworldsserver import save_conf, get_configs, get_config, delete_conf, other_settings, engine_settings, game_settings

from teeawards.libs.maps import get_maps, save_map, get_map, delete_map
from teeawards.web.directives import mako_template


@hug.get('/admin', output=hug.output_format.html)
def admin(request=None, mako_tpl:mako_template='admin'):
    ctx = request.context['tpl_ctx']
    ctx['page'] = 'admin'
    ctx['engine_settings'] = None
    ctx['game_settings'] = None
    ctx['config_list'] = get_configs()
    ctx['map_list'] = get_maps()
    ctx['fullserverstatus'] = request.context['twsm'].get_server_info()
    if ctx['fullserverstatus']:
        ctx['playernames'] = ", ".join([x['name'] for x in ctx['fullserverstatus']['players']])
        ctx['gametype'] = ctx['fullserverstatus']['gametype']
        ctx['server_alive'] = True
    else:
        ctx['server_alive'] = False

    return mako_tpl.render(**ctx)


@hug.get('/admin/conf/edit', output=hug.output_format.html)
@hug.get('/admin/conf/edit/', output=hug.output_format.html)
@hug.get('/admin/conf/edit/{id_}', output=hug.output_format.html)
def conf_edit(id_=None, request=None, mako_tpl:mako_template='conf'):
    ctx = request.context['tpl_ctx']
    ctx['page'] = 'admin'
    ctx['other_settings'] = None
    ctx['engine_settings'] = None
    ctx['game_settings'] = None
    ctx['id'] = id_ if id_ else ''

    if not id_:
        ctx['other_settings'] = other_settings
        ctx['engine_settings'] = engine_settings
        ctx['game_settings'] = game_settings
    else:
        ctx['engine_settings'] = []
        ctx['game_settings'] = []
        ctx['other_settings'] = []
        conf = get_config(id_)

        for setting, help_, _ in engine_settings:
            if not setting in conf['conf']:
                conf['conf'][setting] = ''
            ctx['engine_settings'].append((setting, help_, conf['conf'][setting]))
        for setting, help_, _ in game_settings:
            if not setting in conf['conf']:
                conf['conf'][setting] = ''
            ctx['game_settings'].append((setting, help_, conf['conf'][setting]))
        for setting, help_, _ in other_settings:
            if not setting in conf['conf']:
                conf['conf'][setting] = ''
            if setting == 'server_binary':
                ctx['other_settings'].append((setting, help_, b""))
            else:
                ctx['other_settings'].append((setting, help_, conf['conf'][setting]))
                
    return mako_tpl.render(**ctx)


@hug.post('/admin/conf/edit', output=hug.output_format.html)
@hug.post('/admin/conf/edit/{id_}', output=hug.output_format.html)
def conf_edit(body, id_=None, request=None, mako_tpl:mako_template='conf'):
    save_conf(body, id_)
    hug.redirect.found('/admin')


@hug.get('/admin/conf/delete/{id_}', output=hug.output_format.html)
def conf_delete(id_=None, request=None, mako_tpl:mako_template='conf'):
    delete_conf(id_)
    hug.redirect.found('/admin')


@hug.get('/admin/map/edit', output=hug.output_format.html)
@hug.get('/admin/map/edit/', output=hug.output_format.html)
@hug.get('/admin/map/edit/{id_}', output=hug.output_format.html)
def map_edit(id_=None, request=None, mako_tpl:mako_template='map'):
    ctx = request.context['tpl_ctx']
    ctx['page'] = 'admin'
    ctx['id'] = id_ if id_ else ''

    if not id_:
        ctx['map'] = None
    else:
        tmap = get_map(id_)
        ctx['map'] = tmap
        # TODO
#        raise
                
    return mako_tpl.render(**ctx)


@hug.post('/admin/map/edit', output=hug.output_format.html)
@hug.post('/admin/map/edit/', output=hug.output_format.html)
@hug.post('/admin/map/edit/{id_}', output=hug.output_format.html)
def map_save(body, id_=None, request=None, mako_tpl:mako_template='map'):
    ctx = request.context['tpl_ctx']
    ctx['page'] = 'admin'
    ctx['id'] = id_ if id_ else ''
    ret = save_map(body, id_)

    # TODO ret == False => Error

    hug.redirect.found('/admin')

@hug.get('/admin/map/delete/{id_}', output=hug.output_format.html)
def map_delete(id_=None, request=None, mako_tpl:mako_template='conf'):
    delete_map(id_)
    hug.redirect.found('/admin')
  


@hug.post('/admin/toggle_server/', output=hug.output_format.html)
def map_delete(body, request=None, mako_tpl:mako_template='conf'):
    if body['toggle_server'] == 'start':
        conf_name = body['config']
        request.context['twsm'].start(conf_name)
        time.sleep(1)
    if body['toggle_server'] == 'stop':
        twms.stop()   
        time.sleep(2)

    hug.redirect.found('/admin')
