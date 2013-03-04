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


###  EMPTY DB
#pickup_table.drop()
#kill_table.drop()
###

# Prepare serveur
cmd = '/usr/games/teeworlds-server -f /home/titilambert/projets_opensource/teeworlds/tee.cfg'
master, slave = pty.openpty()


# Launch server
p = Popen(cmd, shell=True, stdin=PIPE, stdout=slave, stderr=slave, close_fds=True)
stdout = os.fdopen(master)

while 1:
    line = stdout.readline()
    # Join team:
#    if re.match("\[(.*)\]\[game\]: team_join player='.*:(.*)' team=(.*)", line):
 #       time, player, team = re.match("\[(.*)\]\[game\]: team_join player='.*:(.*)' team=(.*)", line).groups()
#            print "JOIN: ", player, team
#            data = col.find_one({'player' : player})
#            if not data:
#                data = {'player': player, 'kills': {}, 'deaths': {}, 'pickup': {}}
#                col.insert(data)
    # Pickup
    if re.match("\[(.*)\]\[game\]: pickup player='.*:(.*)' item=(.*)$", line):
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


#        else:
    print line
#    print where
