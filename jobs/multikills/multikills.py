from datetime import datetime

from pymongo import DESCENDING

from libs.lib import tee_db
from libs.statisticator import Job


class MultikillsJob(Job):
    def __init__(self):
        """ Job to get player multikills
              Collection name: kill_results
              Struture:
                    {'player': STR ,
                     'multikills': INT ,
                     'gametype': STR,
                     'last_event_date': DATE ,
              }
              Primary key : 'player'
        """
        Job.__init__(self)
        results_db_name = 'results_multikills'
        self.results_db = tee_db[results_db_name]

        self.dependencies = ('players', 'gametypes', 'rounds')

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
        return self.load_results_from_cache()['multikills']

    def save_results_to_cache(self):
        # Save new line only when data changes
        # Else update only the date
        last_data = self.load_results_from_cache()
        if last_data is not None and last_data['multikills'] == self.results['multikills']:
            last_data['date'] = self.results['date']
            self.results = last_data
        self.results_db.save(self.results)

    def process(self, player_name, gametype, round_):
        if gametype != round_['gametype']:
            return
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
            self.results['multikills'] = {}
            self.results['last_event_date'] = datetime(1,1,1,0,0,0)
        # Get new multikills
        if self.gametype:
            multikills = tee_db['kill'].find(spec={
"$or": [{ 
        '$and': [
                 {'weapon': {'$in': ['0', '1', '2', '3', '4', '5']}},
                 {'killer': self.player_name},
                 {'gametype': self.gametype},
                 {"$where": "this.killer != this.victim"},
# TODO: DELETE WHEN THE LOG DBS ARE UPTODATE
#                                              {"$where": "this.killer_team != this.victim_team"},
#                                              {"killer_team": {"$ne": None}},
                 {'round': round_['_id']},
                 {'when': {'$gt': self.results['last_event_date']}},
                 ]},
        {'$and': [
                 {'weapon': {'$in': ['0', '1', '2', '3', '4', '5']}},
                 {'victim': self.player_name},
                 {'gametype': self.gametype},
                 {'round': round_['_id']},
                 {'when': {'$gt': self.results['last_event_date']}},
                ]},
       ]
    },
    sort=[{'when', DESCENDING}],
    )
        else:
            multikills = tee_db['kill'].find(spec={'$and': [
                                              {'weapon': {'$in': ['0', '1', '2', '3', '4', '5']}},
                                              {'killer': self.player_name},
                                              {"$where": "this.killer != this.victim"},
# TODO: DELETE WHEN THE LOG DBS ARE UPTODATE
#                                              {"$where": "this.killer_team != this.victim_team"},
#                                              {"killer_team": {"$ne": None}},
                                              {'round': round_['_id']},
                                              {'when': {'$gt': self.results['last_event_date']}},
                                             ]},
                                    sort=[{'when', DESCENDING}],
                                   )
        kills_in_row = 0
        for event in multikills:
            "FIND MULTIKILL HERE !!!"
            if event['victim'] == self.player_name:
                print "MULTIKILL ENDED"
                if kills_in_row < min(multikill_list.keys()):
                    # This is not a multikill ( < 3 )
                    pass
                elif kills_in_row in multikill_list:
                    if not kill_in_row in self.results['multikills']:
                        self.results['multikills'][kills_in_row] = 0
                    self.results['multikills'][kills_in_row] += 1
                else:
                    print "MULTIKILL NOT IN THE MULTIKILL LIST ??? %s" % kills_in_row
                kills_in_row= 0
            elif event['killer'] == self.player_name:
                kills_in_row += 1
        import pdb;pdb.set_trace()
        # Set new multikills
        self.results['multikills'] += multikills.count()

        # Set last event date

        if multikills.count() > 0:
            self.results['last_event_date'] = multikills[0]['when']
        self.results['date'] = datetime.now()

        # Save to mongo
        self.save_results_to_cache()

        # Change status
        self.status = 'done'
        if self.results['multikills'] != 0:
            sdg
