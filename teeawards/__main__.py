from io import StringIO

from influxdb import InfluxDBClient
from mako.runtime import Context
import hug


from teeawards.logger import http_logger
from teeawards.web import index, static, admin


@hug.extend_api('')
def with_other_apis():
    """Load all API views."""
    return [index, static, admin]



def main():
    """Senoapi entrypoint function."""
    client = InfluxDBClient('localhost', 8086, 'root', 'root', 'example')
    @hug.request_middleware()
    def create_context(request, response):  # pylint: disable=W0613,W0612
        """Add context element to the request object."""
        request.context['db_client'] = client
        buf = StringIO()
        request.context['tpl_ctx'] = {}
        request.context['tpl_dir'] = 'teeawards/views'
        request.context['tpl_name'] = None

    # TODO add port
    api = hug.API(__name__)

    host = ''
    port = 8080
    http_logger.info("Start HTTP server")

    api.http.serve(host=host, port=port)


if __name__ == "__main__":
    main()
