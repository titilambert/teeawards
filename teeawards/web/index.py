import os

import hug

from teeawards.web.directives import mako_template


@hug.get('/', output=hug.output_format.html)
def api_index(request, mako_tpl:mako_template='index'):
    """
    """
    ctx = request.context['tpl_ctx']

    ctx['page'] = 'home'
    ctx['server_alive'] = ""
    ctx['fullserverstatus'] = ""
    ctx['best_killer'] = ("Nostat", 0)
    ctx['best_ratio'] = ("Nostat", 0)
    ctx['best_victim'] = ("Nostat", 0)
    ctx['best_suicider'] = ("Nostat", 0)
    ctx['best_hammer_victim'] = ("Nostat", 0)

    ctx['best_score'] = ("Nostat", 0)

    return mako_tpl.render(**ctx)
