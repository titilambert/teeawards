from bottle import Bottle, run, mako_template, TEMPLATE_PATH
from bottle import static_file, route
import bottle

from controllers.index import index
from controllers.ladder import ladder
from controllers.item_stats import item_stats
from controllers.player_stats import player_stats

def server_css(filepath):
    return static_file(filepath, root='static/css/')

def server_images(filepath):
    return static_file(filepath, root='static/images/')

def server_js(filepath):
    return static_file(filepath, root='static/js/')

def setup_routing(app):
#    app.route('/edit', method=['GET', 'POST'], callback=form_edit)
    app.route('/', method=['GET', 'POST'], callback=index)
    app.route('/home', method=['GET', 'POST'], callback=index)
    app.route('/index', method=['GET', 'POST'], callback=index)
    app.route('/ladder', method=['GET', 'POST'], callback=ladder)
    app.route('/ladder/<sort>', method=['GET', 'POST'], callback=ladder)
    app.route('/item_stats/<item>', method=['GET', 'POST'], callback=item_stats)
    app.route('/player_stats/<player>', method=['GET'], callback=player_stats)
    app.route('/player_stats', method=['POST'], callback=player_stats)
    app.route('/css/:filepath#.+#', method=['GET', 'POST'], callback=server_css)
    app.route('/images/:filepath#.+#', method=['GET', 'POST'], callback=server_images)
    app.route('/js/:filepath#.+#', method=['GET', 'POST'], callback=server_js)


app = Bottle()

setup_routing(app)


run(app, host='0.0.0.0', port=8081)

