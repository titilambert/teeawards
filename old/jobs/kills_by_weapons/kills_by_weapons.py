from datetime import datetime

from pymongo import DESCENDING

from libs.lib import tee_db, kill_mapping
from libs.statisticator import Job


class Kills_by_weaponsJob(Job):
    def __init__(self):
        """ Job to get player kills_by_weapons
              Collection name: kills_by_weapons_results
              Struture:
                    {'player': STR ,
                     'kills_by_weapons': INT ,
                     'weapon': INT ,
                     'gametype': STR,
                     'last_event_date': DATE ,
              }
              Primary key : 'player'
        """
        Job.__init__(self)
        results_db_name = 'results_kills_by_weapons'
        self.results_db = tee_db[results_db_name]

        self.dependencies = ('players', 'gametypes')

    def get_dependencies(self):
        return self.dependencies

    def load_results_from_cache(self):
        res = self.results_db.find(spec={
                                        'player': self.player_name,
                                        'gametype': self.gametype,
                                        'weapon': self.weapon,
                                        },
                                   limit=1,
                                   sort=[{'date', DESCENDING}],
                                   ) 
        if res.count() > 0:
            return res[0]
        else:
            return None

    def get_results(self):
        return self.load_results_from_cache()['kills_by_weapons']

    def save_results_to_cache(self):
        # Save new line only when data changes
        # Else update only the date
        last_data = self.load_results_from_cache()
        if last_data is not None and last_data['kills_by_weapons'] == self.results['kills_by_weapons']:
            last_data['date'] = self.results['date']
            self.results = last_data
        self.results_db.save(self.results)

    def process(self, player_name, gametype):
        self.player_name = player_name
        self.gametype = gametype
        # Change status
        self.status = 'processing'
        # Get new kills_by_weapons
        for weapon in kill_mapping.values():
            self.weapon = weapon
            # Get old data
            self.results = self.load_results_from_cache()
            # Set data if no history
            if self.results is None:
                self.results = {}
                self.results['player'] = self.player_name
                self.results['gametype'] = self.gametype
                self.results['kills_by_weapons'] = 0
                self.results['last_event_date'] = datetime(1,1,1,0,0,0)
                self.results['weapon'] = self.weapon
            # Get new kills
            if self.gametype:
                kills_by_weapons = tee_db['kill'].find(spec={'$and': [
                                                  {'weapon': self.weapon},
                                                  {'killer': self.player_name},
                                                  {'gametype': self.gametype},
                                                  {"$where": "this.killer != this.victim"},
                                              # "this.killer_team != this.victim_team" bad condition in non TEAM gametype
                                                  {"$where": "this.killer_team != this.victim_team"},
                                                  {"killer_team": {"$ne": None}},
                                                  {'round': { "$ne": None}},
                                                  {'when': {'$gt': self.results['last_event_date']}},
                                                 ]},
                                        sort=[{'when', DESCENDING}],
                                       )
            else:
                kills_by_weapons = tee_db['kill'].find(spec={'$and': [
                                                  {'weapon': self.weapon},
                                                  {'killer': self.player_name},
                                                  {"$where": "this.killer != this.victim"},
                                              # "this.killer_team != this.victim_team" bad condition in non TEAM gametype
                                                  {"$where": "this.killer_team != this.victim_team"},
                                                  {"killer_team": {"$ne": None}},
                                                  {'round': { "$ne": None}},
                                                  {'when': {'$gt': self.results['last_event_date']}},
                                                 ]},
                                        sort=[{'when', DESCENDING}],
                                        )

            # Set new kills_by_weapons
            self.results['kills_by_weapons'] += kills_by_weapons.count()

            # Set last event date

            if kills_by_weapons.count() > 0:
                self.results['last_event_date'] = kills_by_weapons[0]['when']
            self.results['date'] = datetime.now()

            # Save to mongo
            self.save_results_to_cache()

        # Change status
        self.status = 'done'
