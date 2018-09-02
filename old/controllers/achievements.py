from bottle import mako_view, request, response, redirect
from libs.lib import *
from libs import rank
from libs.teeworldsserver import twms
from libs.achievement import *
from libs.hooks import *


@mako_view('achievements')
@prepare_context
def achievements(achievement_name=None, player_name=None, context={}, gametype=None):
    context['page'] = 'achievements'
    context['server_alive'] = twms.is_alive()
    context['achievement_desc_list'] = {}
    
    for name, fct in achievement_desc_list.items():
        context['achievement_desc_list'][name] = fct()

    return context
