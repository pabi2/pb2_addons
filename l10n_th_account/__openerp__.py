# -*- coding: utf-8 -*-

{
    'name': "Undue Tax, Withholding Tax, Retention",
    'summary': "Added support for undue Tax, Withholding Tax and Retention",
    'author': "Ecosoft",
    'website': "http://ecosoft.co.th",
    'category': 'Account',
    'version': '0.1.0',
    'depends': [
        'l10n_th_fields',
        'account',
        'account_voucher',
        'account_voucher_action_move_line_create_hooks',
    ],
    'data': [
        'views/account_view.xml',
        'wizard/print_wht_cert_wizard.xml',
        'views/res_partner_view.xml',
        'views/account_invoice_view.xml',
        'views/voucher_payment_receipt_view.xml',
        'views/account_config.xml',
        'security/ir.model.access.csv',
        'data/report_data.xml',
    ],
    'demo': [
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
