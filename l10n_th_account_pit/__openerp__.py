# -*- coding: utf-8 -*-

{
    'name': "Personal Income Tax",
    'summary': "Calculate Personnal Income Tax",
    'author': "Ecosoft",
    'website': "http://ecosoft.co.th",
    'category': 'Account',
    'version': '0.1.0',
    'depends': [
        'l10n_th_account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_pit_view.xml',
        'views/voucher_payment_receipt_view.xml',
        'views/res_partner_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
