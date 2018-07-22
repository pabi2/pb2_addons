# -*- coding: utf-8 -*-
{
    'name': 'PABI :: Security Management',
    'summary': '',
    'version': '8.0.1.0.0',
    'category': 'Tools',
    'description': """
This module allow easy management of security for each user.
    """,
    'website': 'https://ecosoft.co.th/',
    'author': 'Kitti U.',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'meta_groups',
        'pabi_utils',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/pabi_security_view.xml',
    ],
}
