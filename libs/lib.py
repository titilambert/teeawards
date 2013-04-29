import os
import sys
import Queue
import copy

from pymongo import Connection

con = Connection()
tee_db = con['teeworlds']


# Queues
## live stats
live_stats_queue = Queue.Queue()
econ_command_queue = Queue.Queue()

# CONFIG TABLES DONT EMPTY IT !!!
no_stats_tables = []
conf_table = tee_db['config']
no_stats_tables.append(conf_table)
maps_table = tee_db['maps']
no_stats_tables.append(maps_table)

# DATA TABLES
tables = []
join_table = tee_db['join']
tables.append(join_table)
changeteam_table = tee_db['changeteam']
tables.append(changeteam_table)
changename_table = tee_db['changename']
tables.append(changename_table)
round_table = tee_db['round']
tables.append(round_table)
map_table = tee_db['map']
tables.append(map_table)
kick_table = tee_db['kick']
tables.append(kick_table)
timeout_table = tee_db['timeout']
tables.append(timeout_table)
leave_table = tee_db['leave']
tables.append(leave_table)
pickup_table = tee_db['pickup']
tables.append(pickup_table)
kill_table = tee_db['kill']
tables.append(kill_table)
flaggrab_table = tee_db['flaggrab']
tables.append(flaggrab_table)
flagreturn_table = tee_db['flagreturn']
tables.append(flagreturn_table)
flagcapture_table = tee_db['flagcapture']
tables.append(flagcapture_table)
servershutdown_table = tee_db['servershutdown']
tables.append(servershutdown_table)


# Empty log tables to reset stats
def empty_db():
    join_table.drop()
    changeteam_table.drop()
    changename_table.drop()
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
    # TODO: FIND KILLED WITH FLAG BY FLAG ?????
    }

r_kill_mapping = dict([(x[1], x[0]) for x in kill_mapping.items()])
r_pickup_mapping = dict([(x[1], x[0]) for x in pickup_mapping.items()])


def get_player_list():
    player_list = set([x['player'] for x in pickup_table.find(fields=['player'])])
    return player_list


# Get stats and score
# +1 : kill
# -1 : autokill

# -1 : last player IAR
# playernumbers*2 : first IAR
# playernumbers : second IAR
# playernumbers/2 or 1 : third IAR
# -1 : team kill

# +1 : Grab flag
# +1 : Return flag
# +5 : Capture flag
def get_stats(selected_player=None, selected_gametype=None):
    # Sort all events by rounds
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
    # TODO MAKE mongo filters ('round' != NONE) and selected_gametype
    events_by_round, _ = reduce(reducer, kill_table.find(), ({}, 'kill'))
    events_by_round, _ = reduce(reducer, flaggrab_table.find(), (events_by_round, 'flaggrab'))
    events_by_round, _ = reduce(reducer, flagreturn_table.find(), (events_by_round, 'flagreturn'))
    events_by_round, _ = reduce(reducer, flagcapture_table.find(), (events_by_round, 'flagcapture'))
    events_by_round, _ = reduce(reducer, join_table.find(), (events_by_round, 'join'))
    events_by_round, _ = reduce(reducer, changeteam_table.find(), (events_by_round, 'changeteam'))
    events_by_round, _ = reduce(reducer, round_table.find(), (events_by_round, 'round'))
    events_by_round, _ = reduce(reducer, kick_table.find(), (events_by_round, 'kick'))
    events_by_round, _ = reduce(reducer, timeout_table.find(), (events_by_round, 'timeout'))
    events_by_round, _ = reduce(reducer, leave_table.find(), (events_by_round, 'leave'))
    events_by_round, _ = reduce(reducer, servershutdown_table.find(), (events_by_round, 'servershutdown'))

    # Sort event by warmups
    def none_reducer(ret, data):
        ret, type_ = ret
        data['type'] = type_
        if 'map' in data and data['round'] is None:
            if not data['map'] in ret:
                ret[data['map']] = []
            ret[data['map']].append(data)
            ret[data['map']].sort(key=lambda x: x['when'])
        return ret, type_
    # TODO MAKE mongo filters ('round' == NONE) and selected_gametype
    none_event_by_map, _ = reduce(none_reducer, join_table.find(), ({}, 'join'))
    none_event_by_map, _ = reduce(none_reducer, kick_table.find(), (none_event_by_map, 'kick'))
    none_event_by_map, _ = reduce(none_reducer, timeout_table.find(), (none_event_by_map, 'timeout'))
    none_event_by_map, _ = reduce(none_reducer, leave_table.find(), (none_event_by_map, 'leave'))
    none_event_by_map, _ = reduce(none_reducer, servershutdown_table.find(), (none_event_by_map, 'servershutdown'))

    # Sort rounds by map
    def round_reducer(ret, data):
        if not data['map'] in ret:
            ret[data['map']] = []
        if selected_gametype:
            if data['gametype'].upper() == selected_gametype.upper():
                ret[data['map']].append(data)
        else:
            ret[data['map']].append(data)
        return ret
    # TODO MAKE mongo filters ('round' == NONE) and selected_gametype
    rounds = reduce(round_reducer, round_table.find(), {})

    # Prepare maps to get map name
    maps = dict([(x['_id'], x) for x in map_table.find()])


    def new_player_join_a_new_round(player, team, current_map, live_data, results, round_id=None):
        if not round_id is None:
            if not new_player_name in live_data['rounds'][round_id]['players']:
                live_data['rounds'][round_id]['players'][new_player_name] = {}
                live_data['rounds'][round_id]['players'][new_player_name]['team'] = current_team
                live_data['rounds'][round_id]['players'][new_player_name]['score'] = 0
                live_data['rounds'][round_id]['players'][new_player_name]['status'] = 'online'
                live_data['rounds'][round_id]['players'][new_player_name]['kills'] = 0
                live_data['rounds'][round_id]['players'][new_player_name]['deaths'] = 0
                if not new_player_name in results:
                    # if its a total new player
                    results[new_player_name] = {}
                    results[new_player_name]['score'] = 0
                    results[new_player_name]['kills'] = {}
                    results[new_player_name]['deaths'] = 0
                    results[new_player_name]['victims'] = {}
                    results[new_player_name]['suicides'] = 0
                    results[new_player_name]['teamkills'] = {}
                    results[new_player_name]['teamvictims'] = {}
                    results[new_player_name]['gametype'] = {}
                    results[new_player_name]['team'] = {}
                    results[new_player_name]['maps'] = {}
                    results[new_player_name]['rounds'] = 0
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
                # Count round played
                if not 'rounds' in results[new_player_name]:
                    results[new_player_name]['rounds'] = 0
                results[new_player_name]['rounds'] += 1
            else:
                # this is not a real new player, he left then he came back ...
                # We just need to change his status
                live_data['rounds'][round_id]['players'][new_player_name]['status'] = 'online'
        else:
            live_data['players'][player_name] = {} 
            live_data['players'][player_name]['team'] = current_team
            live_data['players'][player_name]['score'] = 0
            live_data['players'][player_name]['status'] = 'online'
            live_data['players'][player_name]['kills'] = 0
            live_data['players'][player_name]['deaths'] = 0
            # prepare final results
            if not player_name in results:
                # if its a total new player
                results[player_name] = {}
                results[player_name]['score'] = 0
                results[player_name]['kills'] = {}
                results[player_name]['deaths'] = 0
                results[player_name]['victims'] = {}
                results[player_name]['suicides'] = 0
                results[player_name]['teamkills'] = {}
                results[player_name]['teamvictims'] = {}
                results[player_name]['warmup'] = 0
                results[player_name]['gametype'] = {}
                results[player_name]['team'] = {}
                results[player_name]['maps'] = {}
                results[player_name]['rounds'] = 0
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

        return live_data, results


    # Get STATS !!!!
    results = {} 
    for map_, round_in_a_map in rounds.items():
        # SET INITIAL DATA
        live_data = {}
        live_data['map'] = maps[map_]
        current_map = maps[map_]['map']
        live_data['players'] = {}
        live_data['rounds'] = {}
        # EVENTS DURING WARMUP
        for event in none_event_by_map.get(map_, []):
            # GET JOINS
            if event['type'] == 'join':
                player_name = event['player']
                current_team = event['team']
                live_data, results = new_player_join_a_new_round(player_name, current_team, current_map, live_data, results)
            elif event['type'] in ['leave', 'timeout', 'kick']:
                player_name = event['player']
                del(live_data['players'][player_name])
            elif event['type'] == 'servershutdown':
                # DO NOTHING ????
                break

        ### NEW MAP ###
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
                    # Count round played
                    if not 'rounds' in results[player_name]:
                        results[player_name]['rounds'] = 0
                    results[player_name]['rounds'] += 1
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
                        # Count round played
                        if not 'rounds' in results[player_name]:
                            results[player_name]['rounds'] = 0
                        results[player_name]['rounds'] += 1
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

################# SECURITY LINES, USELESS (I HOPE) ###############
#                if 'player' in event:
#                    new_player_name = event['player']
#                    if not new_player_name in live_data['rounds'][round_id]['players']:
#                        current_team = event['team']
#                        live_data, results = new_player_join_a_new_round(new_player_name, current_team, current_map, live_data, results, round_id)
#                elif 'killer' in event:
#                    killer = event['killer']
#                    victim = event['victim']
#                    if not killer in live_data['rounds'][round_id]['players']:
#                        current_team = event['team'] # I don't I have this ...
#                        live_data, results = new_player_join_a_new_round(killer, current_team, current_map, live_data, results, round_id)
#                    if not victim in live_data['rounds'][round_id]['players']:
#                        current_team = event['team'] # I don't I have this ...
#                        live_data, results = new_player_join_a_new_round(victim, current_team, current_map, live_data, results, round_id)
################# SECURITY LINES, USELESS (I HOPE) ###############

                # Some tee join the game
                if event['type'] == 'join':
                    # Set is 
                    new_player_name = event['player']
                    current_team = event['team']
                    # If not a new player in this round, we NOT reset its score ... :)
                    live_data, results = new_player_join_a_new_round(new_player_name, current_team, current_map, live_data, results, round_id)

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
                        if not 'deaths' in results[killer]:
                            results[killer]['deaths'] = 0
                        results[killer]['deaths'] += 1
                        live_data['rounds'][round_id]['players'][killer]['deaths'] += 1
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
                        if not 'deaths' in results[victim]:
                            results[victim]['deaths'] = 0
                        results[victim]['deaths'] += 1
                        live_data['rounds'][round_id]['players'][victim]['deaths'] += 1
                    else:
                        # Normal kill
                        # +1 kill for the killer
                        if not victim in results[killer]['kills']:
                            results[killer]['kills'][victim] = 0
                        results[killer]['kills'][victim] += 1
                        live_data['rounds'][round_id]['players'][killer]['kills'] += 1
                        live_data['rounds'][round_id]['players'][victim]['deaths'] += 1
                        # +1 victim(death) for the victim
                        if not killer in results[victim]['victims']:
                            results[victim]['victims'][killer] = 0
                        results[victim]['victims'][killer] += 1
                        # +1 score ...
                        live_data['rounds'][round_id]['players'][killer]['score'] += 1
                        results[killer]['score'] += 1
                        if not 'deaths' in results[victim]:
                            results[victim]['deaths'] = 0
                        results[victim]['deaths'] += 1
                elif event['type'] == 'flaggrab':
                    player_name = event['player']
                    if not 'flaggrab' in live_data['rounds'][round_id]['players'][player_name]:
                        live_data['rounds'][round_id]['players'][player_name]['flaggrab'] = 0
                    live_data['rounds'][round_id]['players'][player_name]['flaggrab'] += 1
                    if not 'flaggrab' in results[player_name]:
                        results[player_name]['flaggrab'] = 0
                    results[player_name]['flaggrab'] += 1
                    results[player_name]['score'] += 1
                elif event['type'] == 'flagreturn':
                    player_name = event['player']
                    if not 'flagreturn' in live_data['rounds'][round_id]['players'][player_name]:
                        live_data['rounds'][round_id]['players'][player_name]['flagreturn'] = 0
                    live_data['rounds'][round_id]['players'][player_name]['flagreturn'] += 1
                    if not 'flagreturn' in results[player_name]:
                        results[player_name]['flagreturn'] = 0
                    results[player_name]['flagreturn'] += 1
                    results[player_name]['score'] += 1
                elif event['type'] == 'flagcapture':
                    player_name = event['player']
                    if not 'flagcapture' in live_data['rounds'][round_id]['players'][player_name]:
                        live_data['rounds'][round_id]['players'][player_name]['flagcapture'] = 0
                    live_data['rounds'][round_id]['players'][player_name]['flagcapture'] += 1
                    if not 'flagcapture' in results[player_name]:
                        results[player_name]['flagcapture'] = 0
                    results[player_name]['flagcapture'] += 1
                    results[player_name]['score'] += 5
                elif event['type'] == 'changeteam':
                    #import pdb;pdb.set_trace()
                    # TODO handle this
                    print "changeteam", event
                    pass
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

            # MEDALS TODO must be in achievements ...
            for player_name, player in live_data['rounds'][round_id]['players'].items():
                # purple
                if player['deaths'] != 0:
                    ratio = player['kills'] / float(player['deaths'])
                    if ratio <= 0.2:
                        if not'purple' in results[player_name]:
                            results[player_name]['purple'] = 0
                        results[player_name]['purple'] += 1
                # no death
                if player['deaths'] == 0:
                    if not'no death' in results[player_name]:
                        results[player_name]['no death'] = 0
                    results[player_name]['no death'] += 1

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
                    if not 'second_place' in results[second_player]:
                        results[second_player]['second_place'] = 0
                    results[second_player]['second_place'] += 1
                    results[second_player]['score'] += nb_players
                if nb_players >= 4:
                    # Four players or more
                    ## Third
                    third_player = classement[2][0]
                    if not 'third_place' in results[third_player]:
                        results[third_player]['third_place'] = 0
                    results[third_player]['third_place'] += 1
                    results[third_player]['score'] += nb_players / 2

    if selected_player and selected_player in results:
        return results[selected_player]
    else:
        return results


def get_item_stats(item, gametype=None, with_warmup=False):
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
        if gametype:
            kraw_data = kill_table.find({"$and" :[{'weapon' : kitem}, {'gametype': gametype.upper()}]})
        else:
            kraw_data = kill_table.find({'weapon' : kitem})
        stats = reduce(compute_weapon_stats,
                       kraw_data,
                       {kill_with_key: {}, dead_by_key: {}})
    if item in pickup_mapping:
        pitem = pickup_mapping[item]
        if gametype:
            praw_data = pickup_table.find({"$and": [{'item': pitem}, {'gametype': gametype.upper()}] })
        else:
            praw_data = pickup_table.find({'item': pitem})
        pstats = reduce(compute_item_stats, praw_data, {})
        stats.update({'pick up': pstats})

    return stats

def get_player_items_stats(player, gametype=None, with_warmup=False):
    def compute_item_stats(ret, data):
        # warmup
        if (not with_warmup) and data['round'] == None:
            return ret

        key = r_pickup_mapping[data['item']]
        if not key in ret:
            ret[key] = 0
        ret[key] += 1
        return ret

    raw_pickup_stats = pickup_table.find({'player' : player})
    pstats = reduce(compute_item_stats, raw_pickup_stats, {})

    return pstats


def get_general_players_stats(gametype=None, with_warmup=False):
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


def get_player_stats(player, gametype=None, with_warmup=False):
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
    raw_pickup_stats = pickup_table.find({'player': player})
    pstats = reduce(compute_item_stats, raw_pickup_stats, {})

    return kstats, vstats, pstats




##### USELESS ####
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
