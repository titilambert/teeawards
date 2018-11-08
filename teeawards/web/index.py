import os

import hug

from teeawards.web.directives import mako_template
from teeawards.libs.stats import get_best_killer, get_best_ratio, get_best_victim, get_best_suicider, get_best_hammer_victim, get_best_score

@hug.get('/', output=hug.output_format.html)
@hug.get('/home', output=hug.output_format.html)
def api_index(request, mako_tpl:mako_template='index'):
    """
    """
    ctx = request.context['tpl_ctx']

    ctx['page'] = 'home'
    ctx['server_alive'] = ""
    ctx['fullserverstatus'] = ""


    influx_client = request.context['influx_client']          
    # Get best killer
    best_killer = get_best_killer(influx_client)
    if best_killer:
        ctx['best_killer'] = best_killer
    else:
       ctx['best_killer'] = ("Nostat", 0)

    # Get best ratio
    best_ratio = get_best_ratio(influx_client)
    if best_ratio:
       ctx['best_ratio'] = best_ratio
    else:
       ctx['best_ratio'] = ("Nostat", 0)
    
    # Get best victim
    best_victim =  get_best_victim(influx_client)
    if best_victim:
        ctx['best_victim'] = best_victim
    else:
       ctx['best_victim'] = ("Nostat", 0)

    # Get best suicider
    best_suicider = get_best_suicider(influx_client)
    if best_suicider:
        ctx['best_suicider'] = best_suicider
    else:
       ctx['best_suicider'] = ("Nostat", 0)

    # Get hammer lover
    best_hammer_victim = get_best_hammer_victim(influx_client)
    if best_hammer_victim:
        ctx['best_hammer_victim'] = best_hammer_victim
    else:
       ctx['best_hammer_victim'] = ("Nostat", 0)

    # Get best score
    #TODO complete this with CTF and round scores
    best_score = get_best_score(influx_client)
    if best_score:
        ctx['best_score'] = best_score
    else:
        ctx['best_score'] = ("Nostat", 0)
    

    return mako_tpl.render(**ctx)


@hug.post('/set_gametype')
def set_gametype(body, request, response):
    # FIXME not working
    print(request.cookies)
#    import ipdb;ipdb.set_trace()
    response.set_cookie('gametype', body['gametype'])
    hug.redirect.found('/')
