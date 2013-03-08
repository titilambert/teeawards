from bottle import mako_view, request, response, redirect
from libs.lib import *
from libs import rank
from libs.teeworldsserver import twms
from libs.achievements import *

@mako_view('achievements')
def achievements(achievement_name=None,player_name=None):
    context = {}
    context['page'] = 'achievements'
    context['server_alive'] = twms.is_alive()
    context['achievement_list'] = achievement_list
    if not achievement_name is None:
        if achievement_name in achievement_list:
            ok = achievement_list[achievement_name].has_achievements(player_name)
            return str(ok)


    return context

