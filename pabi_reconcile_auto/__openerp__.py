# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Reconcile Auto",
    "summary": "Auto reconcile open item in various cases",
    "version": "1.0",
    "category": "Hidden",
    "description": """
By Odoo standard, only receivable/payable is reconciled when invoice->payment,
reconcilation also extened for all reconcilable account,
* Invoice -> Payment
* Interface Account for Invoice -> Payment (NO USE, moved to pabi_interface)

For more specific reconcilation event, we are using new auto_reconcile_id,
in which, if documents are deemed to be related they will be marked with same
auto_reconcile_id. Mostly, will be grouped by source document.

Currently we have done for following events,
* HR Expense Advance -> Clearing/Return (use Advance document as auto_id)
* Inv Plan Adv/Deposit -> Cleared by following invoices (SO/PO as auto_id)
* GR/IR -> clearing between Picking and Invoice (SO/PO as auto_id)
* Cash On Delivery -> Clear when clear prepaid account (PO as auto_id)
* Recurring -> Clear when Auto Reverse (Original JE as auto_ids)
* Return Retention on PO -> Clear CV's retention with KV's when KV is validated
                            (PO as auto_id)
* Loan Installment -> Reconcile Supplier Payment (loan installment account) w/
                      Customer Invoice

    """,
    "website": "https://nstda.or.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "depends": [
        'l10n_th_account',
        'hr_expense_advance_clearing',
        'pabi_interface',
        'account_subscription_enhanced',
        'pabi_account_retention',
        'pabi_loan_receivable',
    ],
    "data": [
        "security/ir.model.access.csv",
    ],
    "application": False,
    "installable": True,
}
