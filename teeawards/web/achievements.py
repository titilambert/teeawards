import os

import hug

from teeawards.web.directives import mako_template


@hug.get('/achievements', output=hug.output_format.html)
def achievements(request=None, mako_tpl:mako_template='achievements'):
    ctx = request.context['tpl_ctx']
    ctx['page'] = 'achievements'

    ctx['achievement_desc_list'] = {}

    for name, fct in achievement_desc_list.items():
        ctx['achievement_desc_list'][name] = fct()

    return mako_tpl.render(**ctx)
