from libs.lib import tee_db
from datetime import datetime, timedelta
from libs.achievement import Achievement, achievement_list

def kill_death_fct(self, player):
    def map_data(x, y):
        if not y:
            return 0
        if x['killer'] == y['victim'] and \
                y['killer'] == x['victim'] and \
                y['when'] - x['when'] <= timedelta(seconds=1) and\
                x['round'] == y['round'] and \
                x['round'] != None:
            return 1
        return 0
    data_iter = self.kill_table.find( { "$or": [ {'killer': player}, {'victim': player} ] }).sort('when')
    data_iter1 =  self.kill_table.find( { "$or": [ {'killer': player}, {'victim': player} ] }).sort('when')
    ret = map(map_data, data_iter, data_iter1[1:])

    return {0: ('Kill Death', sum(ret))}


kill_death = Achievement('Kill Death', 'killdeath.png', 'Description', kill_death_fct)

achievement_list['kill_death'] = kill_death
