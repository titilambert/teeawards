from datetime import datetime
from bson.code import Code

from pymongo import DESCENDING


from libs.lib import tee_db
from libs.statisticator import Job



class PlayersJob(Job):
    def __init__(self):
        """ Job to players list
              Collection name: players_results
              Struture:
                { 'players':
                    ['PLAYER_NAME',
                     'PLAYER_NAME',
                     'PLAYER_NAME',
                     'PLAYER_NAME',
                     'PLAYER_NAME',
                    ]
                  'date':
                        DATE
                }
        """
        Job.__init__(self)
        results_db_name = 'results_players'
        self.results_db = tee_db[results_db_name]

    def load_results_from_cache(self):
        res = self.results_db.find(
                                    limit=1,
                                    sort=[{'date', DESCENDING}],
                                    )
        if res.count() > 0:
            return res[0]
        else:
            return None

    def save_results_to_cache(self):
        # Save new line only when data changes
        # Else update only the date
        last_data = self.load_results_from_cache()
        if last_data is not None and last_data['players'] == self.results['players']:
            last_data['date'] = self.results['date']
            self.results = last_data
        self.results_db.save(self.results)

    def get_results(self):
        res = self.load_results_from_cache()
        if res is None:
            return []
        else:
            return self.load_results_from_cache()['players']

    def process(self):
        # Change status
        self.status = 'processing'

        # Get datas
        raw_results = tee_db['join'].aggregate([ { "$group": {"_id" : "$player"}} ])
        self.results = {}
        self.results['players'] = [player for x in raw_results['result'] for player in x.values()]
        self.results['date'] = datetime.now()

        # Save to mongo
        if len(self.results['players']) > 0:
            self.save_results_to_cache()

        # Change status
        self.status = 'done'
