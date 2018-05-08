# -*- coding: utf-8 -*-
{
    'name': 'HR Config Settings Extension',
    'version': '8.0.1.0.0',
    'author': 'Tharathip C.',
    'summary': 'Add more fields',
    'description': """
        This module add a common field \n
        Ex: company
    """,
    'category': 'Human Resources',
    'website': 'http://www.ecosoft.co.th',
    'depends': [
        'hr',
    ],
    'data': [
        'views/res_config_view.xml',
    ],
    'auto_install': False,
    'application': False,
    'installable': True,
}
