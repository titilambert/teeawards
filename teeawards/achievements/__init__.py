#achievement_desc_list = {}
#achievement_player_list = {}
#achievement_livestat_list = {}
#for a in achievements.__all__:
#    __import__('achievements.' + a.replace("/", "."))


#import glob
#import re
#import os
#"""Lists all of the importable plugins"""

#regexp = os.path.join(os.path.dirname(__file__), "..", 'achievements/(.*/.*)\.py')
#achievements = glob.glob(os.path.join(os.path.dirname(__file__), "..", 'achievements/*/*.py'))
#achievements = list([re.match(regexp, x).groups()[0] for x in achievements])

#achievements = [a for a in achievements if not a.endswith('__init__')]

#__all__ = achievements


from teeawards.achievements.badges.badges import desc_badges, player_badges

achievement_desc_list = {}
achievement_desc_list['desc_badges'] = desc_badges

achievement_player_list = {}
achievement_player_list['player_badges'] = player_badges
