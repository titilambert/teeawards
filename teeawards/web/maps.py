import hug

from teeawards.libs.teeworldsserver import save_conf, get_configs, get_config, delete_conf, other_settings, engine_settings, game_settings

from teeawards.libs.maps import get_maps, get_map_mods, get_screenshot
from teeawards.web.directives import mako_template


@hug.post('/maps', output=hug.output_format.html)
@hug.get('/maps', output=hug.output_format.html)
def maps(body=None, request=None, mako_tpl:mako_template='maps'):
    ctx = request.context['tpl_ctx']

    gametype = ''
    if body is not None and 'gametype' in body:
        gametype = body['gametype']
    ctx = {}
    ctx['page'] = 'maps'
    ctx['map_list'] = get_maps(gametype)

    ctx['mods'] = get_map_mods()
    ctx['selected_mod'] = gametype
    return mako_tpl.render(**ctx)


@hug.get('/map_screenshots/{id_}')
def map_screenshot(id_, request=None, response=None, mako_tpl:mako_template='maps'):
    
    response.content_type = 'image/png'
    data = get_screenshot(id_)
    return data
