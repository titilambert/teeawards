from libs.lib import tee_db

class Achievement():
    def __init__(self, name, image, condition):
        self.name = name
        self.image = image
        self.condition = condition
        # Prepare table
        self.join_table = tee_db['join']
        self.changeteam_table = tee_db['changeteam']
        self.round_table = tee_db['round']
        self.map_table = tee_db['map']
        self.kick_table = tee_db['kick']
        self.timeout_table = tee_db['timeout']
        self.leave_table = tee_db['leave']
        self.pickup_table = tee_db['pickup']
        self.kill_table = tee_db['kill']
        self.flaggrab_table = tee_db['flaggrab']
        self.flagreturn_table = tee_db['flagreturn']
        self.flagcapture_table = tee_db['flagcapture']

    def has_achievements(self, player):
        return self.condition(self, player)


def double_kill_fct(self, player):
    def toto(x, y):
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

    def tata(ret, data):
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

    data_iter = self.kill_table.find( { "$or": [ {'killer': player}, {'victim': player} ] }).sort('when')
    data_iter1 =  self.kill_table.find( { "$or": [ {'killer': player}, {'victim': player} ] }).sort('when')
    ret = map(toto, data_iter, data_iter1[1:])
    print ret
    ret = reduce(tata, ret, {'tmp': 0})
    if ret['tmp'] != 0:
        if not ret['tmp'] + 1 in ret:
            ret[ret['tmp'] + 1] = 0
        ret[ret['tmp'] + 1] += 1
    del(ret['tmp'])
    print ret
    return  ret

from datetime import datetime, timedelta
def time_fct(self, player):
    def toto(x, y):
        if y is None:
            return (x['when'], None)
        return (x['when'], y['when'])

    def tata(time, x):
        if x[1]:
            time += x[1] - x[0]
        return time
        

    raw_join_data = self.join_table.find({'player': player}).sort('when')
    raw_leave_data = self.leave_table.find({'player': player}).sort('when')

    data = map(toto, raw_join_data, raw_leave_data)

    ret = reduce(tata, data, timedelta(0))
    return ret

dk = Achievement('Double Kill', 'doublekill.png', double_kill_fct)
time = Achievement('Time played', 'tomeplayed.png', time_fct)

achievement_list = {'Double Kill': dk,
                    'Time played': time,
}
