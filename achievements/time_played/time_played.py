from libs.lib import tee_db
from datetime import datetime, timedelta
from libs.achievement import Achievement, achievement_list

def time_fct(self, player):
    def map_data(x, y):
        if y is None:
            return (x['when'], None)
        return (x['when'], y['when'])

    def reduce_data(time, x):
        if x[1]:
            time += x[1] - x[0]
        return time

    raw_join_data = self.join_table.find({'player': player}).sort('when')
    raw_leave_data = self.leave_table.find({'player': player}).sort('when')
    # TODO: Handle when the server is shutdown
    data = map(map_data, raw_join_data, raw_leave_data)
    ret = reduce(reduce_data, data, timedelta(0))
    return ret

time_played = Achievement('Time played', 'tomeplayed.png', 'Description', time_fct)

#achievement_list['time_played'] = time_played
