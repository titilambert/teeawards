import os
import json
import shutil
import socket

from teeawards.server.const import ECON_PORT


class ConfigManager():

    ECON_PORT = ECON_PORT

    def __init__(self):
        self.conf_folder = "data/teeawards/config"
        self.data_folder = "data"
        if not os.path.exists(self.conf_folder):
            os.makedirs(self.conf_folder)

    def save_conf(self, params):
        server_name = params['sv_name'].decode('utf-8').replace("/", "_").replace(" ", "_")
        conf_folder = os.path.join(self.conf_folder, server_name)
        if not os.path.exists(conf_folder):
            os.makedirs(conf_folder)
        if params.get('server_binary'):
            server_bin_path = os.path.join(conf_folder, 'teeworlds-server')
            with open(server_bin_path, "wb") as sfh:
                sfh.write(params.get('server_binary'))
            os.chmod(server_bin_path, 755)
            params['server'] = server_bin_path.encode('utf-8')
            del(params['server_binary'])

        params = dict([(k, v.decode('utf-8')) for k, v in params.items()])
        conf_path = os.path.join(conf_folder, 'config.json')
        # TODO YAML
        with open(conf_path, 'w') as cfh:
            json.dump(params, cfh)

    def get_conf(self, server_name):
        conf_folder = os.path.join(self.conf_folder, server_name)
        if not os.path.isdir(conf_folder):
            raise
        conf_path = os.path.join(conf_folder, 'config.json')
        with open(conf_path, 'r') as cfh:
            conf = json.load(cfh)
        return conf

    def list_conf(self):
        conf_list = []
        for file_ in os.listdir(self.conf_folder):
            conf_folder = os.path.join(self.conf_folder, file_)
            if os.path.isdir(conf_folder):
                conf_list.append({'name': file_, '_id': file_})
        return conf_list

    def delete_conf(self, server_name):
        conf_folder = os.path.join(self.conf_folder, server_name)
        if not os.path.isdir(conf_folder):
            raise
        shutil.rmtree(conf_folder)

    def export_conf(self, server_name):

        filename = self.data_folder + '/teeworlds.conf'
        f = open(filename, 'w')
        conf = self.get_conf(server_name)
        for setting, value in conf.items():
            f.write("%s %s\n" % (setting, value))

        # export external commands
        result = 0
        # FIXME: FIND EMPTY PORT
        ECON_PORT = self.ECON_PORT
        while result == 0:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = s.connect_ex(('127.0.0.1', ECON_PORT))
            ECON_PORT += 1
        print("CONFIG", ECON_PORT)
        f.write("ec_port %s\n" % ECON_PORT)
        f.write("ec_password teeawards\n")
        f.write("ec_auth_timeout 10\n")
        f.write("ec_bantime 0\n")
        f.close()
        return filename, ECON_PORT

