from datetime import datetime

from pymongo import DESCENDING

from libs.lib import tee_db
from libs.statisticator import Job


class FlagreturnsJob(Job):
    def __init__(self):
        """ Job to get player flagreturns
              Collection name: results_flagreturns
              Struture:
                    {'player': STR ,
                     'flagreturns': INT ,
                     'gametype': STR,
                     'last_event_date': DATE ,
              }
              Primary key : 'player'
        """
        Job.__init__(self)
        results_db_name = 'results_flagreturns'
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
        return self.load_results_from_cache()['flagreturns']

    def save_results_to_cache(self):
        # Save new line only when data changes
        # Else update only the date
        last_data = self.load_results_from_cache()
        if last_data is not None and last_data['flagreturns'] == self.results['flagreturns']:
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
            self.results['flagreturns'] = 0
            self.results['last_event_date'] = datetime(1,1,1,0,0,0)
        # Get new flagreturns
        if self.gametype:
            flagreturns = tee_db['flagcapture'].find(spec={'$and': [
                                              {'player': self.player_name},
                                              {'gametype': self.gametype},
                                              {'round': { "$ne": None}},
                                              {'when': {'$gt': self.results['last_event_date']}},
                                             ]},
                                    sort=[{'when', DESCENDING}],
                                   )
        else:
            flagreturns = tee_db['flagcapture'].find(spec={'$and': [
                                              {'player': self.player_name},
                                              {'round': { "$ne": None}},
                                              {'when': {'$gt': self.results['last_event_date']}},
                                             ]},
                                    sort=[{'when', DESCENDING}],
                                   )
        # Set new flagreturns
        self.results['flagreturns'] += flagreturns.count()

        # Set last event date

        if flagreturns.count() > 0:
            self.results['last_event_date'] = flagreturns[0]['when']
        self.results['date'] = datetime.now()

        # Save to mongo
        self.save_results_to_cache()

        # Change status
        self.status = 'done'
