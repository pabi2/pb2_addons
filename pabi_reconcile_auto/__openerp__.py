# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Reconcile Auto",
    "summary": "Auto reconcile open item in various cases",
    "version": "1.0",
    "category": "Hidden",
    "description": """
By Odoo standard, only receivable/payable is reconciled when invoice->payment

This module make sure that other reconcilable account is also reconciled,
  * Invoice -> Payment, for Undue -> Due Taxes
  * HR Expense Advance -> Clearing
  * Account Interface, for Undue -> Due Taxes
  * Invoice Plan's Advance/Deposit -> Clearing on folloing invoice
    """,
    "website": "https://nstda.or.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "depends": [
        'l10n_th_account',
        'hr_expense_advance_clearing',
        'pabi_interface',
    ],
    "data": [
    ],
    "application": False,
    "installable": True,
}
