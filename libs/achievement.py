from libs.lib import tee_db
from datetime import datetime, timedelta
import achievements

class Achievement():
    def __init__(self, name, image, description, condition):
        self.name = name
        self.image = image
        self.description = description
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


achievement_list = {}
for a in achievements.__all__:
    __import__('achievements.' + a.replace("/", "."))
    print a 
