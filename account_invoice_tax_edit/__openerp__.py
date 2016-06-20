# -*- coding: utf-8 -*-

{
    'name': "Invoice Manual Tax Table",
    'summary': "Allow splitting tax table to multiple lines",
    'author': "Ecosoft",
    'website': "http://ecosoft.co.th",
    'category': 'Account',
    'version': '0.1.0',
    'depends': [
        'account',
        'account_invoice_check_tax_lines_hook',
    ],
    'data': [
        'wizard/account_invoice_tax_split_view.xml',
        'views/account_invoice_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
