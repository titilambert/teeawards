from bottle import mako_view, request, response, redirect
from libs.lib import *
from libs.maps import get_maps, get_map_mods
from libs.teeworldsserver import twms


@mako_view('maps')
def maps():
    gametype = ''
    if 'gametype' in request.params:
        gametype = request.params['gametype']
    context = {}
    context['page'] = 'maps'
    context['map_list'] = get_maps(gametype)

    context['mods'] = get_map_mods()
    context['selected_mod'] = gametype
    return context

