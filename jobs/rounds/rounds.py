from datetime import datetime
from bson.code import Code

from pymongo import DESCENDING


from libs.lib import tee_db
from libs.statisticator import Job



class RoundsJob(Job):
    def __init__(self):
        """ Job to rounds list
              Collection name: rounds_results
              Struture:
                { 'rounds':
                    ['ROUND_ID,
                     'ROUND_ID,
                     'ROUND_ID,
                     'ROUND_ID,
                     'ROUND_ID,
                    ]
                  'date':
                        DATE
                }
        """
        Job.__init__(self)
        results_db_name = 'results_rounds'
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
        if last_data is not None and last_data['rounds'] == self.results['rounds']:
            last_data['date'] = self.results['date']
            self.results = last_data
        self.results_db.save(self.results)

    def get_results(self):
        return self.load_results_from_cache()['rounds']

    def process(self):
        # Change status
        self.status = 'processing'
        self.results = {}
        # Get datas
        raw_results = tee_db['round'].find()
        round_list = []
        for round_ in raw_results:
            map_ = tee_db['map'].find({"_id": round_['map']})
            if map_.count() != 1:
                print "ERRRROR MAP searching in ROUND MAP"
                return
            round_['map'] = map_[0]['map'] 
            round_list.append(round_)

        self.results['date'] = datetime.now()
        self.results['rounds'] = round_list

        # Save to mongo
        self.save_results_to_cache()

        # Change status
        self.status = 'done'
