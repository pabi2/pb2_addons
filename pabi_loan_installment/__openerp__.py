# -*- coding: utf-8 -*-
{
    'name': 'NSTDA :: PABI2 - Loan Installment',
    'summary': 'Convert trade receivable to loan installment receivable',
    'version': '8.0.1.0.0',
    'category': 'Accounting & Finance',
    'description': """

    """,
    'website': 'https://ecosoft.co.th/',
    'author': 'Kitti U.',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'l10n_th_account',
        'sale_invoice_plan',
        'pabi_base',
        'pabi_account_move_adjustment',
        'account_cancel_reversal',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'wizard/loan_create_payment_wizard.xml',
        'views/account_config.xml',
        'views/loan_installment_view.xml',
    ],
}
