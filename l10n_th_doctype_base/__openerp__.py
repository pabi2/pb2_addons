# -*- coding: utf-8 -*-
{
    "name": "Sequence Number by Document Type (Base Module)",
    "summary": "",
    "version": "8.0.1.0.0",
    "category": "Accounting & Finance",
    "description": """

New menu, > Settings > Technical > Sequences & Identifiers > Doctype

Overwrite standard documment seqeunce by what what is specified in Doctype

This module provide only basis infrastructure.

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'l10n_th_fields',
        'account_auto_fy_sequence',
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/doctype_view.xml",
        "views/ir_sequence_view.xml",
    ],
}
