from libs.lib import tee_db
from bottle import mako_view
from datetime import datetime, timedelta
from libs.achievement import achievement_desc_list, achievement_player_list
from libs.lib import kill_table


@mako_view("desc_multi_kill")
def desc_multi_kill():
    return {"multikill_list": multikill_list}
    

@mako_view("player_multi_kill")
def player_multi_kill(player):
    def map_data(x, y):
        if not y:
            return 0
        if x['killer'] == y['killer'] and \
                x['killer'] != x['victim'] and \
                y['killer'] != y['victim'] and \
                x['round'] == y['round'] and \
                x['killer'] == player and \
                x['round'] != None:
            return 1
        return 0

    def reduce_data(ret, data):
        # check if multikill is finished
        if data == 0:
            # check if kill counter is != 0
            if ret['tmp'] != 0:
                # Check if it is the first multikill with "ret['tmp'] + 1" kills
                if not ret['tmp'] + 1 in ret:
                    # if not init it
                    ret[ret['tmp'] + 1] = 0
                # Add 1
                ret[ret['tmp'] + 1] += 1
                # Reinit kill counter
                ret['tmp'] = 0
        elif data == 1:
            # increment kill counter
            ret['tmp'] += 1
        return ret

    data_iter = kill_table.find( { "$or": [ {'killer': player}, {'victim': player} ] }).sort('when')
    data_iter1 =  kill_table.find( { "$or": [ {'killer': player}, {'victim': player} ] }).sort('when')
    ret = map(map_data, data_iter, data_iter1[1:])
    ret = reduce(reduce_data, ret, {'tmp': 0})
    if ret['tmp'] != 0:
        if not ret['tmp'] + 1 in ret:
            ret[ret['tmp'] + 1] = 0
        ret[ret['tmp'] + 1] += 1
    del(ret['tmp'])

    
    for mk, value in ret.items():
        if mk in multikill_list:
            multikill_list[mk] = (multikill_list[mk][0], value)

    # TODO RETURN THIS
    max_multikill = max(ret.keys())

    return {'multikill_list': multikill_list}


multikill_list = {
        3: ('Triple Kill', 0),
        5: ('Multi Kill', 0),
        6: ('Rampage', 0),
        7: ('Killing Spree', 0),
        9: ('Dominating', 0),
        11: ('Unstoppable', 0),
        13: ('Mega Kill', 0),
        15: ('Ultra Kill', 0),
        16: ('Eagle Eye', 0),
        17: ('Ownage', 0),
        18: ('Ludicrouskill', 0),
        19: ('Head Hunter', 0),
        20: ('Whicked Sick', 0),
        21: ('Monster Kill', 0),
        23: ('Holy Shit', 0),
        24: ('God Like', 0),
        }


achievement_desc_list['desc_multi_kill'] = desc_multi_kill
achievement_player_list['player_multi_kill'] = player_multi_kill

