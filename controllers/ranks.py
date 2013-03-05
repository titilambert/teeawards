from bottle import mako_view, request, response, redirect
from libs.lib import *
from libs import rank

@mako_view('ranks')
def ranks():
    context = {}
    context['page'] = 'ranks'
    context['ranks'] = rank.ranks

    return context

