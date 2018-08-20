# -*- coding: utf-8 -*-
{
    'name': 'Disable about odoo',
    'summary': '',
    'version': '8.0.1.0.0',
    'category': 'Uncategorized',
    'description': """
    """,
    'website': 'http://ecosoft.co.th',
    'author': 'Tharathip C.',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'web',
    ],
    'data': [
        'security/disable_about_odoo_security.xml',
        'views/disable_about_odoo.xml',
    ],
    'qweb': [],
}
