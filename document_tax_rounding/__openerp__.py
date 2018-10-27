# -*- coding: utf-8 -*-
{
    'name': 'Document Tax Rounding',
    'version': '1.0',
    'author': 'Ecosoft',
    'summary': """

Change tax rounding method per document for PO and INV

    """,

    'category': 'Accounting',
    'website': 'http://www.ecosoft.co.th',
    'images': [],
    'depends': [
        'purchase',
        'account',
    ],
    'demo': [],
    'data': [
        'views/purchase_view.xml',
        'views/account_invoice_view.xml',
    ],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
