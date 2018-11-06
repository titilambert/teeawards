import os
import hug
from falcon import HTTP_404


from teeawards.web.directives import mako_template
from teeawards.server.const import ENGINE_SETTINGS, GAME_SETTINGS, OTHER_SETTINGS


@hug.get('/maps', output=hug.output_format.html)
@hug.post('/maps', output=hug.output_format.html)
def maps(body, request=None, mako_tpl:mako_template='maps'):
    ctx = request.context['tpl_ctx']
    ctx['page'] = 'maps'
    gametype = ''
    if body is not None:
        gametype = body.get('gametype', '')
    ctx['map_list'] = request.context['map_mgr'].get_maps(gametype)
    ctx['mods'] = request.context['map_mgr'].get_mods()
    ctx['selected_mod'] = gametype

    return mako_tpl.render(**ctx)


@hug.get('/map/{map_name}/screenshot', output=hug.output_format.png_image)
def map_screenshot(map_name, request):
    screenshot_path = request.context['map_mgr'].get_screenshot_path(map_name)
    return screenshot_path


@hug.get('/admin/map/edit', output=hug.output_format.html)
@hug.get('/admin/map/edit/{id_}', output=hug.output_format.html)
def map_edit(id_=None, request=None, mako_tpl:mako_template='map'):
    ctx = request.context['tpl_ctx']
    ctx['page'] = 'admin'
    ctx['id_'] = id_
    if id_ is None:
        ctx['map'] = None
    else:
        ctx['map'] = request.context['map_mgr'].get_map(id_)

    return mako_tpl.render(**ctx)

@hug.post('/admin/map/edit', output=hug.output_format.html)
@hug.post('/admin/map/edit/{id_}', output=hug.output_format.html)
def conf_edit(id_=None, body=None, request=None, mako_tpl:mako_template='conf'):
    ctx = request.context['tpl_ctx']
    ctx['page'] = 'admin'
    if id_ is not None:
        request.context['map_mgr'].save_map(body, edit=True)
    else:
        request.context['map_mgr'].save_map(body, edit=False)
    hug.redirect.found('/admin')

@hug.get('/admin/map/delete/{map_name}', output=hug.output_format.html)
def conf_delete(map_name=None, request=None):
    request.context['map_mgr'].delete_map(map_name)
    hug.redirect.temporary('/admin')
