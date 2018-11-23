import os

import hug

from teeawards.web.directives import mako_template
from teeawards.achievements import achievement_desc_list


_DIR_PATH = os.path.dirname(os.path.realpath(__file__))


@hug.get('/achievements', output=hug.output_format.html)
def achievements(request=None, mako_tpl:mako_template='achievements'):
    ctx = request.context['tpl_ctx']
    ctx['page'] = 'achievements'

    ctx['achievement_desc_list'] = {}

    for name, fct in achievement_desc_list.items():
        ctx['achievement_desc_list'][name] = fct()

    return mako_tpl.render(**ctx)


@hug.get('/images/achievements/{achievement}/{filename}', output=hug.output_format.png_image)
def get_schievements_images(achievement, filename, request):
    return os.path.join(_DIR_PATH, "..", "achievements", achievement, "static", "images", filename)


@hug.get('/css/achievements/{achievement}/{filename}', output=hug.output_format.html)
def get_schievements_css(achievement, filename, response, request):
    filepath = os.path.join(_DIR_PATH, "..", "achievements", achievement, "static", "css", filename)
    response.set_header('Content-type', "text/css")
    with open(filepath, "r") as sfh:
        return sfh.read()

