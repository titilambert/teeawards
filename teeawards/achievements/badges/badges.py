import os
#from pymongo import DESCENDING

#from libs.lib import tee_db, get_stats, get_player_stats
from mako.template import Template
from mako.lookup import TemplateLookup


from teeawards.const import R_KILL_MAPPING, KILL_MAPPING
from teeawards.libs.stats import get_kills_by_weapon_for_player, get_pickups_by_items_for_player
#from bottle import mako_view
#from datetime import datetime, timedelta
#from libs.achievement import achievement_desc_list, achievement_player_list, achievement_livestat_list
#from libs.lib import kill_table


#@mako_view("desc_badges")
def desc_badges():
    ordered_list = ['winner', 'heart', 'shield', 'hammer', 'gun',
                    'shotgun', 'grenade', 'laser', 'ninja']
    badges = [(i, badge_list[i]) for i in ordered_list]

    template_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "views"))
    mylookup = TemplateLookup(directories=[template_folder])
    mytemplate = mylookup.get_template('desc_badges.tpl')

    ret = mytemplate.render(**{'badge_list': badges})
    return ret

#@mako_view("player_badges")
def player_badges(influx_client, player, gametype):
#    player_stats = get_stats(player, gametype)
#    kills, _, items = get_player_stats(player)
    kills = get_kills_by_weapon_for_player(influx_client, player)
    items = get_pickups_by_items_for_player(influx_client, player)
    

    badge_result = dict((x, 0) for x in badge_list)
    for badge, limits in badge_list.items():
        if badge in ['heart', 'shield']:
            badge_result[badge] = 0
            for i, l in enumerate(limits):
                if items[badge] > l:
                    badge_result[badge] = i + 1
        elif badge == 'winner':
            badge_result[badge] = 0
            for i, l in enumerate(limits):
#                import ipdb;ipdb.set_trace()
                pass
                # TODO
#                if player_stats.get('first', 0) > l:
#                    badge_result[badge] = i + 1
        elif KILL_MAPPING[badge] in kills.keys():
            badge_result[badge] = 0
            for i, l in enumerate(limits):
                if kills[KILL_MAPPING[badge]] > l:
                    badge_result[badge] = i + 1



    template_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "views"))
    mylookup = TemplateLookup(directories=[template_folder])
    mytemplate = mylookup.get_template('player_badges.tpl')
    ret = mytemplate.render(**{'results': badge_result})

    return ret


def livestat_badges(new_data):
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

#achievement_desc_list['desc_badges'] = desc_badges
#achievement_player_list['player_badges'] = player_badges
#achievement_livestat_list['livestat_badges'] = livestat_badges
