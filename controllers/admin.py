from bottle import mako_view, request, response, redirect
from libs.lib import *
from libs.rank import get_rank
from libs.teeworldsserver import *
from time import sleep

@mako_view('admin')
def admin(action=None,id_=None):
    context = {}
    context['page'] = 'admin'
    context['engine_settings'] = None
    context['game_settings'] = None
    context['config_list'] = get_configs()
    context['fullserverstatus'] = twms.get_server_info()
    if context['fullserverstatus']: 
        context['playernames'] = ", ".join([x['name'] for x in context['fullserverstatus']['players']])
        context['gametype'] = context['fullserverstatus']['gametype']
        context['server_alive'] = True
    else:
        context['server_alive'] = False

    if request.method == 'POST':
        # restart server
        if action == 'toggle_server':
            if request.params['toggle_server'] == 'start':
                conf_name = request.params['config']
                twms.start(conf_name)
                sleep(1)
                redirect("/admin") 
            if request.params['toggle_server'] == 'stop':
                twms.stop()
                sleep(2)
                redirect("/admin") 


    if action == 'new':
        context['engine_settings'] = engine_settings
        context['game_settings'] = game_settings
    
    return context

@mako_view('conf')
def conf_edit(id_=None):
    context = {}
    context['page'] = 'admin'
    context['engine_settings'] = None
    context['game_settings'] = None
    context['id'] = id_ if id_ else ''

    # show form to create new conf
    if not id_ and request.method == 'GET':
        context['engine_settings'] = engine_settings
        context['game_settings'] = game_settings
    # Create new conf
    elif not id_ and request.method == 'POST':
        save_conf(request.params)
        redirect("/admin")
    # Show edit conf
    elif id_ and request.method == 'GET':
        context['engine_settings'] = []
        context['game_settings'] = []
        conf = get_config(id_) 
        for setting, help_, _ in engine_settings:
            context['engine_settings'].append((setting, help_, conf['conf'][setting]))
        for setting, help_, _ in game_settings:
            context['game_settings'].append((setting, help_, conf['conf'][setting]))
    # Edit conf
    elif id_ and request.method == 'POST':
        save_conf(request.params)
        redirect("/admin")

    return context

def conf_delete(id_):
    context = {}
    context['page'] = 'admin'
    delete_conf(id_)
    redirect("/admin") 
