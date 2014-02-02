from datetime import datetime
from bson.code import Code

from pymongo import DESCENDING


from libs.lib import tee_db
from libs.statisticator import Job



class GametypesJob(Job):
    def __init__(self):
        """ Job to get gametypes list
              Collection name: gametypes_results
              Struture:
                { 'gametypes':
                    ['GAMETYPE_NAME',
                     'GAMETYPE_NAME',
                     'GAMETYPE_NAME',
                     'GAMETYPE_NAME',
                    ]
                  'date':
                        DATE
                }
        """
        Job.__init__(self)
        results_db_name = 'results_gametypes'
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
        if last_data is not None and last_data['gametypes'] == self.results['gametypes']:
            last_data['date'] = self.results['date']
            self.results = last_data
        self.results_db.save(self.results)

    def get_results(self):
        # None means all gametypes
        return self.load_results_from_cache()['gametypes'] + [None]

    def process(self):
        # Change status
        self.status = 'processing'

        # Get datas
        raw_results = tee_db['round'].aggregate([ { "$group": {"_id" : "$gametype"}} ])
        self.results = {}
        self.results['gametypes'] = [player for x in raw_results['result'] for player in x.values()]
        self.results['date'] = datetime.now()

        # Save to mongo
        self.save_results_to_cache()

        # Change status
        self.status = 'done'
