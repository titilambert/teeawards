import os

from bson.objectid import ObjectId

from gridfs import GridFS

from teeawards.libs.lib import maps_table, data_folder


def get_maps(gametype=None):
    if gametype:
        return maps_table.find({'map.prefered_mod':  gametype.encode('utf-8')})
    else:
        return maps_table.find()

def get_map_mods():
    return set([x['map']['prefered_mod']
                for x in maps_table.find({}, ['map.prefered_mod'])])

def export_maps(conf):
    # TODO handle multiples ????
    map_name = conf['conf']['sv_map']
    map_ = maps_table.find_one({'name': map_name})
    fs = GridFS(maps_table.database)
    res = fs.find_one({'filename': str(map_['_id']) + ".map"})

    map_file = os.path.join(data_folder, "maps", map_name.decode('utf-8') + ".map")
    if not os.path.exists(os.path.join(data_folder, 'maps')):
        os.makedirs(os.path.join(data_folder, 'maps'))

    with open(map_file, "wb") as fhm:
        fhm.write(res.read())
    print(map_file)

def get_map(id_):
    return maps_table.find_one(ObjectId(id_))

def get_screenshot(id_):
    fs = GridFS(maps_table.database)
    return fs.find_one({'filename': id_ + ".png"})

def delete_map(id_):
    fs = GridFS(maps_table.database)
    res = fs.find_one({'filename': str(id_) + ".map"})
    if res:
        fs.delete(res._id)
    res = fs.find_one({'filename': str(id_) + ".png"})
    if res:
        fs.delete(res._id)
    maps_table.remove(ObjectId(id_))

def save_map(params, id_=None):

    map_name = params['map_name']

    data = {}
    data['map'] = {}
    if id_ is not None:
        data = maps_table.find_one(ObjectId(id_))
        if data is None:
            # New map
            if not params.get('map_file'):
                # Need a file for new map
                return False
            if not params.get('screenshot'):
                # Need a file for new map
                return False

    data['name'] = map_name
    # TODO check map with same name

    data['map']['map_name'] = params['map_name']
    data['map']['prefered_mod'] = params['prefered_mod']
    data['map']['min_players'] = params['min_players']
    data['map']['max_players'] = params['max_players']

    object_id = maps_table.save(data)

    if params.get('map_file'):
        fs = GridFS(maps_table.database)
        res = fs.find_one({'filename': str(object_id) + ".map"})
        try:
            server_file = fs.new_file(filename=str(object_id) + ".map", type="map")
            server_file.write(params.get('map_file'))
        finally:
            server_file.close()
            if res:
                fs.delete(res._id)
    if params.get('screenshot'):
        fs = GridFS(maps_table.database)
        # TODO convert all screenhosts to png
        res = fs.find_one({'filename': str(object_id) + ".png"})
        try:
            server_file = fs.new_file(filename=str(object_id) + ".png", type="screenshot")
            server_file.write(params.get('screenshot'))
        finally:
            server_file.close()
            if res:
                fs.delete(res._id)

    return True
