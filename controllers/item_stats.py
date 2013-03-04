from bottle import mako_view, request, response, redirect
from libs.lib import *

@mako_view('item_stats')
def item_stats(item):
    context = {}
    item = item.lower()
    if not item in kill_mapping.keys() + pickup_mapping.keys():
        return "bad item"

    context['item'] = item
    context['stats'] = get_item_stats(item)
    return context

