#!/usr/bin/python
import time
from pymongo import Connection
from bson.objectid import ObjectId

from subprocess import Popen, PIPE, STDOUT
import pty
import threading
import os
import sys
import re
from datetime import datetime
import select

from libs.lib import conf_table, data_folder
from socket import *

TIMEOUT = 2
PACKET_GETINFO3 = "\xff\xff\xff\xff\xff\xff\xff\xff\xff\xffgie3" + "\x00"

class TeeWorldsManagerServer(object):
    def __init__(self, conf=None):

        # Prepare db
        self.con = Connection()
        tee_db = self.con['teeworlds']
        # Prepare table
        self.join_table = tee_db['join']
        self.changeteam_table = tee_db['changeteam']
        self.round_table = tee_db['round']
        self.map_table = tee_db['map']
        self.kick_table = tee_db['kick']
        self.timeout_table = tee_db['timeout']
        self.leave_table = tee_db['leave']
        self.servershutdown_table = tee_db['servershutdown']
        self.pickup_table = tee_db['pickup']
        self.kill_table = tee_db['kill']
        self.flaggrab_table = tee_db['flaggrab']
        self.flagreturn_table = tee_db['flagreturn']
        self.flagcapture_table = tee_db['flagcapture']
        self.server_executable = None
        self.conf = conf
        self.process = None
        #import pdb;pdb.set_trace()

    def empty_db(self):
        self.join_table.drop()
        self.changeteam_table.drop()
        self.round_table.drop()
        self.map_table.drop()
        self.kick_table.drop()
        self.timeout_table.drop()
        self.leave_table.drop()
        self.pickup_table.drop()
        self.kill_table.drop()
        self.flaggrab_table.drop()
        self.flagreturn_table.drop()
        self.flagcapture_table.drop()

    def is_alive(self):
        if not hasattr(self, 'server'):
            return False
        return self.server.is_alive()

    def get_server_info(self):
        try:
            sock = socket(AF_INET, SOCK_DGRAM)
            sock.settimeout(TIMEOUT);
            sock.sendto(PACKET_GETINFO3, ('localhost',8303))
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

        except: 
            sock.close()
            return None


    def start(self, conf_name):
        self.conf = get_config(conf_name)
        filename = export_conf(self.conf)
        # Prepare server
        ## Prepare storage file
        f = open(os.path.join(data_folder,'storage.cfg'), 'w')
        f.write('add_path .')
        f.close()
        # Server Command
        self.command = 'cd %s && /usr/games/teeworlds-server -f %s' % (data_folder, filename)
        # Open pty
        master, slave = pty.openpty()
        # Launch server
        self.process = Popen(self.command, shell=True, stdin=PIPE, stdout=slave, stderr=slave, close_fds=True)

        # Init thread
        self.server = TeeWorldsServer(self, master)
        # Start Server
        self.server.start()

    def stop(self):
        if self.process:
            # Stop thread
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
            self.process = None
            data = {'when': datetime.now()}
            self.servershutdown_table.save(data)
            return True
        return False

class TeeWorldsServer(threading.Thread):
    def __init__(self, manager, master):
        threading.Thread.__init__(self)
        self.manager = manager

        self.process = manager.process
        self.master = master

        self.stop = threading.Event()

    def stop_server(self):
        self.stop.set()

    def stopped(self):
        return self.stop.isSet()

    def run(self):

        timeout = 2
        round_ = None
        while not self.stopped():
#            print "read"
            ready, _, _ = select.select([self.master], [], [], timeout)
            if not ready:
                continue
            line = os.read(self.master, 512)

            # Join team:
            if re.match("\[(.*)\]\[game\]: team_join player='.*:(.*)' team=(.*)", line):
                when, player, team = re.match("\[(.*)\]\[game\]: team_join player='.*:(.*)' team=(.*)", line).groups()
                print "JOIN: ", player, team
                when = datetime.fromtimestamp(int(when, 16))
                data = {'when': when,  'player': player.strip(), 'team': team.strip(), 'round': round_}
                self.manager.join_table.save(data)
            # Change team
            elif re.match("\[(.*)\]\[game\]: team_join player='.*:(.*)' m_Team=(.*)", line):
                when, player, team = re.match("\[(.*)\]\[game\]: team_join player='.*:(.*)' m_Team=(.*)", line).groups()
                print "Change: ", player, team
                when = datetime.fromtimestamp(int(when, 16))
                data = {'when': when,  'player': player.strip(), 'team': team.strip(), 'round': round_}
                self.manager.changeteam_table.save(data)
            # Start round
            elif re.match("\[(.*)\]\[game\]: start round type='(.*)' teamplay='([0-9]*)'", line):
                when, gametype, teamplay = re.match("\[(.*)\]\[game\]: start round type='(.*)' teamplay='([0-9]*)'", line).groups()
                print "START ROUND:", gametype, "TEAMPLAY", teamplay
                when = datetime.fromtimestamp(int(when, 16))
                data = {'when': when,  'gametype': gametype.strip(), 'teamplay': teamplay.strip()}
                round_ = self.manager.round_table.save(data)
            # Change map
            elif re.match("\[(.*)\]\[datafile\]: loading done. datafile='(.*)'", line):
                when, raw_map = re.match("\[(.*)\]\[datafile\]: loading done. datafile='(.*)'", line).groups()
                when = datetime.fromtimestamp(int(when, 16))
                map_name = os.path.basename(raw_map)
                print "CHANGE MAP", map_name
                data = {'when': when,  'map': map_name.strip()}
                self.manager.kick_table.save(data)
                round_ = None
            # Kick
            elif re.match("\[(.*)\]\[chat\]: \*\*\* '(.*)' has left the game \(Kicked for inactivity\)", line):
                when, player = re.match("\[(.*)\]\[chat\]: \*\*\* '(.*)' has left the game \(Kicked for inactivity\)", line).groups()
                print "KICKED", player
                when = datetime.fromtimestamp(int(when, 16))
                data = {'when': when,  'player': player.strip(), 'round': round_}
                self.manager.kick_table.save(data)
            # Timeout
            elif re.match("\[(.*)\]\[chat\]: \*\*\* '(.*)' has left the game \(Timeout\)", line):
                when, player = re.match("\[(.*)\]\[chat\]: \*\*\* '(.*)' has left the game \(Timeout\)", line).groups()
                print "TIMEOUT", player
                when = datetime.fromtimestamp(int(when, 16))
                data = {'when': when,  'player': player.strip(), 'round': round_}
                self.manager.timeout_table.save(data)
            # Leave game
            elif re.match("\[(.*)\]\[game\]: leave player='[0-9]*:(.*)'", line):
                when, player = re.match("\[(.*)\]\[game\]: leave player='[0-9]*:(.*)'", line).groups()
                print "LEAVE", player
                when = datetime.fromtimestamp(int(when, 16))
                data = {'when': when,  'player': player.strip(), 'round': round_}
                self.manager.leave_table.save(data)
            # Pickup
            elif re.match("\[(.*)\]\[game\]: pickup player='.*:(.*)' item=(.*)$", line):
                when, player, item = re.match("\[(.*)\]\[game\]: pickup player='.*:(.*)' item=(.*\/.*)$", line).groups()
                when = datetime.fromtimestamp(int(when, 16))
                print "PICKUP: ", when, player, item
                data = {'when': when,  'player': player.strip(), 'item': item.strip(), 'round': round_}
                self.manager.pickup_table.save(data)
            # Kill
            elif re.match("\[(.*)\]\[game\]: kill killer='.*:(.*)' victim='.*:(.*)' weapon=(.*) special=(.*)", line):
                when, killer, victim, weapon, special = re.match("\[(.*)\]\[game\]: kill killer='.*:(.*)' victim='.*:(.*)' weapon=(.*) special=(.*)", line).groups()
                when = datetime.fromtimestamp(int(when, 16))
                print when, killer, "KILL", victim, "with", weapon, "and special", special
                data = {'when': when, 'killer': killer.strip(), 'victim': victim.strip(), 'weapon': weapon.strip(), 'special': special.strip(), 'round': round_}
                self.manager.kill_table.save(data)
            # Get Flag
            elif re.match("\[(.*)\]\[game\]: flag_grab player='.*:(.*)'", line):
                when, player = re.match("\[(.*)\]\[game\]: flag_grab player='.*:(.*)'", line).groups()
                when = datetime.fromtimestamp(int(when, 16))
                data = {'when': when, 'player': player, 'round': round_}
                print when, player, "GET FLAG"
                self.manager.flaggrab_table.save(data)
            # Return Flag
            elif re.match("\[(.*)\]\[game\]: flag_return player='.*:(.*)'", line):
                when, player = re.match("\[(.*)\]\[game\]: flag_return player='.*:(.*)'", line).groups()
                when = datetime.fromtimestamp(int(when, 16))
                data = {'when': when, 'player': player, 'round': round_}
                print when, player, "RETURN FLAG"
                self.manager.flagreturn_table.save(data)
            # Capture Flag
            elif re.match("\[(.*)\]\[game\]: flag_capture player='.*:(.*)'", line):
                when, player = re.match("\[(.*)\]\[game\]: flag_capture player='.*:(.*)'", line).groups()
                when = datetime.fromtimestamp(int(when, 16))
                data = {'when': when, 'player': player, 'round': round_}
                print when, player, "CAPTURE FLAG"
                self.manager.flagcapture_table.save(data)
            # Other
            else:
                 print line

engine_settings = [
    ('sv_name', 'Name of the server', 'unnamed server'),
    ('sv_bindaddr', 'Address to bind', ''),
    ('sv_port', 'Port the server will listen on', '8303'),
    ('sv_external_port', 'Port to report to the master servers (e.g. in case of a firewall rename)','0'),
    ('sv_max_clients', 'Number of clients that can be connected to the server at the same time', '12'),
    ('sv_max_clients_per_ip', 'Number of clients with the same ip that can be connected to the server at the same time', '12'),
    ('sv_high_bandwidth', 'Use high bandwidth mode, for LAN servers only', '0'),
    ('sv_register', 'Register on the master servers', '1'),
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
    ('sv_spamprotection', 'Enable spam filter', '1'),
    ('sv_tournament_mode', 'Players will automatically join as spectator', '0'),
    ('sv_respawn_delay_tdm', 'Time in seconds needed to respawn in the tdm gametype', '3'),
    ('sv_teamdamage', 'Enable friendly fire', '0'),
    ('sv_powerups', 'Enable powerups (katana)', '1'),
    ('sv_vote_kick', 'Enable kick voting', '1'),
    ('sv_vote_kick_bantime', 'Time in minutes to ban a player if kicked by voting (0 equals only kick)', '5'),
    ('sv_vote_kick_min', 'Minimum number of players required to start a kick vote', '0'),
    ('sv_inactivekick_time', 'Time in minutes after an inactive player will be taken care of', '3'),
    ('sv_inactivekick', 'How to deal with inactive players (0 = move to spectator, 1 = move to free spectator slot/kick, 2 = kick)', '1'),
]
other_settings = [
    ('server_binary', 'Server Binary (empty means use system binary)', ''),
]

def save_conf(request):
    params = request.params
    files = request.files
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
    filename = '/tmp/teeworlds.conf'
    f = open(filename, 'w')
    for setting, value in conf['conf'].items():
        f.write("%s %s\n" % (setting, value))
        
    f.close()
    return filename

def get_config(name):
    return conf_table.find_one({'name': name})

def get_configs():
    return conf_table.find()


twms = TeeWorldsManagerServer()

