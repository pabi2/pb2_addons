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
        'base',
        'sale',
        'pabi_readonly_group',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/pabi_security_group.xml',
        'views/pabi_security_view.xml',
        'xlsx_template/templates.xml',
        'xlsx_template/xlsx_template_wizard.xml',
        'xlsx_template/load_template.xml',
    ],
}
