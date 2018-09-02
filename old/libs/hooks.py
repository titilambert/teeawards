from bottle import hook, request, response

from libs.teeworldsserver import twms

def prepare_context(func):
    def wrapper(*args, **kwargs):
        # Pre-traitement
        context = {}
        session = request.environ.get('beaker.session')
        # Get gametype
        gametype = session.get('gametype', None)
        context['selected_gametype'] = gametype
        # Get server status
        context['fullserverstatus'] = twms.get_server_info()
        if context['fullserverstatus']:
            context['playernames'] = ", ".join([x['name'] for x in context['fullserverstatus']['players']])
            context['gametype'] = context['fullserverstatus']['gametype']

        # Set args
        kwargs['context'] = context
        kwargs['gametype'] = gametype
        response = func(*args, **kwargs)
        # Post-traitement
        return response

    return wrapper

