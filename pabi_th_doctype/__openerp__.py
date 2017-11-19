# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Sequence Number by Document Type",
    "summary": "",
    "version": "8.0.1.0.0",
    "category": "Accounting & Finance",
    "description": """

PABI2 Extension to l10n_th_doctype for,

* Purchase Requisition
* Work Acceptance
* Approval Report
* Stock Request
* Stock Transfer
* Stock Borrow
* Payment Export
* Interface Account

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'l10n_th_doctype_base',
        'l10n_th_doctype_reversal',
        'pabi_purchase_work_acceptance',
        'stock_request',
        'pabi_procurement',
        'payment_export',
        'pabi_interface',
        'purchase_requisition',
        'pabi_advance_dunning_letter',
        'pabi_asset_management',
        'pabi_loan_installment',
        'pabi_bank_statement_reconcile',
        'pabi_purchase_billing',
    ],
    "data": [
        "data/ir_sequence_data.xml",
        "data/doctype_data.xml",
    ],
}
