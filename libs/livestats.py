from libs.lib import live_stats_queue, econ_command_queue, get_player_stats, get_player_score
from libs.rank import get_rank, ranks
from libs.achievement import achievement_livestat_list
import threading
import Queue
import telnetlib


class LiveStats(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop = threading.Event()

    def stop_server(self):
        self.stop.set()

    def stopped(self):
        return self.stop.isSet()

    def run(self):
        timeout = 2
        round_ = None

        while not self.stopped():
            try:
                stat = live_stats_queue.get(True, 2)
            except Queue.Empty:
                continue
            if stat['type'] == 'kill':
                # Detect if is an autokill !!!
                # Check rank
                player = stat['data']['killer']
                round_ = stat['data']['round']
                if round_ is None:
                    continue
                data = {}
                data['kstats'], data['vstats'], data['pstats'] = get_player_stats(player)
                score = get_player_score(player, data)
                if score in [x[1] for x in ranks]:
                    # New rank
                    new_rank = get_rank(player, data)
                    rank_name = ranks[new_rank][0]
                    msg = """%s is now "%s" """ % (player, rank_name)
                    econ_command_queue.put({'type': 'broadcast', 'data': {'message': msg}})
                # Check achievements
                # TODO ....
                for key, achievement in achievement_livestat_list.items():
                    achievement(self, stat['data'])
#                achievement[1](player)
            if stat['type'] == 'join':
                player = stat['data']['player']
                rank = get_rank(player)
                rank_name = ranks[rank][0]
                msg = "WELCOME to the '%s' %s" % (rank_name, player)
                econ_command_queue.put({'type': 'broadcast', 'data': {'message': msg}})
