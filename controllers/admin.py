from time import sleep
import subprocess
import tarfile

from bottle import mako_view, request, response, redirect, static_file

from libs.lib import *
from libs.rank import get_rank
from libs.teeworldsserver import *
from libs.maps import *
from libs.hooks import *

@mako_view('admin')
@prepare_context
def admin(action=None,id_=None, context={}, gametype=None):
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
@prepare_context
def conf_edit(id_=None, context={}, gametype=None):
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
@prepare_context
def map_edit(id_=None, context={}, gametype=None):
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


def kick(player):
    econ_command_queue.put({'type': 'kick',
                            'data': {'player': player,
                                     'message': 'Kicked from website'
                                    }
                          })
    redirect("/admin")


def export():
    # Delete old dumps
    command = "rm -rf %s" % dump_folder
    p = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, errors = p.communicate()
    # Dump config tables
    for table in no_stats_tables:
        command = "mongodump -d teeworlds -c %s" % table.name
        p = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, errors = p.communicate()
    # Dump stats tables
    if 'stats' in request.params:
        for table in tables:
            command = "mongodump -d teeworlds -c %s" % table.name
            p = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, errors = p.communicate()
    file_name = 'teeawards_dump.tar.gz'
    file_path = os.path.join(data_folder, file_name)
    tf = tarfile.open(file_path, 'w:gz')
    # Add dumps
    tf.add(dump_folder, 'dump')
    # Add Maps
    tf.add(map_folder, 'map')
    # Add Map screenshots
    tf.add(map_screenshot_folder, 'map_screenshots')
    tf.close()
    return static_file(file_name, root=data_folder, download=file_name)

def restore():
    if 'dumpfile' in request.files:
        tf = tarfile.open(mode='r:gz', fileobj=(request.files['dumpfile'].file))
        mandatory_files = ['dump/teeworlds/maps.bson',
                           'dump/teeworlds/config.bson',
                           'map',
                           'map_screenshots']
        if set(mandatory_files).issubset(set(tf.getnames())):
            for f in tf.getnames():
                # TODO import dumps and send maps in good folder
                if f.startswith('dump/'):
                    tf.extract(f , data_folder + '/../restore_dump/')
                    if f.endswith('.bson'):
                        db = f.rsplit('/', 1)[-1].split(".")[0]
                        file_path = data_folder + '/../restore_dump/' + f
                        command = "mongorestore --collection teeworlds --db %s %s" % (db, file_path)
                        p = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        output, errors = p.communicate()
                elif f.startswith('map/'):
                    tf.extract(f, data_folder)
                elif f.startswith('map_screenshots/'):
                    tf.extract(f, data_folder)

    redirect("/admin")
