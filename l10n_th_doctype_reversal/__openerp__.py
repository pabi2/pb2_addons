# -*- coding: utf-8 -*-
{
    "name": "Sequence Number for Cancel with Reversal Case",
    "summary": "",
    "version": "8.0.1.0.0",
    "category": "Accounting & Finance",
    "description": """

Extension for case Cancel with Reversal (account_cancel_reversal)

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'l10n_th_doctype_invoice',
        'l10n_th_doctype_voucher',
        'l10n_th_doctype_bank_receipt',
        'account_cancel_reversal',
    ],
    "data": [
        "data/ir_sequence_data.xml",
        "data/doctype_data.xml",
        "views/doctype_view.xml",
        "views/account_view.xml",
    ],
}
