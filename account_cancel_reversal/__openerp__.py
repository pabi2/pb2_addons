# -*- coding: utf-8 -*-
{
    'name': 'Account Cancel Reversal',
    'version': '1.0',
    'author': 'Ecosoft',
    'summary': 'Cancel Invoice / Voucher by create reversed journal entry',
    'description': """

This module put more accounting control into invoice cancellation.

As-Is:

* Set invoice state to cancel
* Delete all related journal (account posting)

To-Be:

* Set invoice state of the invoice to cancel.
* Create new counter invoice also with state cancel.
* Create journal entry same as original document, but switch debit <-> credit
* Name the new document <old_number>_VOID
* Set to Draft button, to always create new Invoice(s)
** With DO reference, create invoice from DO
** WIthout DO reference, create invoice from copy the existing invoice

    """,
    'category': 'Accounting',
    'website': 'http://www.ecosoft.co.th',
    'images': [],
    'depends': [
        'account',
        'account_voucher',
        'account_cancel',
        'account_invoice_cancel_hooks',
        'account_voucher_cancel_hooks',
        'account_bank_receipt',
    ],
    'demo': [],
    'data': [
        'views/voucher_payment_receipt_view.xml',
        'views/account_invoice_view.xml',
    ],
    'test': [
    ],
    'auto_install': False,
    'application': True,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
