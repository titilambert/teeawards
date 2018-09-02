from datetime import datetime

from pymongo import DESCENDING

from libs.lib import tee_db
from libs.lib import team_gametypes
from libs.statisticator import Job


class KillsJob(Job):
    def __init__(self):
        """ Job to get player kills
              Collection name: kill_results
              Struture:
                    {'player': STR ,
                     'kills': INT ,
                     'gametype': STR,
                     'last_event_date': DATE ,
              }
              Primary key : 'player'
        """
        Job.__init__(self)
        results_db_name = 'results_kills'
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
        res = self.load_results_from_cache()
        if res is None:
            return []
        else:
            return res['kills']

    def save_results_to_cache(self):
        # Save new line only when data changes
        # Else update only the date
        last_data = self.load_results_from_cache()
        if last_data is not None and last_data['kills'] == self.results['kills']:
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
            self.results['kills'] = 0
            self.results['last_event_date'] = datetime(1,1,1,0,0,0)
        # Get new kills
        if self.gametype:
            kills = tee_db['kill'].find(spec={'$and': [
                                              {'weapon': {'$in': ['0', '1', '2', '3', '4', '5']}},
                                              {'killer': self.player_name},
                                              {'gametype': self.gametype},
                                              {"$where": "this.killer != this.victim"},
                                              {'$or': [{'$and': [
                                                                {'gametypes': {"$in": team_gametypes}},
                                                                {"$where": "this.killer_team != this.victim_team"},
                                                               ]},
                                                       {'gametypes': {"$ne": {"$in": team_gametypes}}},
                                                       ]},
                                              {"killer_team": {"$ne": None}},
                                              {'round': { "$ne": None}},
                                              {'when': {'$gt': self.results['last_event_date']}},
                                             ]},
                                    sort=[{'when', DESCENDING}],
                                   )
        else:
            kills = tee_db['kill'].find(spec={'$and': [
                                              {'weapon': {'$in': ['0', '1', '2', '3', '4', '5']}},
                                              {'killer': self.player_name},
                                              # "this.killer_team != this.victim_team" bad condition in non TEAM gametype
                                              {"$where": "this.killer != this.victim"},
                                              {'$or': [{'$and': [
                                                                {'gametypes': {"$in": team_gametypes}},
                                                                {"$where": "this.killer_team != this.victim_team"},
                                                               ]},
                                                       {'gametypes': {"$ne": {"$in": team_gametypes}}},
                                                       ]},
                                              {"killer_team": {"$ne": None}},
                                              {'round': { "$ne": None}},
                                              {'when': {'$gt': self.results['last_event_date']}},
                                             ]},
                                    sort=[{'when', DESCENDING}],
                                   )
        # Set new kills
        self.results['kills'] += kills.count()

        # Set last event date

        if kills.count() > 0:
            self.results['last_event_date'] = kills[0]['when']
        self.results['date'] = datetime.now()

        # Save to mongo
        self.save_results_to_cache()

        # Change status
        self.status = 'done'
