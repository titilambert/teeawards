#!/usr/bin/python
import time
from socket import socket, AF_INET, SOCK_DGRAM
from subprocess import Popen, PIPE, STDOUT
import pty
import threading
import os
import sys
import re
from datetime import datetime
import select


from teeawards.server.const import ECON_PORT
from teeawards.server.livestats import LiveStats

#from pymongo import Connection
#from bson.objectid import ObjectId

#from libs.lib import conf_table, data_folder, server_folder
#from libs.livestats import LiveStats
#from libs.econ import econ_client
#from libs.lib import live_stats_queue, econ_command_queue, econ_port


TIMEOUT = 2
PACKET_GETINFO3 = b"\xff\xff\xff\xff\xff\xff\xff\xff\xff\xffgie3" + b"\x00"

class TeeWorldsServerManager(object):
    def __init__(self, conf_mgr, econ_client, influx_client):

        self.data_folder = "data"
        self.influx_client = influx_client
        self.econ_client = econ_client
        self.conf_mgr = conf_mgr
        # Prepare db
#        self.con = Connection()
#        tee_db = self.con['teeworlds']
        # Prepare table
#        self.join_table = tee_db['join']
#        self.changeteam_table = tee_db['changeteam']
#        self.changename_table = tee_db['changename']
#        self.round_table = tee_db['round']
#        self.map_table = tee_db['map']
#        self.kick_table = tee_db['kick']
#        self.timeout_table = tee_db['timeout']
#        self.leave_table = tee_db['leave']
#        self.servershutdown_table = tee_db['servershutdown']
#        self.pickup_table = tee_db['pickup']
#        self.kill_table = tee_db['kill']
#        self.flaggrab_table = tee_db['flaggrab']
#        self.flagreturn_table = tee_db['flagreturn']
#        self.flagcapture_table = tee_db['flagcapture']
        self.server_executable = None
        self.conf = None
        self.process = None
        self.last_server_info_time = 0
        self.server_info = None

    def is_alive(self):
        if not hasattr(self, 'server'):
            return False
        return self.server.is_alive()

    def get_server_info(self):
        # TODO: Put this in a thread
        if self.last_server_info_time + 10 < time.time:
            return self.server_info
        
        try:
            sock = socket(AF_INET, SOCK_DGRAM)
            sock.settimeout(TIMEOUT);
            sock.sendto(PACKET_GETINFO3, ('localhost',8303))
            data, addr = sock.recvfrom(1400)
            sock.close()

            data = data[14:] # skip header
            slots = data.decode('utf-8').split("\x00")

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

            for i in range(0, server_info["num_clients"]):
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

            self.server_info = server_info
            return server_info

        except Exception: 
            sock.close()
            return None


    def start(self, conf_name):
        self.conf = self.conf_mgr.get_conf(conf_name)
        filename, real_econ_port = self.conf_mgr.export_conf(conf_name)
        # Prepare server
        ## Prepare storage file
        f = open(os.path.join(self.data_folder,'storage.cfg'), 'w')
        # USELESS
        #f.write('add_path .')
        #f.write('add_path $USERDIR')
        #f.write('add_path $DATADIR')
        # END USELESS
        f.write('add_path $CURRENTDIR')
        f.close()
        # Server Command
        if self.conf.get('server', ''):
            server_bin = self.conf['server']
        else:
            server_bin = "`which teeworlds-server`"
        self.command = '%s -f %s' % (server_bin, filename)
        # Open pty
        master, slave = pty.openpty()
        # Launch server
        self.process = Popen(self.command, shell=True, stdin=PIPE, stdout=slave, stderr=slave, close_fds=True)

        # Init thread
        self.server = TeeWorldsServer(self, master, self.influx_client)
        self.live_stats = LiveStats(self.econ_client.queue)
        # Start Server
        self.server.start()
        #self.server.run()
        # Start live stats thread
        self.live_stats.start()
        # Econ client
        self.econ_client.set_econ_port(real_econ_port)

    def stop(self):
        if self.process:
            # Stop thread
            self.live_stats.stop_server()
            self.server.stop_server()
            # Kill  childs
            ps_command = Popen("ps -o pid --ppid %d --noheaders" % self.process.pid, shell=True, stdout=PIPE)
            ps_output = ps_command.stdout.read()
            retcode = ps_command.wait()
            #assert retcode == 0, "ps command returned %d" % retcode
            for pid_str in ps_output.split("\n")[:-1]:
                os.kill(int(pid_str), 15)
            # Kill teeworlds server !!
            self.process.terminate()
            self.process.wait()
            data = {'when': datetime.now(), 'round': self.server.round_, 'map': self.server.map_}
            self.servershutdown_table.save(data)
            self.process = None
            return True
        return False

class TeeWorldsServer(threading.Thread):
    def __init__(self, manager, master, influx_client):
        threading.Thread.__init__(self)
        self.influx_client = influx_client
        # TODO remove manager
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
#            print "read"
            ready, _, _ = select.select([self.master], [], [], timeout)
            if not ready:
                continue
            lines = os.read(self.master, 512)
            if self.manager.conf.get('record_stats', '1') == '0':
                continue

            for line in lines.splitlines():
                # Skip empty lines
                if not line:
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
                    when = when.strftime("%Y-%m-%dT%H:%M:%SZ")

                    team = team.strip()
                    player = player.strip()
                    data = {'measurement': 'join',
                            'time': when,
                            'tags': {'team': team,
                                     'round': self.round_,
                                     'map': self.map_,
                                     'gametype': self.gametype,
                                     },
                            'fields': {'player': player,
                                       }
                            }
                    self.influx_client.write_points([data])
                    self.live_stats.queue.put({'type': 'join', 'data': data})
                    # save team for other stats
                    self.teams[player] = team
                # Change team
                elif re.match(b"\[(.*)\]\[game\]: team_join player='.*:(.*)' m_Team=(.*)", line):
                    when, player, team = re.match(b"\[(.*)\]\[game\]: team_join player='.*:(.*)' m_Team=(.*)", line).groups()
                    if self.debug:
                        print("Change team:", player, team)

                    when = datetime.fromtimestamp(int(when, 16))
                    when = when.strftime("%Y-%m-%dT%H:%M:%SZ")

                    team = team.strip()
                    player = player.strip()
                    data = {'measurement': 'change_team',
                            'time': when,
                            'tags': {'round': self.round_,
                                     'map': self.map_,
                                     'gametype': self.gametype,
                                     'player': player,
                                     },
                            'fields': {'old_team': self.teams[player],
                                       'new_team': team,
                                       }
                            }
                    self.influx_client.write_points([data])
                    # save team for other stats
                    self.teams[player] = team
                # Change name
                    # KICK THE PLAYER !!!!!
                    # JUST FOR don't fuck stats or NOT ??
                elif re.match(b"\[(.*)\]\[chat\]: \*\*\* '(.*)' changed name to '(.*)'", line):
                    when, name, new_name = re.match(b"\[(.*)\]\[chat\]: \*\*\* '(.*)' changed name to '(.*)'", line).groups()
                    if self.debug:
                        print("Change name: ", name, " -> ", new_name)

                    when = datetime.fromtimestamp(int(when, 16))
                    when = when.strftime("%Y-%m-%dT%H:%M:%SZ")

                    data = {'measurement': 'change_name',
                            'time': when,
                            'tags': {'round': self.round_,
                                     'map': self.map_,
                                     'gametype': self.gametype,
                                     'player': name.strip(),
                                     },
                            'fields': {'old_name': name.strip(),
                                       'new_name': new_name.strip(),
                                       }
                            }
                    self.influx_client.write_points([data])

                    econ_command_queue.put({'type': 'kick',
                                            'data': {'player': new_name,
                                                     'message': 'You have to reconnect when you change your name'
                                                    }
                                           })
                # Start round
                elif re.match(b"\[(.*)\]\[game\]: start round type='(.*)' teamplay='([0-9]*)'", line):
                    when, gametype, teamplay = re.match(b"\[(.*)\]\[game\]: start round type='(.*)' teamplay='([0-9]*)'", line).groups()
                    when = datetime.fromtimestamp(int(when, 16))
                    when = when.strftime("%Y-%m-%dT%H:%M:%SZ")


                    # NEED TO BE SURE THAT IS NOT A STARTROUND JUST BEFORE A CHANGE MAP .... handled in changemap section (the next one) 
                    if self.debug:
                        print("START ROUND:", gametype, "TEAMPLAY", teamplay, self.map_)

                    data = {'measurement': 'round_start',
                            'time': when,
                            'tags': {
                                     'map': self.map_,
                                     'gametype': self.gametype,
                                     'teamplay': teamplay.strip(),
                                     },
                            'fields': {'round': self.round_,}
                            }
                    self.influx_client.write_points([data])

                    self.gametype = gametype
                # Change map
                elif re.match(b"\[(.*)\]\[datafile\]: loading done. datafile='(.*)'", line):
                    when, raw_map = re.match(b"\[(.*)\]\[datafile\]: loading done. datafile='(.*)'", line).groups()

                    when = datetime.fromtimestamp(int(when, 16))
                    when = when.strftime("%Y-%m-%dT%H:%M:%SZ")

                    map_name = os.path.basename(raw_map)
                    data = {'measurement': 'map', 'time': when, 'fields': {'map': map_name.strip().decode('utf-8')}}
                    if self.debug:
                        print("CHANGE MAP {} to {}".format(self.map_, map_name))
                    self.map_ = map_name.strip().decode('utf-8')
                    self.influx_client.write_points([data])
#                    self.map_ = self.manager.map_table.save(data)
                    # DELETE BAD LAST ROUND
                    if self.round_:
                        if self.debug:
                            print("DELETE BAD LAST ROUND")
                        self.manager.round_table.remove(self.round_)

                    self.round_ = None
                    self.gametype = None
                    self.teams = {}
                # Kick
                elif re.match(b"\[(.*)\]\[chat\]: \*\*\* '(.*)' has left the game \(Kicked for inactivity\)", line):
                    when, player = re.match(b"\[(.*)\]\[chat\]: \*\*\* '(.*)' has left the game \(Kicked for inactivity\)", line).groups()
                    if self.debug:
                        print("KICKED", player)

                    when = datetime.fromtimestamp(int(when, 16))
                    when = when.strftime("%Y-%m-%dT%H:%M:%SZ")

                    player = player.strip()

                    data = {'measurement': 'kick',
                            'time': when,
                            'tags': {
                                     'map': self.map_,
                                     'gametype': self.gametype,
                                     'round': self.round_,
                                     'team': self.teams.get(player, None),
                                     },
                            'fields': {'player': player,}
                            }
                    self.influx_client.write_points([data])

                # Timeout
                elif re.match(b"\[(.*)\]\[chat\]: \*\*\* '(.*)' has left the game \(Timeout\)", line):
                    when, player = re.match(b"\[(.*)\]\[chat\]: \*\*\* '(.*)' has left the game \(Timeout\)", line).groups()
                    if self.debug:
                        print("TIMEOUT", player)
                    player = player.strip()

                    when = datetime.fromtimestamp(int(when, 16))
                    when = when.strftime("%Y-%m-%dT%H:%M:%SZ")

                    data = {'measurement': 'timeout',
                            'time': when,
                            'tags': {
                                     'map': self.map_,
                                     'gametype': self.gametype,
                                     'round': self.round_,
                                     'team': self.teams.get(player, None),
                                     },
                            'fields': {'player': player,}
                            }
                    self.influx_client.write_points([data])
                # Leave game
                elif re.match(b"\[(.*)\]\[game\]: leave player='[0-9]*:(.*)'", line):
                    when, player = re.match(b"\[(.*)\]\[game\]: leave player='[0-9]*:(.*)'", line).groups()
                    if self.debug:
                        print("LEAVE", player)
                        print(line)

                    when = datetime.fromtimestamp(int(when, 16))
                    when = when.strftime("%Y-%m-%dT%H:%M:%SZ")

                    player = player.strip()

                    data = {'measurement': 'leave',
                            'time': when,
                            'tags': {
                                     'map': self.map_,
                                     'gametype': self.gametype,
                                     'round': self.round_,
                                     'team': self.teams.get(player, None),
                                     },
                            'fields': {'player': player,}
                            }
                    self.influx_client.write_points([data])
                # Pickup
                elif re.match(b"\[(.*)\]\[game\]: pickup player='.*:(.*)' item=(.*)$", line):
                    when, player, item = re.match(b"\[(.*)\]\[game\]: pickup player='.*:(.*)' item=(.*\/.*)$", line).groups()

                    when = datetime.fromtimestamp(int(when, 16))
                    when = when.strftime("%Y-%m-%dT%H:%M:%SZ")

                    if self.debug:
                        print("PICKUP: ", when, player, item)

                    data = {'measurement': 'pickup',
                            'time': when,
                            'tags': {
                                     'map': self.map_,
                                     'gametype': self.gametype,
                                     'round': self.round_,
                                     'team': self.teams.get(player, None),
                                     'player': player.strip(),
                                     },
                            'fields': {'item': item.strip()}
                            }
                    self.influx_client.write_points([data])
                # Kill
                elif re.match(b"\[(.*)\]\[game\]: kill killer='.*:(.*)' victim='.*:(.*)' weapon=(.*) special=(.*)", line):
                    when, killer, victim, weapon, special = re.match(b"\[(.*)\]\[game\]: kill killer='.*:(.*)' victim='.*:(.*)' weapon=(.*) special=(.*)", line).groups()

                    when = datetime.fromtimestamp(int(when, 16))
                    when = when.strftime("%Y-%m-%dT%H:%M:%SZ")

                    if self.debug:
                        print(when, killer, "KILL", victim, "with", weapon, "and special", special)
                    data = {'measurement': 'kill',
                            'time': when,
                            'tags': {
                                     'map': self.map_,
                                     'round': self.round_,
                                     'gametype': self.gametype,
                                     'killer_team': self.teams[killer],
                                     'victim_team': self.teams[victim],
                                     },
                            'fields': {
                                     'killer': killer.strip(),
                                     'victim': victim.strip(),
                                     'weapon': weapon.strip(),
                                     'special': special.strip(),
                                     }
                            }
                    self.influx_client.write_points([data])

                    self.live_stats.queue.put({'type': 'kill', 'data': data})
                # Get Flag
                elif re.match(b"\[(.*)\]\[game\]: flag_grab player='.*:(.*)'", line):
                    when, player = re.match(b"\[(.*)\]\[game\]: flag_grab player='.*:(.*)'", line).groups()

                    when = datetime.fromtimestamp(int(when, 16))
                    when = when.strftime("%Y-%m-%dT%H:%M:%SZ")

                    data = {'measurement': 'flag_grab',
                            'time': when,
                            'tags': {
                                     'map': self.map_,
                                     'round': self.round_,
                                     'gametype': self.gametype,
                                     'team': self.teams.get(player, None)
                                     },
                            'fields': {
                                     'player': player.strip(),
                                     }
                            }
                    self.influx_client.write_points([data])

                # Return Flag
                elif re.match(b"\[(.*)\]\[game\]: flag_return player='.*:(.*)'", line):
                    when, player = re.match(b"\[(.*)\]\[game\]: flag_return player='.*:(.*)'", line).groups()

                    when = datetime.fromtimestamp(int(when, 16))
                    when = when.strftime("%Y-%m-%dT%H:%M:%SZ")

                    data = {'when': when, 'player': player, 'round': self.round_, 'map': self.map_, 'gametype': self.gametype, 'team': self.teams.get(player, None)}
                    if self.debug:
                        print(when, player, "RETURN FLAG")
                    self.manager.flagreturn_table.save(data)

                    data = {'measurement': 'flag_return',
                            'time': when,
                            'tags': {
                                     'map': self.map_,
                                     'round': self.round_,
                                     'gametype': self.gametype,
                                     'team': self.teams.get(player, None)
                                     },
                            'fields': {
                                     'player': player.strip(),
                                     }
                            }
                    self.influx_client.write_points([data])
                # Capture Flag
                elif re.match(b"\[(.*)\]\[game\]: flag_capture player='.*:(.*)'", line):
                    when, player = re.match(b"\[(.*)\]\[game\]: flag_capture player='.*:(.*)'", line).groups()

                    when = datetime.fromtimestamp(int(when, 16))
                    when = when.strftime("%Y-%m-%dT%H:%M:%SZ")

                    player = player.strip()
                    data = {'when': when, 'player': player, 'round': self.round_, 'map': self.map_, 'gametype': self.gametype, 'team': self.teams.get(player, None)}
                    if self.debug:
                        print(when, player, "CAPTURE FLAG")
                    self.manager.flagcapture_table.save(data)
                # Other
                else:
                    if self.debug:
                        f.write("NON CAPTURED LINE: " + line.decode('utf-8'))
                        f.write("\n")
                        print(b"NON CAPTURED LINE", line)
                # Save last line
                last_line = line

        if self.debug:
            f.close()

engine_settings = [
    ('sv_name', 'Name of the server', 'unnamed server'),
    ('sv_bindaddr', 'Address to bind', ''),
    ('sv_port', 'Port the server will listen on', '8303'),
    ('sv_external_port', 'Port to report to the master servers (e.g. in case of a firewall rename)','0'),
    ('sv_max_clients', 'Number of clients that can be connected to the server at the same time', '12'),
    ('sv_max_clients_per_ip', 'Number of clients with the same ip that can be connected to the server at the same time', '12'),
    ('sv_high_bandwidth', 'Use high bandwidth mode, for LAN servers only', '1'),
    ('sv_register', 'Register on the master servers', '0'),
    ('sv_map', 'Map to use', 'dm1'),
    ('sv_rcon_password', 'Password to access the remote console (if not set, rcon is disabled)', ''),
    ('password', 'Password to connect to the server', ''),
    ('logfile', 'Path to a logfile', ''),
    ('console_output_level', 'Adjust the amount of messages in the console', '0'),
    ('sv_rcon_max_tries', 'Maximum number of tries for remote console authetication', '3'),
    ('sv_rcon_bantime', 'Time (in minutes) a client gets banned if remote console authentication fails (0 makes it just use kick)', '5'),
    ]
game_settings = [
    ('sv_warmup', 'Warmup time between rounds', '0'),
    ('sv_scorelimit', 'Score limit of the game (0 disables it)', '20'),
    ('sv_timelimit', 'Time limit of the game (in case of equal points there will be sudden death)', '0'),
    ('sv_gametype', 'Gametype (dm/ctf/tdm) (This setting needs the map to be reloaded in order to take effect)', 'dm'),
    ('sv_maprotation', 'The maps to be rotated', ''),
    ('sv_rounds_per_map', 'Number of rounds before changing to next map in rotation', '1'),
    ('sv_motd', ' Message of the day, shown in server info and when joining a server', ''),
    ('sv_spectator_slots', 'Number of clients that can only be spectators', '0'),
    ('sv_teambalance_time', 'Time in minutes after the teams are uneven, to auto balance', '1'),
    ('sv_spamprotection', 'Enable spam filter', 'False'),
    ('sv_tournament_mode', 'Players will automatically join as spectator', '0'),
    ('sv_respawn_delay_tdm', 'Time in seconds needed to respawn in the tdm gametype', '3'),
    ('sv_teamdamage', 'Enable friendly fire', '1'),
    ('sv_powerups', 'Enable powerups (katana)', '1'),
    ('sv_vote_kick', 'Enable kick voting', '1'),
    ('sv_vote_kick_bantime', 'Time in minutes to ban a player if kicked by voting (0 equals only kick)', '5'),
    ('sv_vote_kick_min', 'Minimum number of players required to start a kick vote', '0'),
    ('sv_inactivekick_time', 'Time in minutes after an inactive player will be taken care of', '3'),
    ('sv_inactivekick', 'How to deal with inactive players (0 = move to spectator, 1 = move to free spectator slot/kick, 2 = kick)', '1'),
]
other_settings = [
    ('server_binary', 'Server Binary (empty means use system binary)', ''),
    ('server', 'old server binary', ''),
    ('record_stats', 'Records stats', '1'),
]

def save_conf(request):
    params = request.params
    files = request.files
    if 'server_binary' in files:
        params['server'] = os.path.join(server_folder,
                     files['server_binary'].filename)
        if os.path.exists(params['server']):
            os.remove(params['server'])
        files['server_binary'].save(server_folder)
        os.chmod(params['server'], 755)
    elif params.get('server', ''):
        # don't change the server
        pass
    else:
        params['server'] = ""
        
    name = params['sv_name']
    conf = dict([x for x in params.items()])        
    data = conf_table.find_one({'name': name})
    if data:
        # Config exists
        data['conf'] = conf
    else:
        # New config
        data = {'name': name, 'conf': conf}
    conf_table.save(data)

def delete_conf(id_):
    conf_table.remove(ObjectId(id_))

def export_conf(conf):
    filename = data_folder + '/teeworlds.conf'
    f = open(filename, 'w')
    for setting, value in conf['conf'].items():
        f.write("%s %s\n" % (setting, value))
        
    # export external commands
    result = 0
    # FIXME: FIND EMPTY PORT
    while result == 0:
        s = socket(AF_INET, SOCK_STREAM)
        result = s.connect_ex(('127.0.0.1', ECON_PORT))
        ECON_PORT += 1
    print("CONFIG", ECON_PORT)
    f.write("ec_port %s\n" % ECON_PORT)
    f.write("ec_password teeawards\n")
    f.write("ec_auth_timeout 10\n")
    f.write("ec_bantime 0\n")
    f.close()
    return filename, ECON_PORT

def get_config(name):
    return conf_table.find_one({'name': name})

def get_configs():
    return conf_table.find()


#twms = TeeWorldsServerManager()

