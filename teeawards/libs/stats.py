from teeawards.const import R_PICKUP_MAPPING, R_KILL_MAPPING, RANKS


def get_rounds(influx_client):
    """Get rounds."""
    res = influx_client.query('select round from round')
    if len(res):
        round_list = list(set([str(r['round']) for r in res.items()[0][1]]))
        return round_list
    return []


def get_kills_by_players(influx_client):
    """Get kills by player."""
    round_list = get_rounds(influx_client)

    query = "SELECT count(*) AS kills FROM kills WHERE round =~ /{}/ GROUP BY killer".format("|".join(round_list))
    res = influx_client.query(query)
    kills_by_players = dict((x[0][1]['killer'], [y['kills_value'] for y in x[1]][0]) for x in res.items())
    # [('player1', 5), ('player2', 4)]
    return kills_by_players


def get_deaths_by_players(influx_client):
    """Get deaths by player."""
    round_list = get_rounds(influx_client)

    query = "SELECT count(*) AS deaths FROM kills WHERE round =~ /{}/ GROUP BY victim".format("|".join(round_list))
    res = influx_client.query(query)
    deaths_by_players = dict((x[0][1]['victim'], [y['deaths_value'] for y in x[1]][0]) for x in res.items())
    # [('player1', 5), ('player2', 4)]
    return deaths_by_players


def get_suicides_by_players(influx_client):
    """Get suicides by players."""
    round_list = get_rounds(influx_client)

    query = "SELECT count(*) AS suicides FROM kills WHERE victim = killer AND round =~ /{}/ GROUP BY victim".format("|".join(round_list))
    res = influx_client.query(query)
    suicides_by_players = dict((x[0][1]['victim'], [y['suicides_value'] for y in x[1]][0]) for x in res.items())
    # [('player1', 5), ('player2', 4)]
    return suicides_by_players

def get_rounds_by_players(influx_client):
    """Get number of rounds by player.

    * Excluding warmup round (round == '')
    * Removing round duplication

    .. todo:: validate this query
    """
    query = """select count(*) as rounds from (SELECT count(value) FROM join GROUP BY player, round) WHERE round != '' group by player"""
    res = influx_client.query(query)
    rounds_by_players = dict((x[0][1]['player'], [y['rounds_count'] for y in x[1]][0]) for x in res.items()) 
    return rounds_by_players
    
def get_teamkills_by_players(influx_client):
    """Get number of teamkills by players."""
    round_list = get_rounds(influx_client)
    query = "SELECT count(*) AS kills FROM kills WHERE killer_team = victim_team AND killer_team != '0' AND round =~ /{}/ GROUP BY killer".format("|".join(round_list))
    res = influx_client.query(query)
    rounds_by_players = dict((x[0][1]['player'], [y['kills_count'] for y in x[1]][0]) for x in res.items())
    return rounds_by_players

def get_kills_by_players_weapon(influx_client):
    """Get kills by player."""
    round_list = get_rounds(influx_client)

    query = "SELECT count(*) AS kills FROM kills WHERE round =~ /{}/ GROUP BY killer, weapon".format("|".join(round_list))
    res = influx_client.query(query)
    ret = {}
    tmp = [(x[0][1]['killer'], {x[0][1]['weapon']: [y['kills_value'] for y in x[1]][0]}) for x in res.items()]  
    for player, stat in tmp:
        ret.setdefault(player, {})
        ret[player].update(stat)
    # {'player1': {'-3': 3, '1': 2, '3': 1}, 'player2': {'-3': 3, '0': 1, '1': 1, '3': 2}}
    return ret

def get_pickups_by_players_items(influx_client):
    """Get pickup by players."""
    round_list = get_rounds(influx_client)

    query = "SELECT count(*) AS pickup FROM pickup WHERE round =~ /{}/ GROUP BY item, player".format("|".join(round_list))
    res = influx_client.query(query)

    pickup_by_user = {}
    for key, data in res.items():
        pickup_by_user.setdefault(key[1]['player'], {})
        str_key = R_PICKUP_MAPPING[key[1]['item']]
        pickup_by_user[key[1]['player']][str_key] = [x['pickup_value'] for x in data][0]
    return pickup_by_user

#######################################################3

def get_rounds_for_player(influx_client, player):
    """Return nb rounds for one player."""
    rounds_by_players = get_rounds_by_players(influx_client)
    return rounds_by_players.get(player, 0)

def get_rank_for_player(influx_client, player):
    """Return rank for one player."""
    rank_by_players = get_rank_by_players(influx_client)
    return rank_by_players.get(player, 0)


def get_kills_for_player(influx_client, player):
    """Return kills for one player."""
    kills_by_players = get_kills_by_players(influx_client)
    return kills_by_players.get(player, 0)

def get_deaths_for_player(influx_client, player):
    """Return deaths for one player."""
    deaths_by_players = get_deaths_by_players(influx_client)
    return deaths_by_players.get(player, 0)

def get_suicides_for_player(influx_client, player):
    """Return suicides for one player."""
    suicides_by_players = get_suicides_by_players(influx_client)
    return suicides_by_players.get(player, 0)

def get_teamkills_for_player(influx_client, player):
    """Return teamkills for one player."""
    teamkills_by_players = get_teamkills_by_players(influx_client)
    return teamkills_by_players.get(player, 0)

def get_score_for_player(influx_client, player):
    score_by_players = get_scores(influx_client)
    return score_by_players.get(player, 0)

def get_ratio_for_player(influx_client, player):
    ratio_by_players = get_ratios(influx_client)
    return ratio_by_players.get(player, 0)

def get_kills_by_weapon_for_player(influx_client, player):
    kills_by_players_weapon = get_kills_by_players_weapon(influx_client)
    return kills_by_players_weapon.get(player, {})

def get_pickups_by_items_for_player(influx_client, player):
    pickups_by_players = get_pickups_by_players_items(influx_client)
    return pickups_by_players.get(player, {})

#######################################################3

def get_ratios(influx_client):
    """Get best ratio."""
    kills_by_players = get_kills_by_players(influx_client)
    deaths_by_players = get_deaths_by_players(influx_client)
    if kills_by_players and deaths_by_players:
        res = {}
        players = set(kills_by_players.keys()).union(set(deaths_by_players.keys()))
        for player in players:
            res[player] = kills_by_players.get(player, 0) / deaths_by_players.get(player, 1)
        return res
    return None


def get_scores(influx_client):
    """Get scores."""
    #TODO complete this with CTF and round scores
    kills_by_players = get_kills_by_players(influx_client)
    suicides_by_players = get_suicides_by_players(influx_client)
    if suicides_by_players and kills_by_players:
        res = {}
        players = set(kills_by_players.keys()).union(set(suicides_by_players.keys()))
        for player in players:
            res[player] = kills_by_players.get(player, 0) - suicides_by_players.get(player, 0)
        return res
    return None


def get_rank_by_players(influx_client):
    scores_by_players = get_scores(influx_client)
    if scores_by_players:
        res = {}
        for player, score in scores_by_players.items():
            for i, rank in enumerate(RANKS):
                if score < rank[1]:
                    break
                res[player] = i
        return res
    return None
        

def get_stats_by_players(influx_client):
    kills_by_players = get_kills_by_players(influx_client)
    suicides_by_players = get_suicides_by_players(influx_client)
    deaths_by_players = get_deaths_by_players(influx_client)
    ratios_by_players = get_ratios(influx_client)
    scores_by_players = get_scores(influx_client)
    rank_by_players = get_rank_by_players(influx_client)
    if kills_by_players and deaths_by_players:
        res = {}
        players = set(kills_by_players.keys()).union(set(deaths_by_players.keys())).union(set(suicides_by_players.keys()))
        for player in players:
            res[player] = {'kills': kills_by_players.get(player, 0),
                           'deaths': deaths_by_players.get(player, 0),
                           'suicides': suicides_by_players.get(player, 0),
                           'ratio': ratios_by_players.get(player, 0),
                           'score': scores_by_players.get(player, 0),
                           'rank': rank_by_players.get(player, 0),
                           }
        return res
    return {}
    #import ipdb;ipdb.set_trace()

def get_stats_by_items(influx_client):
    """???"""
    ret = {}
    round_list = get_rounds(influx_client)

    #kill_with_key = 'kill with ' + item.capitalize()
    #dead_by_key = 'dead by ' + item.capitalize()

    # TODO remove '-3' weapon
    query = "SELECT count(*) AS kills FROM kills WHERE round =~ /{}/ GROUP BY weapon, killer".format("|".join(round_list))
    res = influx_client.query(query)
    kills_by_weapon = {}
    for key, data in res.items():
        str_key = R_KILL_MAPPING[key[1]['weapon']]
        kills_by_weapon.setdefault(str_key, {})
        kills_by_weapon[str_key][key[1]['killer']] = [x['kills_value'] for x in data][0]
    for item, stat in kills_by_weapon.items():
        ret.setdefault(item, {})
        ret[item]['kill'] = stat
    # TODO remove '-3' weapon
    query = "SELECT count(*) AS deaths FROM kills WHERE round =~ /{}/ GROUP BY weapon, victim".format("|".join(round_list))
    res = influx_client.query(query)
    deaths_by_weapon = {}
    for key, data in res.items():
        str_key = R_KILL_MAPPING[key[1]['weapon']]
        deaths_by_weapon.setdefault(str_key, {})
        deaths_by_weapon[str_key][key[1]['victim']] = [x['deaths_value'] for x in data][0]
    for item, stat in kills_by_weapon.items():
        ret.setdefault(item, {})
        ret[item]['death'] = stat

    query = "SELECT count(*) AS pickup FROM pickup WHERE round =~ /{}/ GROUP BY item, player".format("|".join(round_list))
    res = influx_client.query(query)
#    import ipdb;ipdb.set_trace()
    pickup_by_user = {}
    for key, data in res.items():
        str_key = R_PICKUP_MAPPING[key[1]['item']]
        pickup_by_user.setdefault(str_key, {})
        pickup_by_user[str_key][key[1]['player']] = [x['pickup_value'] for x in data][0]
    for item, stat in pickup_by_user.items():
        ret.setdefault(item, {})
        ret[item]['pickup'] = stat

    return ret


#######################################################3

def get_best_killer(influx_client):
    """Get best killer."""
    round_list = get_rounds(influx_client)

    best_killer = influx_client.query("select killer as player, max(kills_value) as kills from ( select count(*) as kills from kills where round =~ /{}/ group by killer )".format("|".join(round_list)))
    if len(best_killer):
        best_killer = [x for x in best_killer][0][0]
        return (best_killer['player'], best_killer['kills'])
    return None


def get_best_victim(influx_client):
    """Get best victim."""
    round_list = get_rounds(influx_client)

    best_victim = influx_client.query("select victim as player, max(deaths_value) as deaths from ( select count(*) as deaths from kills where round =~ /{}/ group by victim )".format("|".join(round_list)))
    if len(best_victim):
        best_victim = [x for x in best_victim][0][0]
        return (best_victim['player'], best_victim['deaths'])

    return None


def get_best_suicider(influx_client):
    """Get best suicider."""
    round_list = get_rounds(influx_client)

    best_suicider = influx_client.query("select victim as player, max(suicides_value) as suicides from ( select count(*) as suicides from kills where victim = killer and round =~ /{}/ group by victim )".format("|".join(round_list)))
    if len(best_suicider):
        best_suicider = [x for x in best_suicider][0][0]
        return (best_suicider['player'], best_suicider['suicides'])
    return None


def get_best_hammer_victim(influx_client):
    """Get best hammer victim."""
    round_list = get_rounds(influx_client)

    best_hammer_victim = influx_client.query("select victim as player, max(deaths_value) as deaths from ( select count(*) as deaths from kills where weapon = '0' and round =~ /{}/ group by victim )".format("|".join(round_list)))
    if len(best_hammer_victim):
        best_hammer_victim = [x for x in best_hammer_victim][0][0]
        return (best_hammer_victim['player'], best_hammer_victim['deaths'])
    return None


def get_best_ratio(influx_client):
    """Get best ratio."""
    ratios = get_ratios(influx_client)
    if ratios:
        best_ratio = max(ratios.items(), key=lambda x: x[1])
        return best_ratio
    return None


def get_best_score(influx_client):
    """Get best score."""
    scores = get_scores(influx_client)
    if scores:
        best_score = max(scores.items(), key=lambda x: x[1])
        return best_score
    return None
