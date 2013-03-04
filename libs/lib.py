from pymongo import Connection

con = Connection()
tee_db = con['teeworlds']
pickup_table = tee_db['pickup']
kill_table = tee_db['kill']

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
#red team=0
#blue team=1


# Mapping
pickup_mapping = {
    'hearth': '0/0',
    'shield': '1/0',
    'shutgun': '2/2',
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
    'shutgun': '2',
    'grenade': '3',
    'laser': '4',
    'ninja': '5',
    }

r_kill_mapping = dict([(x[1], x[0]) for x in kill_mapping.items()])
r_pickup_mapping = dict([(x[1], x[0]) for x in pickup_mapping.items()])


def get_general_players_stats():
    def get_stats_by_players(ret, data):
        if data['weapon'] == '-3':
            # Handle exit
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


def get_item_stats(item):
    kill_with_key = 'kill with ' + item.capitalize()
    dead_by_key = 'dead by ' + item.capitalize()
    def compute_weapon_stats(ret, data):
        if not data['killer'] in ret[kill_with_key]:
            ret[kill_with_key][data['killer']] = 0
        ret[kill_with_key][data['killer']] += 1
        if not data['victim'] in ret[dead_by_key]:
            ret[dead_by_key][data['victim']] = 0
        ret[dead_by_key][data['victim']] += 1
        return ret

    def compute_item_stats(ret, data):
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

    

def get_player_stats(player):
    def compute_item_stats(ret, data):
        key = r_pickup_mapping[data['item']]
        if not key in ret:
            ret[key] = 0
        ret[key] += 1
        return ret

    def compute_kill_stats(ret, data):
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

        return ret

    raw_killer_stats = kill_table.find({'killer' : player})
    kstats = reduce(compute_kill_stats, raw_killer_stats, {'weapon': {}, 'victim': {}})
    raw_victim_stats = kill_table.find({'victim' : player})
    vstats = reduce(compute_victim_stats, raw_victim_stats, {'weapon': {}, 'killer': {}, 'suicide': 0})
    raw_pickup_stats = pickup_table.find({'player' : player})
    pstats = reduce(compute_item_stats, raw_pickup_stats, {})

    return kstats, vstats, pstats






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