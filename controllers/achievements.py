from bottle import mako_view, request, response, redirect
from libs.lib import *
from libs import rank
from libs.teeworldsserver import twms
from libs.achievement import *

@mako_view('achievements')
def achievements(achievement_name=None,player_name=None):
    context = {}
    context['page'] = 'achievements'
    context['server_alive'] = twms.is_alive()
    context['achievement_desc_list'] = {}
    print achievement_desc_list
    
    for name, fct in achievement_desc_list.items():
        context['achievement_desc_list'][name] = fct()

    return context
