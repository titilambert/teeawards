from pymongo import DESCENDING

from libs.lib import tee_db, get_stats, get_player_stats
from bottle import mako_view
from datetime import datetime, timedelta
from libs.achievement import achievement_desc_list, achievement_player_list, achievement_livestat_list
from libs.lib import kill_table


@mako_view("desc_badges")
def desc_badges():
    ordered_list = ['winner', 'heart', 'shield', 'hammer', 'gun',
                    'shotgun', 'grenade', 'laser', 'ninja']
    badges = [(i, badge_list[i]) for i in ordered_list]

    return {'badge_list': badges}

@mako_view("player_badges")
def player_badges(player):
    player_stats = get_stats(player)
    kills, _, items = get_player_stats(player)

    badge_result = dict([(x, 0) for x in badge_list])
    for badge, limits in badge_list.items():
        if badge in kills['weapon']:
            badge_result[badge] = 0
            for i, l in enumerate(limits):
                if kills['weapon'][badge] > l:
                    badge_result[badge] = i + 1
        elif badge in items:
            badge_result[badge] = 0
            for i, l in enumerate(limits):
                if items[badge] > l:
                    badge_result[badge] = i + 1
        elif badge == 'winner':
            badge_result[badge] = 0
            for i, l in enumerate(limits):
                if player_stats.get('first', 0) > l:
                    badge_result[badge] = i + 1

    return {'results': badge_result}


def livestat_badges(live_stat, new_data):
    return None


badge_list = {
        'hammer': [100, 400, 1000],
        'gun': [100, 400, 1000],
        'shotgun': [100, 400, 1000],
        'grenade': [100, 400, 1000],
        'laser': [100, 400, 1000],
        'ninja': [50, 200, 500],
        'winner': [50, 200, 500],
        'heart': [500, 1500, 4000],
        'shield': [500, 1500, 4000],
        }

achievement_desc_list['desc_badges'] = desc_badges
achievement_player_list['player_badges'] = player_badges
achievement_livestat_list['livestat_badges'] = livestat_badges
