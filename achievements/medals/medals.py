from pymongo import DESCENDING

from libs.lib import tee_db, get_stats, get_player_stats
from bottle import mako_view
from datetime import datetime, timedelta
from libs.achievement import achievement_desc_list, achievement_player_list, achievement_livestat_list
from libs.lib import kill_table


@mako_view("desc_medals")
def desc_medals():
    ordered_list = ['winner', 'heart', 'shield', 'hammer', 'gun',
                    'shotgun', 'grenade', 'laser', 'ninja']
    badges = [(i, badge_list[i]) for i in ordered_list]

    return {'badge_list': badges}

@mako_view("player_medals")
def player_medals(player):
    player_stats = get_stats(player)

    medal_result = {}

    medal_result['gold'] = player_stats.get('first_place', 0)
    medal_result['silver'] = player_stats.get('silver_place', 0)
    medal_result['bronze'] = player_stats.get('bronze_place', 0)
    medal_result['fake gold'] = player_stats.get('last_place', 0)
    medal_result['purple'] = player_stats.get('purple', 0)
    medal_result['no death'] = player_stats.get('no death', 0)

    return {'results': medal_result,
            'medals_list': medals_list}


def livestat_medals(live_stat, new_data):
    return None


#
medals_list = [
        ('gold', 'First place IAR'),
        ('silver', 'Second place IAR'),
        ('bronze', 'Third place IAR'),
        ('fake gold', 'Last place IAR'),
        ('purple', 'Ratio < 1:4 IAR'),
        ('no death', 'No death IAR'),
        ]

achievement_desc_list['desc_medals'] = desc_medals
achievement_player_list['player_medals'] = player_medals
achievement_livestat_list['livestat_medals'] = livestat_medals
