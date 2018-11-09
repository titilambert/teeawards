from io import StringIO

from influxdb import InfluxDBClient
from mako.runtime import Context
import hug
from hug.middleware import SessionMiddleware
from hug.store import InMemoryStore


from teeawards.logger import http_logger
#from teeawards.web import index, static, admin, conf, map
from teeawards.web import index, static, admin, maps, ladder, items, ranks, achievements, player_stats
#from teeawards.server.conf import ConfigManager
#from teeawards.server.map import MapManager
from teeawards.libs.teeworldsserver import TeeWorldsServerManager
#from teeawards.server.econ import EconClient


@hug.extend_api('')
def with_other_apis():
    """Load all API views."""
    #return [index, static, admin, conf, map]
    return [index, static, admin, maps, ladder, items, ranks, achievements, player_stats]


def main():
    """Senoapi entrypoint function."""
    influx_client = InfluxDBClient('localhost', 8086, 'root', 'root', 'teeawards')
    influx_client.create_database('teeawards')

#    config_manager = ConfigManager()
#    map_manager = MapManager()
#    econ_client = EconClient()
#    econ_client.start()
#    server_manager = TeeWorldsServerManager(config_manager, econ_client, influx_client)
    twsm = TeeWorldsServerManager(influx_client)

    @hug.request_middleware()
    def create_context(request, response):  # pylint: disable=W0613,W0612
        """Add context element to the request object."""
        request.context['influx_client'] = influx_client
        request.context['tpl_ctx'] = {}
#        request.context['cfg_mgr'] = config_manager
#        request.context['map_mgr'] = map_manager
        request.context['tpl_dir'] = 'teeawards/views'
        request.context['tpl_name'] = None
        request.context['twsm'] = twsm
#        request.context['tpl_ctx']['fullserverstatus'] = request.context['server_mgr'].get_server_info()

    # TODO add port
    api = hug.API(__name__)
    # FIXME cookies/session not working
    session_store = InMemoryStore()
    middleware = SessionMiddleware(session_store, cookie_name='teeawards')
    api.http.add_middleware(middleware)

    host = ''
    port = 8080
    http_logger.info("Start HTTP server")

    api.http.serve(host=host, port=port)


if __name__ == "__main__":
    main()
