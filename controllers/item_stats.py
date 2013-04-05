from bottle import mako_view, request, response, redirect
from libs.lib import *
from libs.teeworldsserver import twms

@mako_view('item_stats')
def item_stats():
    context = {}
    #if not item in kill_mapping.keys() + pickup_mapping.keys():
    #    return "bad item"

    context['page'] = 'items'
    context['items'] = []
    context['fullserverstatus'] = twms.get_server_info()
    if context['fullserverstatus']:
        context['playernames'] = ", ".join([x['name'] for x in context['fullserverstatus']['players']])
        context['gametype'] = context['fullserverstatus']['gametype']


    context['itemlist'] = ['heart', 'shield', 'hammer', 'gun', 
             'shotgun', 'grenade', 'laser', 'ninja',]
    for item in context['itemlist']:
        context['items'].append(get_item_stats(item))
    return context

