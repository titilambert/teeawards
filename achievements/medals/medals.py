from pymongo import DESCENDING

from libs.lib import tee_db, get_stats, get_player_stats
from bottle import mako_view
from datetime import datetime, timedelta
from libs.achievement import achievement_desc_list, achievement_player_list, achievement_livestat_list
from libs.lib import kill_table


@mako_view("desc_medals")
def desc_medals():
    return {'medal_list': medals_list}

@mako_view("player_medals")
def player_medals(player, gametype):
    player_stats = get_stats(player, gametype)

    medal_result = {}

    medal_result['gold star'] = player_stats.get('first_place', 0)
    medal_result['silver star'] = player_stats.get('second_place', 0)
    medal_result['bronze star'] = player_stats.get('third_place', 0)
    medal_result['chocolate star'] = player_stats.get('last_place', 0)
    medal_result['purple heart'] = player_stats.get('purple', 0)
    medal_result['eternal heart'] = player_stats.get('no death', 0)

    return {'results': medal_result,
            'medals_list': medals_list}


def livestat_medals(new_data):
    return None


#
medals_list = [
        ('gold star', 'First place IAR'),
        ('silver star', 'Second place IAR'),
        ('bronze star', 'Third place IAR'),
        ('chocolate star', 'Last place IAR'),
        ('purple heart', 'Ratio < 1:4 IAR'),
        ('eternal heart', 'No death IAR'),
        ]

achievement_desc_list['desc_medals'] = desc_medals
achievement_player_list['player_medals'] = player_medals
achievement_livestat_list['livestat_medals'] = livestat_medals
