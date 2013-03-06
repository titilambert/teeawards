from bottle import mako_view, request, response, redirect
from libs.lib import *
from libs.rank import get_rank
from libs.teeworldsserver import twms
from time import sleep

@mako_view('admin')
def admin():
    context = {}
    context['page'] = 'admin'
    context['server_alive'] = twms.is_alive()

    if request.method == 'POST':
        req = request.params['toggle_server']
        if req == 'start':
            twms.start()
            redirect("/admin") 
        if req == 'stop':
            twms.stop()
	    sleep(2)
            redirect("/admin") 

    return context
