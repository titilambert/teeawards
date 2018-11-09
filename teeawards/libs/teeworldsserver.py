import threading
import time
import json
from datetime import datetime
import re
import select
import pty
import subprocess
import hashlib
import os
import socket

from pymongo import MongoClient
from bson.objectid import ObjectId
from gridfs import GridFS

from teeawards.libs.lib import conf_table, data_folder
from teeawards.libs.maps import export_maps
#from teeawards.libs.livestats import LiveStats


TIMEOUT = 2
PACKET_GETINFO2 = b"\xff\xff\xff\xff\xff\xff\xff\xff\xff\xffgie2" + b"\x00"
PACKET_GETINFO3 = b"\xff\xff\xff\xff\xff\xff\xff\xff\xff\xffgie3" + b"\x00"


engine_settings = [
    ('sv_name', 'Name of the server', b'unnamed server'),
    ('sv_bindaddr', 'Address to bind', b''),
    ('sv_port', 'Port the server will listen on', b'8303'),
    ('sv_external_port', 'Port to report to the master servers (e.g. in case of a firewall rename)', b'0'),
    ('sv_max_clients', 'Number of clients that can be connected to the server at the same time', b'12'),
    ('sv_max_clients_per_ip', 'Number of clients with the same ip that can be connected to the server at the same time', b'12'),
    ('sv_high_bandwidth', 'Use high bandwidth mode, for LAN servers only', b'1'),
    ('sv_register', 'Register on the master servers', b'0'),
    ('sv_map', 'Map to use', b'dm1'),
    ('sv_rcon_password', 'Password to access the remote console (if not set, rcon is disabled)', b''),
    ('password', 'Password to connect to the server', b''),
    ('logfile', 'Path to a logfile', b''),
    ('console_output_level', 'Adjust the amount of messages in the console', b'0'),
    ('sv_rcon_max_tries', 'Maximum number of tries for remote console authetication', b'3'),
    ('sv_rcon_bantime', 'Time (in minutes) a client gets banned if remote console authentication fails (0 makes it just use kick)', b'5'),
]
game_settings = [
    ('sv_warmup', 'Warmup time between rounds', b'0'),
    ('sv_scorelimit', 'Score limit of the game (0 disables it)', b'20'),
    ('sv_timelimit', 'Time limit of the game (in case of equal points there will be sudden death)', b'0'),
    ('sv_gametype', 'Gametype (dm/ctf/tdm) (This setting needs the map to be reloaded in order to take effect)', b'dm'),
    ('sv_maprotation', 'The maps to be rotated', b''),
    ('sv_rounds_per_map', 'Number of rounds before changing to next map in rotation', b'1'),
    ('sv_motd', ' Message of the day, shown in server info and when joining a server', b''),
    ('sv_spectator_slots', 'Number of clients that can only be spectators', b'0'),
    ('sv_teambalance_time', 'Time in minutes after the teams are uneven, to auto balance', b'1'),
    ('sv_spamprotection', 'Enable spam filter', b'False'),
    ('sv_tournament_mode', 'Players will automatically join as spectator', b'0'),
    ('sv_respawn_delay_tdm', 'Time in seconds needed to respawn in the tdm gametype', b'3'),
    ('sv_teamdamage', 'Enable friendly fire', b'1'),
    ('sv_powerups', 'Enable powerups (katana)', b'1'),
    ('sv_vote_kick', 'Enable kick voting', b'1'),
    ('sv_vote_kick_bantime', 'Time in minutes to ban a player if kicked by voting (0 equals only kick)', b'5'),
    ('sv_vote_kick_min', 'Minimum number of players required to start a kick vote', b'0'),
    ('sv_inactivekick_time', 'Time in minutes after an inactive player will be taken care of', b'3'),
    ('sv_inactivekick', 'How to deal with inactive players (0 = move to spectator, 1 = move to free spectator slot/kick, 2 = kick)', b'1'),
]
other_settings = [
    ('server_binary', 'Server Binary (empty means use system binary)', b''),
    ('server', 'old server binary', b''),
    ('record_stats', 'Records stats', b'1'),
]

def get_config(id_):
    return conf_table.find_one(ObjectId(id_))

def get_configs():
    return conf_table.find()

def delete_conf(id_):
    fs = GridFS(conf_table.database)
    res = fs.find_one({'filename': str(id_)})
    if res:
        fs.delete(res._id)
    conf_table.remove(ObjectId(id_))

def save_conf(request, id_=None):
    params = request

    name = params['sv_name']
    conf = dict([x for x in params.items()])
    server_binary = conf.get('server_binary')
    data = {'name': name, 'conf': conf}
    if id_ is not None:
        # NOT New config
        data = conf_table.find_one(ObjectId(id_))
        if data:
            if not server_binary:
                server_binary = data['conf']['server_binary']

            # Config exists
            data['conf'] = conf
            data['name'] = name
            if server_binary:
                data['conf']['server_binary'] = b''

    object_id = conf_table.save(data)

    if server_binary:
        fs = GridFS(conf_table.database)
        res = fs.find_one({'filename': str(object_id)})
        try:
            server_file = fs.new_file(filename=str(object_id))
            server_file.write(conf['server_binary'])
        finally:
            server_file.close()
            if res:
                fs.delete(res._id)

def export_conf(conf):
    filename = data_folder + '/teeworlds.conf'
    f = open(filename, 'w')
    for setting, value in conf['conf'].items():
        f.write("%s %s\n" % (setting, value.decode('utf-8')))

    # export external commands
    from teeawards.libs.lib import econ_port
    result = 0
    # FIXME: FIND EMPTY PORT
    while result == 0:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = s.connect_ex(('127.0.0.1', econ_port))
        econ_port += 1
    print("CONFIG", econ_port)
    f.write("ec_port %s\n" % econ_port)
    f.write("ec_password teeawards\n")
    f.write("ec_auth_timeout 10\n")
    f.write("ec_bantime 0\n")
    f.close()
    return filename, econ_port


class TeeWorldsServerManager(object):
    def __init__(self, influx_client):

        # Prepare db
        self.influx_client = influx_client
        self.con = MongoClient()
        tee_db = self.con['teeworlds']

    def get_server_info(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(TIMEOUT);
            sock.sendto(PACKET_GETINFO2, ('localhost', 8303))
            data, addr = sock.recvfrom(1400)
            sock.close()

            data = data[14:] # skip header
            slots = data.split("\x00")

            server_info = {}
            server_info["token"] = slots[0]
            server_info["version"] = slots[1]
            server_info["name"] = slots[2]
            server_info["map"] = slots[3]
            server_info["gametype"] = slots[4]
            server_info["flags"] = int(slots[5])
            server_info["num_players"] = int(slots[6])
            server_info["max_players"] = int(slots[7])
            server_info["num_clients"] = int(slots[8])
            server_info["max_clients"] = int(slots[9])
            server_info["players"] = []

            for i in xrange(0, server_info["num_clients"]):
                    player = {}
                    player["name"] = slots[10+i*5]
                    player["clan"] = slots[10+i*5+1]
                    player["country"] = int(slots[10+i*5+2])
                    player["score"] = int(slots[10+i*5+3])
                    if int(slots[10+i*5+4]):
                            player["player"] = True
                    else:
                            player["player"] = False
                    server_info["players"].append(player)

            return server_info

        except socket.timeout:
            sock.close()
            return None

    def start(self, conf_name):
        self.conf = get_config(conf_name)
        export_maps(self.conf)
        filename, real_econ_port = export_conf(self.conf)
        # Prepare server
        ## Prepare storage file
        f = open(os.path.join(data_folder,'storage.cfg'), 'w')
        # USELESS
        #f.write('add_path .')
        #f.write('add_path $USERDIR')
        #f.write('add_path $DATADIR')
        # END USELESS
        f.write('add_path $CURRENTDIR')
        f.close()
        # Server Command
        if self.conf['conf'].get('server', ''):
            # TODO fix me
            server_bin = self.conf['conf']['server']
        else:
            server_bin = "`which teeworlds-server`"
#        self.command = 'cd %s && %s -f %s' % (data_folder, server_bin, os.path.abspath(filename))
        self.command = '%s -f %s' % (server_bin, os.path.basename(filename))
        # Open pty
        master, slave = pty.openpty()
        # Launch server
        print(self.command)
        self.process = subprocess.Popen(self.command, shell=True, stdin=subprocess.PIPE, stdout=slave, stderr=slave, close_fds=True, cwd=data_folder)

        # Init thread
        self.server = TeeWorldsServer(self, master)
#        self.live_stats = LiveStats()
        # Start Server
        self.server.start()
        # Start live stats thread
#        self.live_stats.start()
        # Econ client
#        econ_client.set_econ_port(real_econ_port)



class TeeWorldsServer(threading.Thread):
    def __init__(self, manager, master):
        threading.Thread.__init__(self)
        self.manager = manager

        self.process = manager.process
        self.master = master

        self.stop = threading.Event()
        self.debug = True

    def stop_server(self):
        self.stop.set()

    def stopped(self):
        return self.stop.isSet()

    def run(self):

        timeout = 2
        self.round_ = None
        self.gametype = None
        self.teams = {}
        # Map is None at Starting then is it possible ???
        self.map_ = None
        if self.debug:
            f = open('teeawards.log', 'w')

        last_line = ''
        while not self.stopped():
            ready, _, _ = select.select([self.master], [], [], timeout)
            if not ready:
                continue
            lines = os.read(self.master, 512)
            if self.manager.conf['conf'].get('record_stats', '1') == '0':
                continue
            for line in lines.splitlines():
                # Skip empty lines
                if line == '':
                    continue
                # Handle splitted lines
                if not re.match(b"^\[[a-z0-9]*\]\[", line):
                    line = last_line.strip() + line.strip()
                # Join team:
                if re.match(b"\[(.*)\]\[game\]: team_join player='.*:(.*)' team=(.*)", line):
                    when, player, team = re.match(b"\[(.*)\]\[game\]: team_join player='.*:(.*)' team=(.*)", line).groups()
                    if self.debug:
                        print("JOIN: ", player, team)
                    when = datetime.fromtimestamp(int(when, 16))
                    team = team.strip()
                    player = player.strip()
                    data = [{"measurement": "join",
                             "tags": {"player": player.decode('utf-8'),
                                      "team": team.decode('utf-8'),
                                      "gametype": self.gametype.decode('utf-8') if self.gametype else "",
                                      "round": self.round_,
                                      "map": self.map_.decode('utf-8') if self.map_ else "",
                                     },
                             "time": when.strftime("%Y-%m-%dT%H:%M:%S%Z"),
                             "fields": {"value": 1}
                             }]
                    self.manager.influx_client.write_points(data)

                    #live_stats_queue.put({'type': 'join', 'data': data})
                    # save team for other stats
                    self.teams[player] = team
                # Start round
                elif re.match(b"\[(.*)\]\[game\]: start match type='(.*)' teamplay='([0-9]*)'", line):
                    when, gametype, teamplay = re.match(b"\[(.*)\]\[game\]: start match type='(.*)' teamplay='([0-9]*)'", line).groups()
                    when = datetime.fromtimestamp(int(when, 16))
                    # NEED TO BE SURE THAT IS NOT A STARTROUND JUST BEFORE A CHANGE MAP .... handled in changemap section (the next one) 
                    print("START ROUND:", gametype, "TEAMPLAY", teamplay, self.map_)
                    round = time.time()
                    data = [{"measurement": "round",
                             "tags": {"teamplay": teamplay.decode('utf-8'),
                                      "gametype": self.gametype.decode('utf-8') if self.gametype else "",
                                      "map": self.map_.decode('utf-8') if self.map_ else "",
                                     },
                             "time": when.strftime("%Y-%m-%dT%H:%M:%S%Z"),
                             "fields": {"round": round}
                             }]
                    self.round_ = round
                    self.gametype = gametype
                    self.manager.influx_client.write_points(data)
                # Change map
                elif re.match(b"\[(.*)\]\[datafile\]: loading done. datafile='(.*)'", line):
                    when, raw_map = re.match(b"\[(.*)\]\[datafile\]: loading done. datafile='(.*)'", line).groups()
                    when = datetime.fromtimestamp(int(when, 16))
                    map_name = os.path.basename(raw_map)
                    data = [{"measurement": "map",
                             "tags": {"map": map_name.decode('utf-8'),
                                     },
                             "time": when.strftime("%Y-%m-%dT%H:%M:%S%Z"),
                             "fields": {"value": 1}
                             }]
                    self.map_ = map_name
                    #data = {'when': when,  'map': map_name.strip()}
                    #self.map_ = self.manager.map_table.save(data)
                    # DELETE BAD LAST ROUND
                    if self.round_:
                        print("DELETE BAD LAST ROUND")
                        # TODO: handle that
                        self.manager.round_table.remove(self.round_)
                    print("CHANGE MAP", map_name, self.map_)
                    self.round_ = None
                    self.gametype = None
                    self.teams = {}
                    self.manager.influx_client.write_points(data)
                # Pickup
                elif re.match(b"\[(.*)\]\[game\]: pickup player='.*:(.*)' item=(.*)$", line):
                    when, player, item = re.match(b"\[(.*)\]\[game\]: pickup player='.*:(.*)' item=(.*)$", line).groups()
                    when = datetime.fromtimestamp(int(when, 16))
                    print("PICKUP: ", when, player, item)
                    player = player.strip()

                    data = [{"measurement": "pickup",
                             "tags": {"player": player.decode('utf-8'),
                                      "gametype": self.gametype.decode('utf-8') if self.gametype else "",
                                      "round": self.round_,
                                      "map": self.map_.decode('utf-8') if self.map_ else "",
                                      "item": item.strip().decode('utf-8'),
                                     },
                             "time": when.strftime("%Y-%m-%dT%H:%M:%S%Z"),
                             "fields": {"value": 1}
                             }]
                    self.manager.influx_client.write_points(data)
                # Kill
                elif re.match(b"\[(.*)\]\[game\]: kill killer='.*:(.*)' victim='.*:(.*)' weapon=(.*) special=(.*)", line):
                    when, killer, victim, weapon, special = re.match(b"\[(.*)\]\[game\]: kill killer='.*:(.*)' victim='.*:(.*)' weapon=(.*) special=(.*)", line).groups()
                    when = datetime.fromtimestamp(int(when, 16))
                    print(when, killer, "KILL", victim, "with", weapon, "and special", special)
                    killer = killer.strip()
                    victim = victim.strip()
                    weapon = weapon.strip()
                    special = special.strip()
                    data = [{"measurement": "kills",
                             "tags": {"killer": killer.decode('utf-8'),
                                      "victim": victim.decode('utf-8'),
                                      "killer_team": self.teams[killer],
                                      "victim_team": self.teams[victim],
                                      "weapon": weapon.decode('utf-8'),
                                      "special": special.decode('utf-8'),
                                      "gametype": self.gametype.decode('utf-8') if self.gametype else "",
                                      "round": self.round_,
                                      "map": self.map_.decode('utf-8') if self.map_ else "",
                                     },
                             "time": when.strftime("%Y-%m-%dT%H:%M:%S%Z"),
                             "fields": {"value": 1}
                             }]
                    self.manager.influx_client.write_points(data)
                    #live_stats_queue.put({'type': 'kill', 'data': data})
                # Other
                else:
                    if self.debug:
                        f.write("NON CAPTURED LINE: " + line.decode('utf-8'))
                        f.write("\n")
                        print("NON CAPTURED LINE: {}".format(line))
                # Save last line
                last_line = line

