# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI Apps Configuration",
    "summary": "",
    "version": "1.0",
    "category": "Tools",
    "description": """

PABI Odoo Configuration Menu in Settings,
as separated menu from normal setting.

This module sits on top of other modules whose configuration is moved here.

* res_partner_ext
* purchase_invoice_line_percentage
* sale_invoice_line_percentage
* hr_expense_advance_clearing
* l10n_th_account_tax_detail
* l10n_th_account
* pabi_account
* pabi_purchase_work_acceptance
* pabi_purchase_billing
* pabi_ar_late_payment_penalty
* pabi_loan_receivable
* pabi_advance_dunning_letter
* pabi_loan_installment
* pabi_long_term_investment_report

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'res_partner_ext',
        'purchase_invoice_line_percentage',
        'sale_invoice_line_percentage',
        'hr_expense_advance_clearing',
        'l10n_th_account_tax_detail',
        'l10n_th_account',
        'pabi_account',
        'pabi_purchase_work_acceptance',
        'pabi_purchase_billing',
        'pabi_ar_late_payment_penalty',
        'pabi_loan_receivable',
        'pabi_advance_dunning_letter',
        'pabi_long_term_investment_report',
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/pabi_user_setting.xml',
        'views/pabi_apps_config.xml',
        'views/pabi_menu_config.xml',
        'views/pabi_menu_system.xml',
        'scripts/del_lang_th.xml',
    ],
}
