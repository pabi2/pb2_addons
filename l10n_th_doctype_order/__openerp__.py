# -*- coding: utf-8 -*-
{
    "name": "Sequence Number by Document Type for Orders",
    "summary": "",
    "version": "8.0.1.0.0",
    "category": "Accounting & Finance",
    "description": """

New menu, > Settings > Technical > Sequences & Identifiers > Doctype

List of Doctype

* Sales Quotation
* Purchase Quotation
* Sales Order
* Purchase Order

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'l10n_th_doctype_base',
        'sale', 'purchase',
        'sale_split_quote2order',
        'purchase_split_quote2order',
    ],
    "data": [
        "data/ir_sequence_data.xml",
        "data/doctype_data.xml",
    ],
}
