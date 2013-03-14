import os

from bson.objectid import ObjectId

from libs.lib import *


def get_map(name):
    maps = maps_table.find_one({'name': name})
    return maps

def get_maps():
    return maps_table.find()

def save_map(request):
    #params = [x for x in request.params.items()]
    #files = [x for x in request.files.items()]
    
    if 'map_name' in request.params:
        # Name in request => Edit map
        map_name = request.params['map_name']
        data = maps_table.find_one({'name': map_name})
    else:
        # no name in request => New map
        if not 'map_file' in request.files:
            # Need a file for new map
            return False
        name = request.files['map_file'].filename
        map_name = name[:-4]
        if not map_name or not name.endswith('.map'):
            return False
        data = {}
        data['name'] = map_name
        data['map'] = {}


    if 'screenshot' in request.files:
        ext = request.files['screenshot'].filename.rsplit('.', 1)[-1]
        filename = ".".join((map_name, ext))
        if os.path.exists(os.path.join(map_screenshot_folder, filename)):
            os.remove(os.path.join(map_screenshot_folder, filename))
        request.files['screenshot'].save(map_screenshot_folder)

    prefered_mod = request.params['prefered_mod']
    min_players = request.params['min_players']
    max_players = request.params['max_players']

    data['map']['prefered_mod'] = prefered_mod
    data['map']['min_players'] = min_players
    data['map']['max_players'] = max_players
    
    if 'map_file' in request.files:
        filename = request.files['map_file'].filename
        if os.path.exists(os.path.join(map_folder, filename)):
            os.remove(os.path.join(map_folder, filename))
        request.files['map_file'].save(map_folder)

    maps_table.save(data)
    return True

def delete_map(id_):
    maps_table.remove(ObjectId(id_))

