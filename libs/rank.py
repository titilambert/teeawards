from libs.lib import *

def get_rank(player, data=None):
    score = get_player_score(player, data)
    player_rank = 0
    for i, rank in enumerate(ranks):
        if score < rank[1]:
            break
        player_rank = i
    return player_rank


ranks = [
        ('Private', 0),
        ('Private First Class', 40),
        ('Lance Corporal', 100),
        ('Corporal', 250),
        ('Sergeant', 500),
        ('Staff Sergeant', 1000),
        ('Gunnery Sergeant', 2000),
        ('Master Sergeant', 4000),
        ('First Sergeant', 6500),
        ('Master Gunnery Sergeant', 10000),
        ('Sergeant Major', 15000),
        ('Sergeant Major of the Corps', 20000),
        ('2nd Lieutenant', 30000),
        ('1st Lieutenant', 40000),
        ('Captain', 50000),
        ('Major', 65000),
        ('Lieutenant Colonel', 80000),
        ('Colonel', 100000),
        ('Brigadier General', 125000),
        ('Major General', 150000),
        ('Lieutenant General', 175000),
        ('General', 200000),
    ]
