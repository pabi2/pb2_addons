# -*- coding: utf-8 -*-
{
    'name': 'Purchase Invoice Plan',
    'version': '1.0',
    'author': 'Ecosoft',
    'summary': 'Purchase Invoice Plan',
    'description': """
Purchase Invoice Plan
    """,
    'category': 'Accounting',
    'website': 'http://www.ecosoft.co.th',
    'images': [],
    'depends': [
        'purchase',
        'purchase_invoice_line_percentage'
    ],
    'demo': [],
    'data': [
        'wizard/create_invoice_view.xml',
        'wizard/purchase_create_invoice_plan_view.xml',
        'views/purchase_view.xml',
        'security/ir.model.access.csv'
    ],
    'test': [
    ],
    'auto_install': False,
    'application': True,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
