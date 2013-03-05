from bottle import mako_view, request, response, redirect
from libs.lib import *

@mako_view('item_stats')
def item_stats():
    context = {}
    #if not item in kill_mapping.keys() + pickup_mapping.keys():
    #    return "bad item"

    context['items'] = []
    context['itemlist'] = ['hearth', 'shield', 'gun', 'hammer', 
             'shutgun', 'grenade', 'laser', 'ninja',]
    for item in context['itemlist']:
        context['items'].append(get_item_stats(item))
    return context

