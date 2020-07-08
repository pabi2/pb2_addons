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
        'account',
        'account_voucher',
        'base',
        'sale',
        'pabi_readonly_group',
        'l10n_th_account_deduction',
        'account_bank_receipt',
        'account_bank_receipt_deduction',
        'pabi_budget_plan',
        'pabi_bank_statement_reconcile',
    ],
    'data': [
        'security/pabi_security_group.xml',
        'security/ir.model.access.csv',
        'views/pabi_security_view.xml',
        'xlsx_template/templates.xml',
        'xlsx_template/xlsx_template_wizard.xml',
        'xlsx_template/load_template.xml',
    ],
}
