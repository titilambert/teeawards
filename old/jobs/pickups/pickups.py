from datetime import datetime

from pymongo import DESCENDING

from libs.lib import tee_db, pickup_mapping
from libs.statisticator import Job


class PickupsJob(Job):
    def __init__(self):
        """ Job to get player pickups
              Collection name: pickups_results
              Struture:
                    {'player': STR ,
                     'pickups': INT ,
                     'item': INT ,
                     'gametype': STR,
                     'last_event_date': DATE ,
              }
              Primary key : 'player'
        """
        Job.__init__(self)
        results_db_name = 'results_pickups'
        self.results_db = tee_db[results_db_name]

        self.dependencies = ('players', 'gametypes')

    def get_dependencies(self):
        return self.dependencies

    def load_results_from_cache(self):
        res = self.results_db.find(spec={
                                        'player': self.player_name,
                                        'gametype': self.gametype,
                                        'item': self.item,
                                        },
                                   limit=1,
                                   sort=[{'date', DESCENDING}],
                                   ) 
        if res.count() > 0:
            return res[0]
        else:
            return None

    def get_results(self):
        return self.load_results_from_cache()['pickups']

    def save_results_to_cache(self):
        # Save new line only when data changes
        # Else update only the date
        last_data = self.load_results_from_cache()
        if last_data is not None and last_data['pickups'] == self.results['pickups']:
            last_data['date'] = self.results['date']
            self.results = last_data
        self.results_db.save(self.results)

    def process(self, player_name, gametype):
        self.player_name = player_name
        self.gametype = gametype
        # Change status
        self.status = 'processing'
        # Get new pickups
        for item in pickup_mapping.values():
            self.item = item
            # Get old data
            self.results = self.load_results_from_cache()
            # Set data if no history
            if self.results is None:
                self.results = {}
                self.results['player'] = self.player_name
                self.results['gametype'] = self.gametype
                self.results['pickups'] = 0
                self.results['last_event_date'] = datetime(1,1,1,0,0,0)
                self.results['item'] = self.item

            if self.gametype:
                pickups = tee_db['pickup'].find(spec={'$and': [
                                              {'item': self.item},
                                              {'player': self.player_name},
                                              {'gametype': self.gametype},
                                              {'round': { "$ne": None}},
                                              {'when': {'$gt': self.results['last_event_date']}},
                                             ]},
                                    sort=[{'when', DESCENDING}],
                                   )
            else:
                pickups = tee_db['pickup'].find(spec={'$and': [
                                              {'item': self.item},
                                              {'player': self.player_name},
                                              {'round': { "$ne": None}},
                                              {'when': {'$gt': self.results['last_event_date']}},
                                             ]},
                                    sort=[{'when', DESCENDING}],
                                   )
            # Set new pickups
            self.results['pickups'] += pickups.count()

            # Set last event date

            if pickups.count() > 0:
                self.results['last_event_date'] = pickups[0]['when']
            self.results['date'] = datetime.now()

            # Save to mongo
            self.save_results_to_cache()

        # Change status
        self.status = 'done'
