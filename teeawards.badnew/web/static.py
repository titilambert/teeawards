import os
import hug

_DIR_PATH = os.path.dirname(os.path.realpath(__file__))


@hug.get('/css/{filename}.css', output=hug.output_format.html)
def get_css(filename, request, response):
    filepath = os.path.join(_DIR_PATH, "../static", request.path.strip("/"))
    response.set_header('Content-type', "text/css")
    with open(filepath, "r") as sfh:
        return sfh.read()


@hug.get('/images/{filename}.png', output=hug.output_format.png_image)
@hug.get('/images/card/{filename}.png', output=hug.output_format.png_image)
@hug.get('/images/decor/{filename}.png', output=hug.output_format.png_image)
@hug.get('/images/favorites/{filename}.png', output=hug.output_format.png_image)
#@hug.get('/images/other/{filename}.png', output=hug.output_format.png_image)
# TODO move badge
#@hug.get('/images/other/badge/{filename}.png', output=hug.output_format.png_image)
#@hug.get('/images/other/raw/{filename}.png', output=hug.output_format.png_image)
@hug.get('/images/ranks/{filename}.png', output=hug.output_format.png_image)
@hug.get('/images/weapon/{filename}.png', output=hug.output_format.png_image)
@hug.get('/images/weapon_set/{filename}.png', output=hug.output_format.png_image)
def get_images(filename, request, response):  # pylint: disable=W0613
    return os.path.join(_DIR_PATH, "../static/", request.path.strip("/"))
