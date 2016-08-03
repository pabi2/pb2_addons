# -*- coding: utf-8 -*-
{
    "name": "Payment Export Pack",
    "version": "8.0.0.1.0",
    "license": 'AGPL-3',
    "author": "Ecosoft",
    "category": "Accounting & Finance",
    "depends": [
        "account_voucher",
    ],
    "description": """

    """,
    "data": [
        "data/payment_export_sequence.xml",
        "security/ir.model.access.csv",
        "views/account_bank_view.xml",
        "views/payment_export_view.xml",
        "views/cheque_lot_view.xml",
        "views/voucher_payment_receipt_view.xml",
    ],
    'installable': True,
}
