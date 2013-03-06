#!/usr/bin/python
import time
from pymongo import Connection

from subprocess import Popen, PIPE, STDOUT
import pty
import os
import sys
import re
from datetime import datetime

# Prepare db
con = Connection()
tee_db = con['teeworlds']
pickup_table = tee_db['pickup']
kill_table = tee_db['kill']
join_table = tee_db['join']
change_team_table = tee_db['changeteam']
round_table = tee_db['round']
kick_table = tee_db['kick']
timeout_table = tee_db['timeout']
leave_table = tee_db['leave']


###  EMPTY DB
#pickup_table.drop()
#kill_table.drop()
###

# Prepare serveur
#cmd = '/usr/games/teeworlds-server -f /home/titilambert/projets_opensource/teeworlds/tee.cfg'
cmd = '/usr/games/teeworlds-server ' + " ".join(sys.argv[1:])
master, slave = pty.openpty()


# Launch server
p = Popen(cmd, shell=True, stdin=PIPE, stdout=slave, stderr=slave, close_fds=True)
stdout = os.fdopen(master)


# TEAMS
#-1 spectator
# 0 Red
# 1 Blue

while 1:
    line = stdout.readline()
    # Join team:
    if re.match("\[(.*)\]\[game\]: team_join player='.*:(.*)' team=(.*)", line):
        time, player, team = re.match("\[(.*)\]\[game\]: team_join player='.*:(.*)' team=(.*)", line).groups()
        print "JOIN: ", player, team
#            data = col.find_one({'player' : player})
#            if not data:
#                data = {'player': player, 'kills': {}, 'deaths': {}, 'pickup': {}}
#                col.insert(data)
    # Change team
    elif re.match("\[(.*)\]\[game\]: team_join player='.*:(.*)' m_Team=(.*)", line):
       time, player, team = re.match("\[(.*)\]\[game\]: team_join player='.*:(.*)' m_Team=(.*)", line).groups()
       print "Change: ", player, team
    # Start round
    elif re.match("\[(.*)\]\[game\]: start round type='(.*)' teamplay='([0-9]*)'", line):
	when, gametype, teamplay = re.match("\[(.*)\]\[game\]: start round type='(.*)' teamplay='([0-9]*)'", line).groups()
	print "START ROUND:", gametype, "TEAMPLAY", teamplay
    # Change map
    elif re.match("\[(.*)\]\[datafile\]: loading done. datafile='(.*)'", line):
	when, raw_map = re.match("\[(.*)\]\[datafile\]: loading done. datafile='(.*)'", line).groups()
	map_name = os.path.basename(raw_map)
    # Kick
    elif re.match("\[(.*)\]\[chat\]: \*\*\* '(.*)' has left the game \(Kicked for inactivity\)", line):
        when, player = re.match("\[(.*)\]\[chat\]: \*\*\* '(.*)' has left the game \(Kicked for inactivity\)", line).groups()
        print "KICKED", player
    # Timeout
    elif re.match("\[(.*)\]\[chat\]: \*\*\* '(.*)' has left the game \(Timeout\)", line):
        when, player = re.match("\[(.*)\]\[chat\]: \*\*\* '(.*)' has left the game \(Timeout\)", line).groups()
        print "TIMEOUT", player
    # Leave game
    elif re.match("\[(.*)\]\[game\]: leave player='[0-9]*:(.*)'", line):
        when, player = re.match("\[(.*)\]\[game\]: leave player='[0-9]*:(.*)'", line).groups()
        print "LEAVE", player
    # Pickup
    elif re.match("\[(.*)\]\[game\]: pickup player='.*:(.*)' item=(.*)$", line):
        when, player, item = re.match("\[(.*)\]\[game\]: pickup player='.*:(.*)' item=(.*\/.*)$", line).groups()
        when = datetime.fromtimestamp(int(when, 16))
        print "PICKUP: ", when, player, item
        data = {'datetime': when,  'player': player.strip(), 'item': item.strip()}
        pickup_table.save(data)
#            for x in pickup_table.find():
#                print x
    # Kill
    elif re.match("\[(.*)\]\[game\]: kill killer='.*:(.*)' victim='.*:(.*)' weapon=(.*) special=(.*)", line):
        when, killer, victim, weapon, special = re.match("\[(.*)\]\[game\]: kill killer='.*:(.*)' victim='.*:(.*)' weapon=(.*) special=(.*)", line).groups()
        when = datetime.fromtimestamp(int(when, 16))
        print when, killer, "KILL", victim, "with", weapon, "and special", special
        data = {'when': when, 'killer': killer.strip(), 'victim': victim.strip(), 'weapon': weapon.strip(), 'special': special.strip()}
        kill_table.save(data)
#            for x in kill_table.find():
#                print x

    else:
#        else:
         print line
#    print where
