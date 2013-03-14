from bottle import mako_view, request, response, redirect
from libs.lib import *
from libs.maps import get_maps
from libs.teeworldsserver import twms


@mako_view('maps')
def maps(id=None):
    context = {}
    context['page'] = 'maps'
    context['map_list'] = get_maps()

    return context

