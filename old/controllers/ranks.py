from bottle import mako_view, request, response, redirect
from libs.lib import *
from libs import rank
from libs.teeworldsserver import twms
from libs.hooks import *


@mako_view('ranks')
@prepare_context
def ranks(context={}, gametype=None):
    context = {}
    context['page'] = 'ranks'
    context['ranks'] = rank.ranks
    context['fullserverstatus'] = twms.get_server_info()
    if context['fullserverstatus']:
        context['playernames'] = ", ".join([x['name'] for x in context['fullserverstatus']['players']])
        context['gametype'] = context['fullserverstatus']['gametype']

    return context

