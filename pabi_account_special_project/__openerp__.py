# -*- coding: utf-8 -*-
{
    'name': 'PABI2 :: Special Project Imort/Export',
    'version': '8.0.1.0.0',
    'author': 'Ecosoft',
    'summary': 'Import/Export with account mapping',
    'description': """

    """,
    'category': 'Accounting',
    'website': 'http://www.ecosoft.co.th',
    'images': [],
    'depends': [
        'account',
        'pabi_utils',
    ],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'xlsx_template/templates.xml',
        'wizard/import_xlsx_special_project_wizard.xml',
        'views/account_view.xml',
    ],
    'test': [
    ],
    'auto_install': False,
    'application': True,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
