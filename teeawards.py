#!/usr/bin/python
import sys
import time
import signal
import glob

import bottle
from bottle import Bottle, run, mako_template, TEMPLATE_PATH
from bottle import static_file, route

from beaker.middleware import SessionMiddleware

from controllers.index import index, set_gametype
from controllers.ladder import ladder
from controllers.item_stats import item_stats
from controllers.player_stats import player_stats
from controllers.ranks import ranks
from controllers.admin import admin, conf_edit, conf_delete, map_edit, map_delete, reset_data, kick, export, restore
from controllers.achievements import achievements
from controllers.maps import maps
from libs.teeworldsserver import twms
from libs.econ import econ_client

from libs import hooks


def server_css(filepath):
    return static_file(filepath, root='static/css/')

def server_css_achievements(name, filepath):
    path = 'achievements/%s/static/css/' % name
    return static_file(filepath, root=path)

def server_images_achievements(name, filepath):
    path = 'achievements/%s/static/images/' % name
    return static_file(filepath, root=path)

def server_images(filepath):
    return static_file(filepath, root='static/images/')

def server_map_screenshots(filepath):
    return static_file(filepath, root='server_data/map_screenshots/')

def server_js(filepath):
    return static_file(filepath, root='static/js/')

def setup_routing(app):
#    bottle.route('/edit', method=['GET', 'POST'], callback=form_edit)
    bottle.route('/', method=['GET', 'POST'], callback=index)
    bottle.route('/home', method=['GET', 'POST'], callback=index)
    bottle.route('/index', method=['GET', 'POST'], callback=index)
    bottle.route('/ladder', method=['GET', 'POST'], callback=ladder)
    bottle.route('/ranks', method=['GET', 'POST'], callback=ranks)
    bottle.route('/maps', method=['GET', 'POST'], callback=maps)
    bottle.route('/maps/<gametype>', method=['GET', 'POST'], callback=maps)
    bottle.route('/map/<id>', method=['GET', 'POST'], callback=maps)
    bottle.route('/admin/map/edit', method=['GET', 'POST'], callback=map_edit)
    bottle.route('/admin/map/edit/', method=['GET', 'POST'], callback=map_edit)
    bottle.route('/admin/map/edit/<id_>', method=['GET', 'POST'], callback=map_edit)
    bottle.route('/admin/map/delete/<id_>', method=['GET', 'POST'], callback=map_delete)
    bottle.route('/admin', method=['GET', 'POST'], callback=admin)
    bottle.route('/achievements', method=['GET', 'POST'], callback=achievements)
    bottle.route('/admin/reset_data', method=['GET', 'POST'], callback=reset_data)
#    bottle.route('/admin/conf/<id>', method=['GET', 'POST'], callback=admin)
    bottle.route('/admin/conf/edit', method=['GET', 'POST'], callback=conf_edit)
    bottle.route('/admin/conf/edit/', method=['GET', 'POST'], callback=conf_edit)
    bottle.route('/admin/conf/edit/<id_>', method=['GET', 'POST'], callback=conf_edit)
    bottle.route('/admin/conf/delete/<id_>', method=['GET', 'POST'], callback=conf_delete)
    bottle.route('/admin/kick/<player>', method=['GET', 'POST'], callback=kick)
    bottle.route('/admin/export', method=['GET', 'POST'], callback=export)
    bottle.route('/admin/restore', method=['GET', 'POST'], callback=restore)
    bottle.route('/admin/<action>', method=['GET', 'POST'], callback=admin)
    bottle.route('/ladder/<sort>', method=['GET', 'POST'], callback=ladder)
    bottle.route('/items', method=['GET', 'POST'], callback=item_stats)
    bottle.route('/player_stats/<player>/<gametype>', method=['GET'], callback=player_stats)
    bottle.route('/player_stats/<player>', method=['GET'], callback=player_stats)
    bottle.route('/player_stats', method=['POST'], callback=player_stats)
    bottle.route('/css/achievements/<name>/:filepath#.+#', method=['GET', 'POST'], callback=server_css_achievements)
    bottle.route('/css/:filepath#.+#', method=['GET', 'POST'], callback=server_css)
    bottle.route('/images/achievements/<name>/:filepath#.+#', method=['GET', 'POST'], callback=server_images_achievements)
    bottle.route('/images/:filepath#.+#', method=['GET', 'POST'], callback=server_images)
    bottle.route('/js/:filepath#.+#', method=['GET', 'POST'], callback=server_js)
    bottle.route('/map_screenshots/:filepath#.+#', method=['GET', 'POST'], callback=server_map_screenshots)
    bottle.route('/set_gametype', method=['POST'], callback=set_gametype)

def signal_handler(signal, frame):
        print 'You pressed Ctrl+C!'
        econ_client.stop_server()
        if twms.stop():
            print 'Please waiting... The teeworlds server is stopping !'
            time.sleep(3)
        sys.exit(0)

def main():
    achvmts = glob.glob("achievements/*/views/")
    for a in achvmts:
        bottle.TEMPLATE_PATH.append(a)
    
    session_opts = {
        'session.type': 'file',
        'session.data_dir': './session_data',
        'session.secret': 'Ki2ho0zeeghiemie9eengaxu7zaung1aico2shee7aechei7moozumuisae1',
        'session.auto': True,
        'session.key': 'teeaward',
    }

    app = bottle.app()
    app = SessionMiddleware(app, session_opts)
    setup_routing(app)
    signal.signal(signal.SIGINT, signal_handler)
    sys.stderr = open('teeawards.log', 'a')
    run(app, host='0.0.0.0', port=8081)

if __name__ == '__main__':
    main()
