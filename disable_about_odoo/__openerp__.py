# -*- coding: utf-8 -*-
{
    'name': 'Disable about odoo',
    'summary': '',
    'version': '8.0.1.0.0',
    'category': 'Uncategorized',
    'description': """
This module will disable for some menu consisted of
1. About Odoo ('Developer Mode' group only see)
2. My Odoo.com account
3. Help
    """,
    'website': 'http://ecosoft.co.th',
    'author': 'Tharathip C.',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'web',
        'mail',
        'sales_team',
    ],
    'data': [
        'security/disable_about_odoo_security.xml',
        'views/disable_about_odoo.xml',
        'views/res_user_view.xml',
    ],
    'qweb': [
        'static/src/xml/base.xml',
    ],
}
