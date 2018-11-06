import os
import hug
from falcon import HTTP_404


from teeawards.web.directives import mako_template
from teeawards.server.const import ENGINE_SETTINGS, GAME_SETTINGS, OTHER_SETTINGS


@hug.get('/admin/conf/edit', output=hug.output_format.html)
@hug.get('/admin/conf/edit/{id_}', output=hug.output_format.html)
def conf_edit(id_=None, request=None, mako_tpl:mako_template='conf'):
    ctx = request.context['tpl_ctx']
    ctx['page'] = 'admin'
    ctx['other_settings'] = None
    ctx['engine_settings'] = None
    ctx['game_settings'] = None
    ctx['id'] = id_
    if not id_:
        ctx['other_settings'] = OTHER_SETTINGS
        ctx['engine_settings'] = ENGINE_SETTINGS
        ctx['game_settings'] = GAME_SETTINGS
    else:
        ctx['engine_settings'] = []
        ctx['game_settings'] = []
        ctx['other_settings'] = []
        conf = request.context['cfg_mgr'].get_conf(id_)
        for setting, help_, _ in ENGINE_SETTINGS:
            if not setting in conf:
                conf[setting] = ''
            ctx['engine_settings'].append((setting, help_, conf[setting]))
        for setting, help_, _ in GAME_SETTINGS:
            if not setting in conf:
                conf[setting] = ''
            ctx['game_settings'].append((setting, help_, conf[setting]))
        for setting, help_, _ in OTHER_SETTINGS:
            if not setting in conf:
                conf[setting] = ''
            ctx['other_settings'].append((setting, help_, conf[setting]))


    return mako_tpl.render(**ctx)

@hug.post('/admin/conf/edit', output=hug.output_format.html)
@hug.post('/admin/conf/edit/{id_}', output=hug.output_format.html)
def conf_edit(id_=None, body=None, request=None, mako_tpl:mako_template='conf'):
    ctx = request.context['tpl_ctx']
    ctx['page'] = 'admin'
    ctx['other_settings'] = None
    ctx['engine_settings'] = None
    ctx['game_settings'] = None
    request.context['cfg_mgr'].save_conf(body)
    hug.redirect.found('/admin')

    return mako_tpl.render(**ctx)

@hug.get('/admin/conf/delete/{id_}', output=hug.output_format.html)
def conf_delete(id_=None, request=None):
    request.context['cfg_mgr'].delete_conf(id_)
    hug.redirect.temporary('/admin')
