import os

from mako.template import Template
from mako.lookup import TemplateLookup
import hug


@hug.directive()
def mako_template(template_name, request=None, **kwargs):
    __slots__ = ('template_folder', )

    _mylookup = TemplateLookup(directories=['.'])
    template_folder = request.context['tpl_dir']
    template_path = os.path.join(template_folder, template_name + '.tpl')
    template = Template(filename=template_path, lookup=_mylookup)
    return template
