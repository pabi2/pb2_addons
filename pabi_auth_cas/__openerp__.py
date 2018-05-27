# -*- coding: utf-8 -*-
{
    'name': "NSTDA-BASE :: Authentication CAS",
    'description': """NSTDA CAS Authentication""",
    'author': 'Jakkrich.cha',
    'category': 'NSTDA-BASE',
    'depends': ['base', 'base_setup', 'web'],
    'data': [
            'static/src/views/auth_cas.xml',
            'res_config_view.xml',
            'ir_ui_menu_view.xml'
    ],
    'qweb': [
        "static/src/xml/auth_cas.xml"
    ],
    'installable': True,
    'external_dependencies': {
        'python': ['ldap'],
    }
}
