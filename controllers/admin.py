from bottle import mako_view, request, response, redirect
from libs.lib import *
from libs.rank import get_rank
from libs.teeworldsserver import *
from libs.maps import *
from time import sleep

@mako_view('admin')
def admin(action=None,id_=None):
    context = {}
    context['page'] = 'admin'
    context['engine_settings'] = None
    context['game_settings'] = None
    context['config_list'] = get_configs()
    context['map_list'] = get_maps()
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
    context['other_settings'] = None
    context['engine_settings'] = None
    context['game_settings'] = None
    context['id'] = id_ if id_ else ''

    # show form to create new conf
    if not id_ and request.method == 'GET':
        context['other_settings'] = other_settings
        context['engine_settings'] = engine_settings
        context['game_settings'] = game_settings
    # Create new conf
    elif not id_ and request.method == 'POST':
        save_conf(request)
        redirect("/admin")
    # Show edit conf
    elif id_ and request.method == 'GET':
        context['engine_settings'] = []
        context['game_settings'] = []
        context['other_settings'] = []
        conf = get_config(id_) 

        for setting, help_, _ in engine_settings:
            if not setting in conf['conf']:
                conf['conf'][setting] = ''
            context['engine_settings'].append((setting, help_, conf['conf'][setting]))
        for setting, help_, _ in game_settings:
            if not setting in conf['conf']:
                conf['conf'][setting] = ''
            context['game_settings'].append((setting, help_, conf['conf'][setting]))
        for setting, help_, _ in other_settings:
            if not setting in conf['conf']:
                conf['conf'][setting] = ''
            context['other_settings'].append((setting, help_, conf['conf'][setting]))
    # Edit conf
    elif id_ and request.method == 'POST':
        save_conf(request)
        redirect("/admin")

    return context

def conf_delete(id_):
    delete_conf(id_)
    redirect("/admin") 

@mako_view('map')
def map_edit(id_=None):
    context = {}
    context['page'] = 'admin'
    context['id'] = id_ if id_ else ''

    # show form to create new map
    if not id_ and request.method == 'GET':
        context['map'] = None
        pass
    # Create new map
    elif not id_ and request.method == 'POST':
        save_map(request)
        redirect("/admin")
    # Save map
    elif id_ and request.method == 'POST':
        save_map(request)
        redirect("/admin")
    # Show edit map
    elif id_ and request.method == 'GET':
        context['map'] = get_map(id_)

    return context


def map_delete(id_):
    delete_map(id_)
    redirect("/admin")


def reset_data():
    empty_db()
    redirect("/admin")
