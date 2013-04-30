import glob
import re
import os
"""Lists all of the importable plugins"""

regexp = os.path.join(os.path.dirname(__file__), "..", 'achievements/(.*/.*)\.py')
achievements = glob.glob(os.path.join(os.path.dirname(__file__), "..", 'achievements/*/*.py'))
achievements = list([re.match(regexp, x).groups()[0] for x in achievements])

achievements = [a for a in achievements if not a.endswith('__init__')]

__all__ = achievements
