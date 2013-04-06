import os
import sys
import Queue

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

def empty_db(self):
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
    get_round_classement(player)

    return score



def get_round_classement(player):
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
#            if not 'round' in data:
#                import pdb;pdb.set_trace()
#                sd
#            if str(data['round']) == '514ba5120182b00618001cf5':
#                import pdb;pdb.set_trace()
            if 'round' in data and not data['round'] is None:
                if not data['round'] in ret:
                    ret[data['round']] = []
                ret[data['round']].append(data)
                ret[data['round']].sort(key=lambda x: x['when'])
        return ret, type_
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
    join_by_map = reduce(join_none_reducer, join_table.find(), {})

    def round_reducer(ret, data):
        if not data['map'] in ret:
            ret[data['map']] = []
        ret[data['map']].append(data)

        return ret
    rounds = reduce(round_reducer, round_table.find(), {})

    maps = dict([(x['_id'], x) for x in map_table.find()])

    for map_, round_in_a_map in rounds.items():
        # SET INITIAL DATA
        print "================================================================="
        map_data = {}
        map_data['map'] = map_
        map_data['players'] = {}
        map_data['rounds'] = {}
        # GET JOINs DURING WARMUP
        for join in join_by_map.get(map_, []):
            map_data['players'][join['player']] = {} 
            map_data['players'][join['player']]['team'] = join['team']
            map_data['players'][join['player']]['score'] = 0
        # ITER on rounds in a map
        for i, round_ in enumerate(round_in_a_map):
            ### NEW ROUND ###
            print "-----------------------------------"
            end_of_round = False
            map_data['rounds'][i] = {}
            map_data['rounds'][i]['gametype'] = round_['gametype']
            map_data['rounds'][i]['teamplay'] = round_['teamplay']
            # SET PLAYERS A round start
            if i == 0:
                map_data['rounds'][i]['players'] = map_data['players'].copy()
            else:
                map_data['rounds'][i]['players'] = map_data['rounds'][i - 1]['players'].copy()
            # Check if there are any events in a round
            if not round_['_id'] in events_by_round:
                print "NOTFOUND !!!!!!!!!!!!", round_['_id']
#                import pdb;pdb.set_trace()
                # POSSIBLE ?????
                continue
            # ITER ON Events in a round
            print [(x['player'], x['type']) for x in events_by_round[round_['_id']] if 'player' in x]
            for event in events_by_round[round_['_id']]:
                if event['type'] == 'join':
                    map_data['rounds'][i]['players'][event['player']] = {}
                    map_data['rounds'][i]['players'][event['player']]['team'] = event['team']
                    map_data['rounds'][i]['players'][event['player']]['score'] = 0
#                    print event
                if event['type'] == 'kill':
#                    import pdb;pdb.set_trace()
                    if not event['killer'] in map_data['rounds'][i]['players']:
#                        print "NOTFOUND !!!!!!!!!!!!k", event['killer'], event['when'], event
#                        import pdb;pdb.set_trace()
                         # POSSIBLE ????? rename ??
                        continue
                    if not event['victim'] in map_data['rounds'][i]['players']:
#                        print "NOTFOUND !!!!!!!!!!!!v", event['victim'], event['when'], event
#                        import pdb;pdb.set_trace()
                         # POSSIBLE ????? rename ??
                        continue
                    if event['killer'] == event['victim']:
                        map_data['rounds'][i]['players'][event['killer']]['score'] -= 1
                    elif round_['teamplay'] and map_data['rounds'][i]['players'][event['killer']]['team'] == map_data['rounds'][i]['players'][event['victim']]:
                        map_data['rounds'][i]['players'][event['killer']]['score'] -= 1
                    else:
                        map_data['rounds'][i]['players'][event['killer']]['score'] += 1
                if event['type'] == 'changeteam':
                    import pdb;pdb.set_trace()
                    print event
                if event['type'] == 'kick':
                    import pdb;pdb.set_trace()
                    print event
                if event['type'] == 'timeout':
                    import pdb;pdb.set_trace()
                    print event
                if event['type'] == 'leave':
                    map_data['rounds'][i]['players'][event['player']]['status'] = 'offline'
                    import pdb;pdb.set_trace()
                    print event
                if event['type'] == 'servershutdown':
                    import pdb;pdb.set_trace()
                    # END OF ROUND
                    end_of_round = True
                    break
                    print event

        print map_data



    return

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
