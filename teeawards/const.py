# Kill mapping
KILL_MAPPING = {
    'exit': '-3',
    'death fall': '-1',
    'hammer': '0',
    'gun': '1',
    'shotgun': '2',
    'grenade': '3',
    'laser': '4',
    'ninja': '5',
    }

R_KILL_MAPPING = dict((v, k) for k, v in KILL_MAPPING.items())

# Pickup mapping
PICKUP_MAPPING = {
    'heart': '0',
    'shield': '1',
    'shotgun': '3',
    'grenade': '2',
    'laser': '4',
    'ninja': '5',
}

R_PICKUP_MAPPING = dict((v, k) for k, v in PICKUP_MAPPING.items())

# Ranks
RANKS = [
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
