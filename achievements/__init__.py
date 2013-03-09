import glob
import re
"""Lists all of the importable plugins"""

achievements = glob.glob('achievements/*/*.py')
achievements = list([re.match('achievements/*/(.*).py', x).groups()[0] for x in achievements])
for i, f in enumerate(achievements):
    if f.endswith('/__init__'):
        del(achievements[i])

print achievements
__all__ = achievements
