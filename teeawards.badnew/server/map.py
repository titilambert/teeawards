import os
import json
import shutil


class MapManager():

    def __init__(self):
        self.map_folder = "data/map"
        if not os.path.exists(self.map_folder):
            os.makedirs(self.map_folder)

    def save_map(self, params, edit=False):
        map_name = params['map_name'].decode('utf-8')
        map_folder = os.path.join(self.map_folder, map_name)
        if not os.path.exists(map_folder):
            os.makedirs(map_folder)
        if not edit:
            map_file_path = os.path.join(map_folder, map_name + ".map")
            with open(map_file_path, "wb") as mfh:
                mfh.write(params.get('map_file'))
            del(params['map_file'])

        if params.get('screenshot'):
            screenshot_path = os.path.join(map_folder, 'screenshot')
            with open(screenshot_path, "wb") as mfh:
                mfh.write(params.get('screenshot'))
        del(params['screenshot'])
    
        params = dict([(k, v.decode('utf-8')) for k, v in params.items()])
        map_path = os.path.join(map_folder, 'map.json')
        # TODO YAML
        with open(map_path, 'w') as cfh:
            json.dump(params, cfh)

    def get_maps(self, gametype=''):
        map_list = []
        for map_ in os.listdir(self.map_folder):
            map_conf = os.path.join(self.map_folder, map_, 'map.json')
            with open(map_conf, 'r') as mfh:
                data = json.load(mfh)
                if gametype == '':
                    map_list.append(data)
                elif gametype == data['prefered_mod']:
                    map_list.append(data)
        return map_list

    def get_mods(self):
        mod_list = set()
        for map_ in os.listdir(self.map_folder):
            map_conf = os.path.join(self.map_folder, map_, 'map.json')
            with open(map_conf, 'r') as mfh:
                data = json.load(mfh)
                mod_list.add(data['prefered_mod'])
        return mod_list

    def get_screenshot_path(self, map_name):
        map_screenshot_path = os.path.join(self.map_folder, map_name, 'screenshot')
        return map_screenshot_path

    def get_map(self, map_name):
        map_conf = os.path.join(self.map_folder, map_name, 'map.json')
        with open(map_conf, 'r') as mfh:
            data = json.load(mfh)
        return data

    def delete_map(self, server_name):
        map_folder = os.path.join(self.map_folder, map_name)
        if not os.path.isdir(map_folder):
            raise
        shutil.rmtree(map_folder)
