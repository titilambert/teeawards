from datetime import datetime
from bson.son import SON

from pymongo import DESCENDING

from libs.lib import tee_db
from libs.statisticator import Job


class Favorite_victimsJob(Job):
    def __init__(self):
        """ Job to get player favorite_victims
              Collection name: kill_results
              Struture:
                    {'player': STR ,
                     'favorite_victims': {
                                            'killer_name': kills,
                                            'killer_name': kills,
                                            'killer_name': kills,
                                         }
                     'gametype': STR,
                     'last_event_date': DATE ,
              }
              Primary key : 'player'
        """
        Job.__init__(self)
        results_db_name = 'results_favorite_victims'
        self.results_db = tee_db[results_db_name]

        self.dependencies = ('players', 'gametypes')

    def get_dependencies(self):
        return self.dependencies

    def load_results_from_cache(self):
        res = self.results_db.find(spec={
                                        'player': self.player_name,
                                        'gametype': self.gametype,
                                        },
                                   limit=1,
                                   sort=[{'date', DESCENDING}],
                                   ) 
        if res.count() > 0:
            return res[0]
        else:
            return None

    def get_results(self):
        return self.load_results_from_cache()['favorite_victims']

    def save_results_to_cache(self):
        # Save new line only when data changes
        # Else update only the date
        last_data = self.load_results_from_cache()
        if last_data is not None and last_data['favorite_victims'] == self.results['favorite_victims']:
            last_data['date'] = self.results['date']
            self.results = last_data
        self.results_db.save(self.results)

    def process(self, player_name, gametype):
        self.player_name = player_name
        self.gametype = gametype
        # Change status
        self.status = 'processing'
        # Get old data
        self.results = self.load_results_from_cache()
        # Set data if no history
        if self.results is None:
            self.results = {}
            self.results['player'] = self.player_name
            self.results['gametype'] = self.gametype
            self.results['favorite_victims'] = {}
            self.results['last_event_date'] = datetime(1,1,1,0,0,0)
        # Get new favorite_victims
        if self.gametype:
            favorite_victims = tee_db['kill'].aggregate([
                             {"$match": {'$and': [
                                              {'weapon': {'$in': ['0', '1', '2', '3', '4', '5']}},
                                              {'killer': self.player_name},
                                              {'victim': {"$ne": self.player_name}},
                                              {'gametype': self.gametype},
                                              {'round': { "$ne": None}},
                                              {'when': {'$gt': self.results['last_event_date']}},
                                             ]}},
                             #{"$group": {"_id": "$killer", "count":  {"$sum": 1} }},
                             {"$group": {"_id": "$victim", "count":  {"$sum": 1}, "last_event_date": {"$max": "$when"} }},
                            ])
        else:
            favorite_victims = tee_db['kill'].aggregate([
                             {"$match": {'$and': [
                                              {'weapon': {'$in': ['0', '1', '2', '3', '4', '5']}},
                                              {'killer': self.player_name},
                                              {'victim': {"$ne": self.player_name}},
                                              {'round': { "$ne": None}},
                                              {'when': {'$gt': self.results['last_event_date']}},
                                             ]}},
                             {"$group": {"_id": "$victim", "count":  {"$sum": 1}, "last_event_date": {"$max": "$when"} }},
                            ])
        # Set new favorite_victims
        for raw_result in favorite_victims['result']:
            # Initializing ...
            if not raw_result['_id'] in self.results['favorite_victims']:
                self.results['favorite_victims'][raw_result['_id']] = 0
            self.results['favorite_victims'][raw_result['_id']] += raw_result['count']

        # Set last event date
        if len(favorite_victims['result']) > 0:
            self.results['last_event_date'] = max([ x['last_event_date'] for x in favorite_victims['result'] ])
        self.results['date'] = datetime.now()

        # Save to mongo
        self.save_results_to_cache()

        # Change status
        self.status = 'done'
