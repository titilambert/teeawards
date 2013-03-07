from bottle import mako_view, request, response, redirect
from libs.lib import *
from libs.rank import get_rank
from libs.teeworldsserver import twms, save_conf, engine_settings, game_settings, get_configs
from time import sleep

@mako_view('admin')
def admin(action=None):
    context = {}
    context['page'] = 'admin'
    context['server_alive'] = twms.is_alive()
    context['engine_settings'] = None
    context['game_settings'] = None
    context['config_list'] = get_configs()


    if request.method == 'POST':
        # restart server
        if action == 'toggle_server':
            if request.params['toggle_server'] == 'start':
                twms.start()
                redirect("/admin") 
            if request.params['toggle_server'] == 'stop':
                twms.stop()
                sleep(2)
                redirect("/admin") 
        # create new conf
        elif action == 'new':
            save_conf(request.params)
            redirect("/admin") 



    if action == 'new':
        context['engine_settings'] = engine_settings
        context['game_settings'] = game_settings
    
    return context
