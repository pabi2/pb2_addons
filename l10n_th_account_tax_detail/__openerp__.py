# -*- coding: utf-8 -*-

{
    'name': "Invoice Tax Detail",
    'summary': "Allow editing tax table in detail",
    'author': "Ecosoft",
    'website': "http://ecosoft.co.th",
    'category': 'Account',
    'version': '0.1.0',
    'depends': [
        'account',
        'l10n_th_account',
        'account_invoice_check_tax_lines_hook',
    ],
    'data': [
        'data/config_data.xml',
        'security/ir.model.access.csv',
        'wizard/account_tax_detail_view.xml',
        'views/account_view.xml',
        'views/account_invoice_view.xml',
        'views/account_voucher_view.xml',
        'views/account_config.xml',
    ],
    'demo': [
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
