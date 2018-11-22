from queue import Queue
import os

from pymongo import MongoClient

con = MongoClient()
tee_db = con['teeworlds']
econ_port = 9999

# cache timeout (seconds)
cache_timeout = 60
cache_timeout = 0

# Queues
## live stats
live_stats_queue = Queue()
econ_command_queue = Queue()

# CONFIG TABLES DONT EMPTY IT !!!
conf_table = tee_db['config']
maps_table = tee_db['maps']



data_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "server_data"))
