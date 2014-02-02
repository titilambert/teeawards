from datetime import datetime

from pymongo import DESCENDING

from libs.lib import tee_db
from libs.statisticator import Job


class RatiosJob(Job):
    def __init__(self):
        """ Job to get player ratios
              Collection name: death_results
              Struture:
                    {'player': STR ,
                     'ratios': INT ,
                     'gametype': STR,
                     'date': DATE ,
              }
              Primary key : 'player'
        """
        Job.__init__(self)
        results_db_name = 'results_ratios'
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
        return self.load_results_from_cache()['ratios']

    def save_results_to_cache(self):
        # Save new line only when data changes
        # Else update only the date
        last_data = self.load_results_from_cache()
        if last_data is not None and last_data['ratios'] == self.results['ratios']:
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
            self.results['ratios'] = 0
            self.results['date'] = datetime(1,1,1,0,0,0)
        # Get kills results
        kills = tee_db['results_kills'].find(spec={'$and': [
                                                            {'gametype': self.gametype},
                                                            {'player': self.player_name},
                                                           ]
                                                   },
                                             limit=1,
                                             sort=[{'when', DESCENDING}],
                                            )
        if kills.count() != 1:
            # TODO: Handle it
            print "ERROR !!!!!!!!!"
            return
        nb_kill = kills[0]['kills']
        # Get Deaths results
        deaths = tee_db['results_deaths'].find(spec={'$and': [
                                                            {'gametype': self.gametype},
                                                            {'player': self.player_name},
                                                           ]
                                                   },
                                             limit=1,
                                             sort=[{'when', DESCENDING}],
                                            )
        if deaths.count() != 1:
            # TODO: Handle it
            print "ERROR !!!!!!!!!"
            return
        nb_death = deaths[0]['deaths']
        # Set new ratios
        if nb_death != 0:
            self.results['ratios'] = nb_kill/float(nb_death)
        else:
            self.results['ratios'] = 0
        # Set date
        self.results['date'] = datetime.now()

        # Save to mongo
        self.save_results_to_cache()

        # Change status
        self.status = 'done'
