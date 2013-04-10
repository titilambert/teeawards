import os
import sys
import Queue
import copy

from pymongo import Connection

con = Connection()
tee_db = con['teeworlds']
# CONFIG TABLES DONT EMPTY IT !!!
conf_table = tee_db['config']
maps_table = tee_db['maps']

# DATA TABLES
join_table = tee_db['join']
changeteam_table = tee_db['changeteam']
round_table = tee_db['round']
map_table = tee_db['map']
kick_table = tee_db['kick']
timeout_table = tee_db['timeout']
leave_table = tee_db['leave']
pickup_table = tee_db['pickup']
kill_table = tee_db['kill']
flaggrab_table = tee_db['flaggrab']
flagreturn_table = tee_db['flagreturn']
flagcapture_table = tee_db['flagcapture']
servershutdown_table = tee_db['servershutdown']

def empty_db():
    join_table.drop()
    changeteam_table.drop()
    round_table.drop()
    map_table.drop()
    kick_table.drop()
    timeout_table.drop()
    leave_table.drop()
    servershutdown_table.drop()
    pickup_table.drop()
    kill_table.drop()
    flaggrab_table.drop()
    flagreturn_table.drop()
    flagcapture_table.drop()




live_status_queue = Queue.Queue()

# DATA FOLDER (maps, daemon, ...)
data_folder = os.path.join(os.path.dirname(__file__), "..", "server_data")
map_folder = os.path.join(data_folder, 'maps')
demo_folder = os.path.join(data_folder, 'demo')
skin_folder = os.path.join(data_folder, 'skin')
map_screenshot_folder = os.path.join(data_folder, 'map_screenshots')
server_folder = os.path.join(data_folder, 'servers')
folders = [
    data_folder,
    map_folder,
    demo_folder,
    skin_folder,
    map_screenshot_folder,
    server_folder,
]
for folder in folders:
    if not os.path.exists(folder):
        os.makedirs(folder)
    if not os.path.isdir(folder):
        print "ERROR: ", folder," must be a folder and writable"
        sys.exit(1)


#Team score
#+1 for taking the flag from the flag stand 
#+100 for capture 
#Player score
#+1 for taking the flag from the flag stand 
#+1 for returning the flag 
#+1 for fragging the enemy flag carrier 
#+5 for capturing the flag 
#+1 for fragging an enemy 
#-1 for killing a teammate or yourself


#Team
team_mapping = {
    'Spectator': '-1',
    'Red': '0',
    'Blue': 1,
}

# Mapping
pickup_mapping = {
    'heart': '0/0',
    'shield': '1/0',
    'shotgun': '2/2',
    'grenade': '2/3',
    'laser': '2/4',
    'ninja': '3/5',
}

# Kill mapping
kill_mapping = {
    'exit': '-3',
    'death fall': '-1',
    'hammer': '0',
    'gun': '1',
    'shotgun': '2',
    'grenade': '3',
    'laser': '4',
    'ninja': '5',
    }

# Special
special = {
    'normal_death': '0',
    'die_with_flag': '1',
    'your_killer_have_flag': '2',
    'suicide_with_flag': '3',
    }

r_kill_mapping = dict([(x[1], x[0]) for x in kill_mapping.items()])
r_pickup_mapping = dict([(x[1], x[0]) for x in pickup_mapping.items()])


def get_general_players_stats(with_warmup=False):
    def get_stats_by_players(ret, data):
        # warmup
        if (not with_warmup) and data['round'] == None:
            return ret
        # Handle exit
        if data['weapon'] == '-3':
            return ret

        if not data['victim'] in ret:
            ret[data['victim']] = {'kills': 0,
                                   'deaths': 0,
                                   'suicides': 0,
                                  }
        ret[data['victim']]['deaths'] += 1

        if data['killer'] != data['victim']:
            if not data['killer'] in ret:
                ret[data['killer']] = {'kills': 0,
                                       'deaths': 0,
                                       'suicides': 0,
                                      }
            ret[data['killer']]['kills'] += 1

        if data['killer'] == data['victim']:
            if not data['killer'] in ret:
                ret[data['killer']] = {'kills': 0,
                                       'deaths': 0,
                                       'suicides': 0,
                                      }
            ret[data['killer']]['suicides'] += 1

        return ret

    raw_data = kill_table.find()
    return reduce(get_stats_by_players, raw_data, {})


def get_item_stats(item, with_warmup=False):
    kill_with_key = 'kill with ' + item.capitalize()
    dead_by_key = 'dead by ' + item.capitalize()
    def compute_weapon_stats(ret, data):
        # warmup
        if (not with_warmup) and data['round'] == None:
            return ret

        if not data['killer'] in ret[kill_with_key]:
            ret[kill_with_key][data['killer']] = 0
        ret[kill_with_key][data['killer']] += 1
        if not data['victim'] in ret[dead_by_key]:
            ret[dead_by_key][data['victim']] = 0
        ret[dead_by_key][data['victim']] += 1
        return ret

    def compute_item_stats(ret, data):
        # warmup
        if (not with_warmup) and data['round'] == None:
            return ret

        if not data['player'] in ret:
            ret[data['player']] = 0
        ret[data['player']] += 1
        return ret

    item = item.lower()

    stats = {}
    if item in kill_mapping:
        kitem = kill_mapping[item]
        kraw_data = kill_table.find({'weapon' : kitem})
        stats = reduce(compute_weapon_stats,
                       kraw_data,
                       {kill_with_key: {}, dead_by_key: {}})
    if item in pickup_mapping:
        pitem = pickup_mapping[item]
        praw_data = pickup_table.find({'item': pitem})
        pstats = reduce(compute_item_stats, praw_data, {})
        stats.update({'pick up': pstats})


    return stats

def get_player_list():
    player_list = set([x['player'] for x in pickup_table.find(fields=['player'])])
    return player_list

def get_player_stats(player, with_warmup=False):
    def compute_item_stats(ret, data):
        # warmup
        if (not with_warmup) and data['round'] == None:
            return ret

        key = r_pickup_mapping[data['item']]
        if not key in ret:
            ret[key] = 0
        ret[key] += 1
        return ret

    def compute_kill_stats(ret, data):
        # warmup
        if (not with_warmup) and data['round'] == None:
            return ret

        weapon_key = r_kill_mapping[data['weapon']]
        victim_key = data['victim']
        if data['weapon'] == '-3':
            # Handle exit
            return ret
        if data['killer'] != data['victim']:
            if not weapon_key in ret['weapon']:
                ret['weapon'][weapon_key] = 0
            ret['weapon'][weapon_key] += 1
            if not victim_key in ret['victim']:
                ret['victim'][victim_key] = 0
            ret['victim'][victim_key] += 1
        return ret
        
    def compute_victim_stats(ret, data):
        # warmup
        if (not with_warmup) and data['round'] == None:
            return ret

        weapon_key = r_kill_mapping[data['weapon']]
        killer_key = data['killer']

        if data['weapon'] == '-3':
            # Handle exit
            return ret
        if data['killer'] != data['victim']:
            if not weapon_key in ret['weapon']:
                ret['weapon'][weapon_key] = 0
            ret['weapon'][weapon_key] += 1
            if not killer_key in ret['killer'] :
                ret['killer'] [killer_key] = 0
            ret['killer'] [killer_key] += 1
        else:
            ret['suicide'] += 1
            if weapon_key == 'death fall':
                if not weapon_key in ret['weapon']:
                    ret['weapon'][weapon_key] = 0
                ret['weapon'][weapon_key] += 1

        return ret

    raw_killer_stats = kill_table.find({'killer' : player})
    kstats = reduce(compute_kill_stats, raw_killer_stats, {'weapon': {}, 'victim': {}})
    raw_victim_stats = kill_table.find({'victim' : player})
    vstats = reduce(compute_victim_stats, raw_victim_stats, {'weapon': {}, 'killer': {}, 'suicide': 0})
    raw_pickup_stats = pickup_table.find({'player' : player})
    pstats = reduce(compute_item_stats, raw_pickup_stats, {})

    return kstats, vstats, pstats


# NEED REFACTORING !!!=
# +1 : kill
# -1 : autokill

# -1 : last player IAR
# playernumbers*2 : first IAR
# playernumbers : second IAR
# playernumbers/2 or 1 : third IAR
#######
# -1 : team kill
def get_player_score(player, data=None):
    if data is None:
        data = {}
        data['kstats'], data['vstats'], data['pstats'] = get_player_stats(player)
    if 'kills' in data:
        kills = data['kills']
    else:
        kills = sum(data['kstats']['victim'].values())
    if 'suicides' in data:
        suicides = data['suicides']
    else:
        suicides = data['vstats']['suicide']

    score = kills - suicides

    return score



def get_stats(player):
    def reducer(ret, data):
        ret, type_ = ret  
        data['type'] = type_
        if type_ == 'round':
            # ROUND start
            if not data['_id'] in ret:
                ret[data['_id']] = []
            ret[data['_id']].append(data)
            ret[data['_id']].sort(key=lambda x: x['when'])
        else:   
            if 'round' in data and not data['round'] is None:
                if not data['round'] in ret:
                    ret[data['round']] = []
                ret[data['round']].append(data)
                ret[data['round']].sort(key=lambda x: x['when'])
        return ret, type_
    # Sort all events by rounds
    # TODO MAKE mongo filters ('round' != NONE)
    events_by_round, _ = reduce(reducer, kill_table.find(), ({}, 'kill'))
    events_by_round, _ = reduce(reducer, join_table.find(), (events_by_round, 'join'))
    events_by_round, _ = reduce(reducer, changeteam_table.find(), (events_by_round, 'changeteam'))
    events_by_round, _ = reduce(reducer, round_table.find(), (events_by_round, 'round'))
    events_by_round, _ = reduce(reducer, kick_table.find(), (events_by_round, 'kick'))
    events_by_round, _ = reduce(reducer, timeout_table.find(), (events_by_round, 'timeout'))
    events_by_round, _ = reduce(reducer, leave_table.find(), (events_by_round, 'leave'))
    events_by_round, _ = reduce(reducer, servershutdown_table.find(), (events_by_round, 'servershutdown'))

    def join_none_reducer(ret, data):
        data['type'] = 'join'
        if 'map' in data and data['round'] is None:
            if not data['map'] in ret:
                ret[data['map']] = []
            ret[data['map']].append(data)
            ret[data['map']].sort(key=lambda x: x['when'])
        return ret
    # Sort event by warmups
    # TODO MAKE mongo filters ('round' == NONE)
    join_by_map = reduce(join_none_reducer, join_table.find(), {})
    # TODO with kick, timeout, leave and server shutdown

    def round_reducer(ret, data):
        if not data['map'] in ret:
            ret[data['map']] = []
        ret[data['map']].append(data)
        return ret
    # Sort rounds by map
    rounds = reduce(round_reducer, round_table.find(), {})

    # Prepare maps to get map name
    maps = dict([(x['_id'], x) for x in map_table.find()])

    # Get STATS !!!!
    results = {} 
    for map_, round_in_a_map in rounds.items():
        # SET INITIAL DATA
        live_data = {}
        live_data['map'] = maps[map_]
        current_map = maps[map_]['map']
        live_data['players'] = {}
        live_data['rounds'] = {}
        # GET JOINs DURING WARMUP or at start
        for join in join_by_map.get(map_, []):
            player_name = join['player']
            current_team = join['team']
            live_data['players'][player_name] = {} 
            live_data['players'][player_name]['team'] = current_team
            live_data['players'][player_name]['score'] = 0
            live_data['players'][player_name]['status'] = 'online'
            # prepare final results
            if not player_name in results:
                # if its a total new player
                results[player_name] = {}
                results[player_name]['score'] = 0
                results[player_name]['kills'] = {}
                results[player_name]['victims'] = {}
                results[player_name]['suicides'] = 0
                results[player_name]['teamkills'] = {}
                results[player_name]['teamvictims'] = {}
                results[player_name]['warmup'] = 0
                results[player_name]['gametype'] = {}
                results[player_name]['team'] = {}
                results[player_name]['maps'] = {}
            # +1 for this map
            if not current_map in results[player_name]['maps']:
                results[player_name]['maps'][current_map] = 0
            results[player_name]['maps'][current_map] += 1
            # +1 for this team
            if not current_team in results[player_name]:
                results[player_name]['team'][current_team] = 0
            results[player_name]['team'][current_team] += 1
            # +1 for warmup
            if not 'warmup' in results[player_name]:
                results[player_name]['warmup'] = 0
            results[player_name]['warmup'] += 1
        # Iter on rounds in a map
        for round_id, round_ in enumerate(round_in_a_map):
            ### NEW ROUND ###
            live_data['rounds'][round_id] = {}
            # which game type : DM, TDM, CTF, ...
            live_data['rounds'][round_id]['gametype'] = round_['gametype']
            # Is it a team game ?
            current_teamplay = bool(int(round_['teamplay']))
            # Set players A round start
            if round_id == 0:
                # First round on the map
                # Copy data from warmup
                live_data['rounds'][round_id]['players'] = copy.copy(live_data['players'])
                for player_name, player in live_data['rounds'][round_id]['players'].items():
                    # +1 for this game type
                    if not round_['gametype'] in results[player_name]['gametype']:
                        results[player_name]['gametype'][round_['gametype']] = 0
                    results[player_name]['gametype'][round_['gametype']] += 1
            else:
                # Not first round on the map
                live_data['rounds'][round_id]['players'] = {}
                # For each player from the previous round
                for player_name, player in live_data['rounds'][round_id - 1]['players'].items():
                    # Get only which are still online !
                    if player['status'] == 'online':
                        # Copy data from last round
                        live_data['rounds'][round_id]['players'][player_name] = copy.copy(player)
                        # Reset score
                        live_data['rounds'][round_id]['players'][player_name]['score'] = 0
                        # +1 for this maps
                        if not current_map in results[player_name]['maps']:
                            results[player_name]['maps'][current_map] = 0
                        results[player_name]['maps'][current_map] += 1
                        # +1 for this game type
                        if not round_['gametype'] in results[player_name]['gametype']:
                            results[player_name]['gametype'][round_['gametype']] = 0
                        results[player_name]['gametype'][round_['gametype']] += 1
                        # +1 for this team
                        current_team = live_data['rounds'][round_id]['players'][player_name]['team']
                        if not current_team in results[player_name]['team']:
                            results[player_name]['team'][current_team] = 0
                        results[player_name]['team'][current_team] += 1
            # Check if there are any events in a round
            if not round_['_id'] in events_by_round:
                print "NOTFOUND !!!!!!!!!!!!", round_['_id']
#                import pdb;pdb.set_trace()
                # POSSIBLE ?????
                continue
            # Iter on events in a round
            for event in events_by_round[round_['_id']]:
                # Some tee join the game
                if event['type'] == 'join':
                    # Set is 
                    new_player_name = event['player']
                    current_team = event['team']
                    # If not a new player in this round, we NOT reset its score ... :)
                    if not new_player_name in live_data['rounds'][round_id]['players']:
                        live_data['rounds'][round_id]['players'][new_player_name] = {}
                        live_data['rounds'][round_id]['players'][new_player_name]['team'] = current_team
                        live_data['rounds'][round_id]['players'][new_player_name]['score'] = 0
                        live_data['rounds'][round_id]['players'][new_player_name]['status'] = 'online'
                        if not player_name in results:
                            # if its a total new player
                            results[new_player_name] = {}
                            results[new_player_name]['score'] = 0
                            results[new_player_name]['kills'] = {}
                            results[new_player_name]['victims'] = {}
                            results[new_player_name]['suicides'] = 0
                            results[new_player_name]['teamkills'] = {}
                            results[new_player_name]['teamvictims'] = {}
                            results[new_player_name]['gametype'] = {}
                            results[new_player_name]['team'] = {}
                            results[new_player_name]['maps'] = {}
                        # +1 for this maps
                        if not current_map in results[new_player_name]['maps']:
                            results[new_player_name]['maps'][current_map] = 0
                        results[new_player_name]['maps'][current_map] += 1
                        # +1 for this team
                        if not current_team in results[new_player_name]:
                            results[new_player_name]['team'][current_team] = 0
                        results[new_player_name]['team'][current_team] += 1
                        # +1 for this game type
                        if not round_['gametype'] in results[new_player_name]['gametype']:
                            results[new_player_name]['gametype'][round_['gametype']] = 0
                        results[new_player_name]['gametype'][round_['gametype']] += 1
                # A tee kills a tee
                elif event['type'] == 'kill':
                    weapon = event['weapon']
                    # Exit kill ... just pass
                    if event['weapon'] == -3:
                        continue
                    # OK, this is a real kill
                    killer = event['killer']
                    victim = event['victim']
                    killer_team = live_data['rounds'][round_id]['players'][killer]['team']
                    victim_team = live_data['rounds'][round_id]['players'][victim]['team']
                    # Is it Auto kill ?
                    if killer == victim:
                        live_data['rounds'][round_id]['players'][killer]['score'] -= 1
                        results[killer]['score'] -= 1
                        results[killer]['suicides'] += 1
                    # Is it Team kill ?
                    elif current_teamplay and killer_team == victim_team:
                        # +1 team kill for the killer
                        if not victim in results[killer]['teamkills']:
                            results[killer]['teamkills'][victim] = 0
                        results[killer]['teamkills'][victim] += 1
                        # +1 team victim(death) for the victim
                        if not killer in results[victim]['teamvictims']:
                            results[victim]['teamvictims'][killer] = 0
                        results[victim]['teamvictims'][killer] += 1
                        # -1 score ...
                        live_data['rounds'][round_id]['players'][killer]['score'] -= 1
                        results[killer]['score'] -= 1
                    else:
                        # Normal kill
                        # +1 kill for the killer
                        if not victim in results[killer]['kills']:
                            results[killer]['kills'][victim] = 0
                        results[killer]['kills'][victim] += 1
                        # +1 victim(death) for the victim
                        if not killer in results[victim]['victims']:
                            results[victim]['victims'][killer] = 0
                        results[victim]['victims'][killer] += 1
                        # +1 score ...
                        live_data['rounds'][round_id]['players'][killer]['score'] += 1
                        results[killer]['score'] += 1

                elif event['type'] == 'changeteam':
                    #import pdb;pdb.set_trace()
                    # TODO handle this
                    print event
                elif event['type'] == 'kick':
                    live_data['rounds'][round_id]['players'][event['player']]['status'] = 'kicked'
                    # TODO add this in stats
                elif event['type'] == 'timeout':
                    live_data['rounds'][round_id]['players'][event['player']]['status'] = 'timeout'
                    # TODO add this in stats
                elif event['type'] == 'leave':
                    live_data['rounds'][round_id]['players'][event['player']]['status'] = 'left'
                    # TODO add this in stats
                elif event['type'] == 'servershutdown':
                    for p in live_data['rounds'][round_id]['players'].values():
                        p['status'] = 'servershutdown'
                        # TODO add this in stats
                    # END OF ROUND
                    break

            # ADD round points
            nb_players = len(live_data['rounds'][round_id]['players'])
            # GET ONLINE PLAYERS ROUND CLASSEMENT
#            online_classement = sorted([(k, v) for k, v in live_data['rounds'][round_id]['players'].items() if v['status'] == 'online'], key=lambda x: x[1]['score'], reverse=True)
            # GET PLAYERS ROUND CLASSEMENT
            classement = sorted([(k, v) for k, v in live_data['rounds'][round_id]['players'].items()], key=lambda x: x[1]['score'], reverse=True)
            if nb_players <= 1:
                # One player or less
                # Do thing
                pass
            else:
                # Two players or more
                first_player = classement[0][0]
                ## First
                if not 'first_place' in results[first_player]:
                    results[first_player]['first_place'] = 0
                results[first_player]['first_place'] += 1
                results[first_player]['score'] += nb_players * 2
                ## Last on for online player
                last_player = classement[-1][0]
                if not 'last_place' in results[last_player]:
                    results[last_player]['last_place'] = 0
                results[last_player]['last_place'] += 1
                results[last_player]['score'] -= 1
                if nb_players >= 3:
                    # Three players or more
                    ## Second
                    second_player = classement[1][0]
                    if not 'second_place' in results[last_player]:
                        results[last_player]['second_place'] = 0
                    results[last_player]['second_place'] += 1
                    results[last_player]['score'] += nb_players
                if nb_players >= 4:
                    # Four players or more
                    ## Third
                    third_player = classement[2][0]
                    if not 'third_place' in results[last_player]:
                        results[last_player]['third_place'] = 0
                    results[last_player]['third_place'] += 1
                    results[last_player]['score'] += nb_players / 2

    return results

def toto():
    # ##
    data_tables =[
    join_table,
    changeteam_table,
    kick_table,
    timeout_table,
    leave_table,
#    servershutdown_table,
    pickup_table,
    kill_table,
    flaggrab_table,
    flagreturn_table,
    flagcapture_table,
    ]

    for t in data_tables:
        datas = [x for x in t.find()]
        rounds = [x for x in round_table.find()]
        #maps = [x for x in map_table.find()]
        events = sorted(rounds + datas, key=lambda x: x['when'])
        map_id = None

        for event in events:
            if 'map' in event:
                map_id = event['map']
                round_id = event['_id']
            elif map_id:
                event['map'] = map_id
                event['round'] = round_id
  #              print event
#                t.save(event)
            else:
                print "DELETE", event
#                t.remove(event)













### MAYBE USELESS
def get_players_kills(ret, data):
    if data['killer'] != data['victim']:
        if not data['killer'] in ret:
            ret[data['killer']] = 0
        ret[data['killer']] += 1
    return ret


def get_players_victims(ret, data):
    if not data['victim'] in ret:
        ret[data['victim']] = 0
    ret[data['victim']] += 1
    return ret
