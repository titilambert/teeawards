from datetime import datetime
from bson.code import Code

from pymongo import DESCENDING


from libs.lib import tee_db
from libs.statisticator import Job



class Played_roundsJob(Job):
    def __init__(self):
        """ Job to played_rounds list
              Collection name: played_rounds_results
              Struture:
                { 'played_rounds': INT,
                  'player': 'PLAYER_NAME',
                  'gametype': STR,
                  'date': DATE,
                }
        """
        Job.__init__(self)
        results_db_name = 'results_played_rounds'
        self.results_db = tee_db[results_db_name]

        self.dependencies = ('players', 'gametypes')

    def load_results_from_cache(self):
        res = self.results_db.find(
                                    spec={'player': self.player_name, 'gametype': self.gametype},
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
        if last_data is not None and last_data['played_rounds'] == self.results['played_rounds']:
            last_data['date'] = self.results['date']
            self.results = last_data
        self.results_db.save(self.results)

    def get_results(self):
        return self.load_results_from_cache()['played_rounds']

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
            self.results['played_rounds'] = 0
            self.results['last_event_date'] = datetime(1,1,1,0,0,0)

        self.results['gametype'] = self.gametype
        # Get datas
        if self.gametype:
            raw_results = tee_db['pickup'].find(spec={'$and': [
                                                        {'player': self.player_name},
                                                        {'gametype': self.gametype},
                                                        {'round': { "$ne": None}},
                                                        {'when': {'$gt': self.results['last_event_date']}},
                                                        ]
                                                },
                                          fields=['player', 'round', 'when'],
                                          sort=[{'when', DESCENDING}],
                                        )
        else:
            raw_results = tee_db['pickup'].find(spec={'$and': [
                                                        {'player': self.player_name},
                                                        {'round': { "$ne": None}},
                                                        {'when': {'$gt': self.results['last_event_date']}},
                                                        ]
                                                },
                                          fields=['player', 'round', 'when'],
                                          sort=[{'when', DESCENDING}],
                                        )
        raw_results = [(r['player'], r['round'], r['when']) for r in raw_results]

        new_nb_played_rounds = len(set([(r[0], r[1]) for r in raw_results]))
        self.results['played_rounds'] += new_nb_played_rounds

        if new_nb_played_rounds > 0:
            self.results['last_event_date'] = raw_results[0][2]
        self.results['date'] = datetime.now()

        # Save to mongo

        self.save_results_to_cache()

        # Change status
        self.status = 'done'
