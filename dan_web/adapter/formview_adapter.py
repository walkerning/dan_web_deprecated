# -*- coding: utf-8 -*-
"""
根据工具类型, 渲染所需表单"""

from __future__ import unicode_literals
import os

from jinja2 import Environment, PackageLoader, Template

here = os.path.dirname(os.path.abspath(__file__))

basic_form_group_template = Template("""
<div class="form-group" name="{{ ARG_NAME }}" {{ addition_info }}>
{{ form_group_content }}
</div>
""")

class FormViewAdapter(object):
    def __init__(self, app, templates_dir='templates'):
        if hasattr(app, 'config') and 'APP_NAME' in app.config:
            self.name = app.config['APP_NAME']
        else:
            self.name = app
        self.env = Environment(loader=PackageLoader(self.name, templates_dir))

    def render_js(self, arg_dict):
        """
        Render a js."""
        js_list = []

        for arg_name, render_conf in arg_dict.iteritems():
            # fixme: 如果找不到template的错误处理
            try:
                template = self.env.get_template(render_conf['template'] + '.js')
            except Exception:
                continue
            js_list.append(template.render(ARG_NAME=arg_name,
                                           **render_conf['template_args']))

        return '\n'.join(js_list)
        
    def render_form(self, arg_dict, addition_info='', required=False):
        """
        Render a argument form."""

        form_group_list = []

        for arg_name, render_conf in arg_dict.iteritems():
            # fixme: 如果找不到template的错误处理
            template = self.env.get_template(render_conf['template'] + '.html')
            form_group_list.append(basic_form_group_template.render(ARG_NAME=arg_name, addition_info=addition_info, form_group_content=template.render(ARG_NAME=arg_name, REQUIRED='required' if required else '', **render_conf['template_args'])))

        return '\n'.join(form_group_list)
