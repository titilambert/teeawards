#!/usr/bin/python
import time
from pymongo import Connection

from subprocess import Popen, PIPE, STDOUT
import pty
import threading
import os
import sys
import re
from datetime import datetime
import select

from libs.lib import conf_table

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
        self.pickup_table = tee_db['pickup']
        self.kill_table = tee_db['kill']
        self.conf = conf

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

    def is_alive(self):
        if not hasattr(self, 'server'):
            return False
        return self.server.is_alive()

    def start(self):
        # Prepare server
        # Server Command
        self.command = '/usr/games/teeworlds-server'
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
        while not self.stopped():
#            print "read"
            ready, _, _ = select.select([self.master], [], [], timeout)
            if not ready:
                continue
            line = os.read(self.master, 512)
            # Join team:
            if re.match("\[(.*)\]\[game\]: team_join player='.*:(.*)' team=(.*)", line):
                time, player, team = re.match("\[(.*)\]\[game\]: team_join player='.*:(.*)' team=(.*)", line).groups()
                print "JOIN: ", player, team
                data = {'datetime': when,  'player': player.strip(), 'team': team.strip()}
                self.manager.join_table.save(data)
            # Change team
            elif re.match("\[(.*)\]\[game\]: team_join player='.*:(.*)' m_Team=(.*)", line):
                time, player, team = re.match("\[(.*)\]\[game\]: team_join player='.*:(.*)' m_Team=(.*)", line).groups()
                print "Change: ", player, team
                data = {'datetime': when,  'player': player.strip(), 'team': team.strip()}
                self.manager.changeteam_table.save(data)
            # Start round
            elif re.match("\[(.*)\]\[game\]: start round type='(.*)' teamplay='([0-9]*)'", line):
                when, gametype, teamplay = re.match("\[(.*)\]\[game\]: start round type='(.*)' teamplay='([0-9]*)'", line).groups()
                print "START ROUND:", gametype, "TEAMPLAY", teamplay
                data = {'datetime': when,  'gametype': gametype.strip(), 'teamplay': teamplay.strip()}
                self.manager.round_table.save(data)
            # Change map
            elif re.match("\[(.*)\]\[datafile\]: loading done. datafile='(.*)'", line):
                when, raw_map = re.match("\[(.*)\]\[datafile\]: loading done. datafile='(.*)'", line).groups()
                map_name = os.path.basename(raw_map)
                print "CHANGE MAP", map_name
                data = {'datetime': when,  'map': map_name.strip()}
                self.manager.kick_table.save(data)
            # Kick
            elif re.match("\[(.*)\]\[chat\]: \*\*\* '(.*)' has left the game \(Kicked for inactivity\)", line):
                when, player = re.match("\[(.*)\]\[chat\]: \*\*\* '(.*)' has left the game \(Kicked for inactivity\)", line).groups()
                print "KICKED", player
                data = {'datetime': when,  'player': player.strip()}
                self.manager.kick_table.save(data)
            # Timeout
            elif re.match("\[(.*)\]\[chat\]: \*\*\* '(.*)' has left the game \(Timeout\)", line):
                when, player = re.match("\[(.*)\]\[chat\]: \*\*\* '(.*)' has left the game \(Timeout\)", line).groups()
                print "TIMEOUT", player
                data = {'datetime': when,  'player': player.strip()}
                self.manager.timeout_table.save(data)
            # Leave game
            elif re.match("\[(.*)\]\[game\]: leave player='[0-9]*:(.*)'", line):
                when, player = re.match("\[(.*)\]\[game\]: leave player='[0-9]*:(.*)'", line).groups()
                print "LEAVE", player
                data = {'datetime': when,  'player': player.strip()}
                self.manager.leave_table.save(data)
            # Pickup
            elif re.match("\[(.*)\]\[game\]: pickup player='.*:(.*)' item=(.*)$", line):
                when, player, item = re.match("\[(.*)\]\[game\]: pickup player='.*:(.*)' item=(.*\/.*)$", line).groups()
                when = datetime.fromtimestamp(int(when, 16))
                print "PICKUP: ", when, player, item
                data = {'datetime': when,  'player': player.strip(), 'item': item.strip()}
                self.manager.pickup_table.save(data)
            # Kill
            elif re.match("\[(.*)\]\[game\]: kill killer='.*:(.*)' victim='.*:(.*)' weapon=(.*) special=(.*)", line):
                when, killer, victim, weapon, special = re.match("\[(.*)\]\[game\]: kill killer='.*:(.*)' victim='.*:(.*)' weapon=(.*) special=(.*)", line).groups()
                when = datetime.fromtimestamp(int(when, 16))
                print when, killer, "KILL", victim, "with", weapon, "and special", special
                data = {'when': when, 'killer': killer.strip(), 'victim': victim.strip(), 'weapon': weapon.strip(), 'special': special.strip()}
                self.manager.kill_table.save(data)
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

def save_conf(params):
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


def export_conf(conf):
    pass

def get_configs():
    return conf_table.find()


twms = TeeWorldsManagerServer()

