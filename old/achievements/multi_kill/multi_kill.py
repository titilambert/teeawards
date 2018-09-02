import copy

from pymongo import DESCENDING

from libs.lib import tee_db
from bottle import mako_view
from datetime import datetime, timedelta
from libs.achievement import achievement_desc_list, achievement_player_list, achievement_livestat_list
from libs.lib import kill_table
from libs.lib import econ_command_queue



@mako_view("desc_multi_kill")
def desc_multi_kill():
    return {"multikill_list": multikill_list}
    

@mako_view("player_multi_kill")
def player_multi_kill(player, gametype):
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

    ret_multikill = copy.copy(multikill_list)
    for mk, value in ret.items():
        if mk in ret_multikill:
            ret_multikill[mk] = (ret_multikill[mk][0], value)

    # TODO RETURN THIS
#    max_multikill = max(ret.keys())

    return {'multikill_list': ret_multikill}


def livestat_multi_kill(new_data):
    def reduce_data(ret, data):
        if data['killer'] != data['victim'] and ret[1] and data['killer'] == player:
            return (ret[0] + 1, True)
        return (ret[0], False)
    player = new_data['killer']
    round_ = new_data['round']
    data = kill_table.find({ "$and": [{ "$or": [{'killer': player},
                                                {'victim': player},
                                               ]
                                      },
                                      {'round': round_},
                                     ]
                           }
                          ).sort('when', DESCENDING)
    
    multi_level = reduce(reduce_data, data, (0, True))
    multikill_name = multikill_list.get(multi_level[0], None)
    if multikill_name:
        msg = "(%s) !!! %s !!! (%s kills)" % (player, multikill_name[0].upper(), multi_level[0])
        econ_command_queue.put({'type': 'broadcast',
                                'data': {'message': msg}
                              })


#multikill_list = {
#        3: ('Triple Kill', 0),
#        5: ('Multi Kill', 0),
#        6: ('Rampage', 0),
#        7: ('Killing Spree', 0),
#        9: ('Dominating', 0),
#        11: ('Unstoppable', 0),
#        13: ('Mega Kill', 0),
#        15: ('Ultra Kill', 0),
#        16: ('Eagle Eye', 0),
#        17: ('Ownage', 0),
#        18: ('Ludicrouskill', 0),
#        19: ('Head Hunter', 0),
#        20: ('Whicked Sick', 0),
#        21: ('Monster Kill', 0),
#        23: ('Holy Shit', 0),
#        24: ('God Like', 0),
#        }

multikill_list = {
        3: ('Triple Kill', 0),
        4: ('Multi Kill', 0),
        5: ('Rampage', 0),
        6: ('Killing Spree', 0),
        7: ('Dominating', 0),
        8: ('Unstoppable', 0),
        9: ('Mega Kill', 0),
        10: ('Ultra Kill', 0),
        11: ('Eagle Eye', 0),
        12: ('Ownage', 0),
        13: ('Ludicrouskill', 0),
        14: ('Head Hunter', 0),
        15: ('Wicked Sick', 0),
        16: ('Monster Kill', 0),
        17: ('Holy Shit', 0),
        18: ('God Like', 0),
        }


achievement_desc_list['desc_multi_kill'] = desc_multi_kill
achievement_player_list['player_multi_kill'] = player_multi_kill
achievement_livestat_list['livestat_multi_kill'] = livestat_multi_kill
