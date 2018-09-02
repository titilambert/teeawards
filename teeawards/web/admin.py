
import os
import hug
from falcon import HTTP_404


from teeawards.web.directives import mako_template


@hug.get('/admin', output=hug.output_format.html)
def api_index(request, mako_tpl:mako_template='admin'):
    """
    """
    ctx = request.context['tpl_ctx']


    return mako_tpl.render(**ctx)
