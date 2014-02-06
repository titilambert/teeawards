#!/usr/bin/python

import time
import threading
import jobs

class Job(object):
    def __init__(self):
        self.status = 'waiting'
        self.dependencies = ()

    def get_dependencies(self):
        results_db_name = 'results_CHANGEME'
        return self.dependencies

    def get_results(self):
        return []

    def load_results_from_cache(self):
        pass

    def save_results_to_cache(self):
        self.results_db.save(self.results)

    def process(self):
        pass


class StatisticatorManager(object):

    def __init__(self):
        pass


    def start(self):
        self.statisticator = Statisticator(self)
        self.statisticator.start()

    def pause(self):
        self.statisticator.pause()

    def unpause(self):
        self.statisticator.unpause()

    def stop(self):
        self.statisticator.stop_th()


class Statisticator(threading.Thread):

    def __init__(self, manager):
        threading.Thread.__init__(self)
        self.pause = False
        self.stop = threading.Event()
        self.manager = manager

    def pause(self):
        self.pause = True

    def unpause(self):
        self.pause = False

    def stop_th(self):
        self.stop.set()

    def stopped(self):
        return self.stop.isSet()

    def run(self):
        job_list = {}
        
        for job in jobs.__all__:
            #job_folder_name, job_file_name = job.split("/")
            job_name = job.split("/")[0]
            job_class_name = job_name.capitalize() + "Job"
            job_module_name = 'jobs.' + job.replace("/", ".")
            job_module = __import__(job_module_name, fromlist=True)
            # JobClass available with getattr(job_module, job_class_name)
            job_list[job_class_name] = job_module

        # TODO: Create autodiscovery dependencies between jobs
        ordered_job_list = [
                            'PlayersJob',
                            'GametypesJob',
                            'RoundsJob',
                            'Played_roundsJob',
                            'KillsJob',
                            'SuicidesJob',
                            'DeathsJob',
                            'RatiosJob',
                            'PickupsJob',
                            'Kills_by_weaponsJob',
                            'Deaths_by_weaponsJob',
                            'FlagcapturesJob',
                            'FlaggrabsJob',
                            'FlagreturnsJob',
                            'Favorite_killersJob',
                            'Favorite_victimsJob',
                            'MultikillsJob',
                            ]
        while not self.stopped():
            time.sleep(1)
            for o_job_name in ordered_job_list: 
 
                # Pause when there is at leat one player on the server
                # Add an option to desactivate it
                # Usefull for resourceless server (ei Raspi)
                while self.pause:
                    time.sleep(30)
                print o_job_name
                # Get job from dict (just to have an ordered dict ...)
                job_module = job_list[o_job_name]
                job_class_name = o_job_name
                # When we get the automatique way we could use only this next following line
                #job_class_name, job_module = job
                # Create job
                current_job = getattr(job_module, job_class_name)()
                if len(current_job.get_dependencies()) > 0:
                    ## We have to found all results data combinaisons ...
                    dep_lists = []
                    # Get all dependant results and add these to dep_lists
                    for dep in current_job.get_dependencies():
                        dep_job_class_name = dep.capitalize() + "Job"
                        dep_job_module = job_list[dep_job_class_name]
                        dep_job = getattr(dep_job_module, dep_job_class_name)()
                        dep_lists.append(dep_job.get_results())
                    # Find lists lengths
                    list_dicts = {}
                    for index, dep_list in enumerate(dep_lists):
                        list_dicts[index] = (dep_list, len(dep_list))
                    # Prepare lists for zipping
                    final_dep_list = []
                    for index, dep_list in enumerate(dep_lists):
                        multiplicators = [l[1] for k, l in list_dicts.items() if k != index]
                        multiplicator = reduce(lambda x,y: x * y, multiplicators, 1)
                        final_dep_list.append(dep_list * multiplicator)
                    # zipping lists
                    argument_lists = zip(*final_dep_list)
                    for arguments in argument_lists:
                        current_job.process(*arguments)
                else:
                    current_job.process()
            print "NEXT"


stats_mgr = StatisticatorManager()

