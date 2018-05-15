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

    """,
    "website": "https://nstda.or.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "depends": [
        'l10n_th_account',
        'hr_expense_advance_clearing',
    ],
    "data": [
    ],
    "application": False,
    "installable": True,
}
