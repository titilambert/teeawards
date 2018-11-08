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
