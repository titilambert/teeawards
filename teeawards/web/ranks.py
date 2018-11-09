import hug


from teeawards.const import RANKS
from teeawards.web.directives import mako_template


@hug.get('/ranks', output=hug.output_format.html)
def ladder(body=None, request=None, mako_tpl:mako_template='ranks'):
    ctx = request.context['tpl_ctx']

    ctx = {}
    ctx['page'] = 'ranks'
    ctx['ranks'] = RANKS

    return mako_tpl.render(**ctx)
