import glob
import re
import os
"""Lists all of the importable plugins"""

regexp = os.path.join(os.path.dirname(__file__), "..", 'jobs/(.*/.*)\.py')
jobs = glob.glob(os.path.join(os.path.dirname(__file__), "..", 'jobs/*/*.py'))
jobs = list([re.match(regexp, x).groups()[0] for x in jobs])

jobs = [j for j in jobs if not j.endswith('__init__')]

__all__ = jobs

