#!/usr/bin/python
import sys
import time
import signal

import bottle
from bottle import Bottle, run, mako_template, TEMPLATE_PATH
from bottle import static_file, route

from controllers.index import index
from controllers.ladder import ladder
from controllers.item_stats import item_stats
from controllers.player_stats import player_stats
from controllers.ranks import ranks
from controllers.admin import admin, conf_edit, conf_delete, map_edit, map_delete
from controllers.achievements import achievements
from controllers.maps import maps
from libs.teeworldsserver import twms

def server_css(filepath):
    return static_file(filepath, root='static/css/')

def server_images(filepath):
    return static_file(filepath, root='static/images/')

def server_map_screenshots(filepath):
    return static_file(filepath, root='server_data/map_screenshots/')

def server_js(filepath):
    return static_file(filepath, root='static/js/')

def setup_routing(app):
#    app.route('/edit', method=['GET', 'POST'], callback=form_edit)
    app.route('/', method=['GET', 'POST'], callback=index)
    app.route('/home', method=['GET', 'POST'], callback=index)
    app.route('/index', method=['GET', 'POST'], callback=index)
    app.route('/ladder', method=['GET', 'POST'], callback=ladder)
    app.route('/ranks', method=['GET', 'POST'], callback=ranks)
    app.route('/maps', method=['GET', 'POST'], callback=maps)
    app.route('/map/<id>', method=['GET', 'POST'], callback=maps)
    app.route('/admin/map/edit', method=['GET', 'POST'], callback=map_edit)
    app.route('/admin/map/edit/', method=['GET', 'POST'], callback=map_edit)
    app.route('/admin/map/edit/<id_>', method=['GET', 'POST'], callback=map_edit)
    app.route('/admin/map/delete/<id_>', method=['GET', 'POST'], callback=map_delete)
    app.route('/admin', method=['GET', 'POST'], callback=admin)
    app.route('/achievements', method=['GET', 'POST'], callback=achievements)
    app.route('/admin/<action>', method=['GET', 'POST'], callback=admin)
#    app.route('/admin/conf/<id>', method=['GET', 'POST'], callback=admin)
    app.route('/admin/conf/edit', method=['GET', 'POST'], callback=conf_edit)
    app.route('/admin/conf/edit/', method=['GET', 'POST'], callback=conf_edit)
    app.route('/admin/conf/edit/<id_>', method=['GET', 'POST'], callback=conf_edit)
    app.route('/admin/conf/delete/<id_>', method=['GET', 'POST'], callback=conf_delete)
    app.route('/ladder/<sort>', method=['GET', 'POST'], callback=ladder)
    app.route('/items', method=['GET', 'POST'], callback=item_stats)
    app.route('/player_stats/<player>', method=['GET'], callback=player_stats)
    app.route('/player_stats', method=['POST'], callback=player_stats)
    app.route('/css/:filepath#.+#', method=['GET', 'POST'], callback=server_css)
    app.route('/images/:filepath#.+#', method=['GET', 'POST'], callback=server_images)
    app.route('/js/:filepath#.+#', method=['GET', 'POST'], callback=server_js)
    app.route('/map_screenshots/:filepath#.+#', method=['GET', 'POST'], callback=server_map_screenshots)


app = Bottle()

setup_routing(app)

def signal_handler(signal, frame):
        print 'You pressed Ctrl+C!'
        if twms.stop():
            print 'Please waiting... The teeworlds server is stopping !'
            time.sleep(3)
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

run(app, host='0.0.0.0', port=8081)

