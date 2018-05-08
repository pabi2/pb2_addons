# -*- coding: utf-8 -*-
{
    "name": "Stock Request",
    "summary": "",
    "version": "8.0.1.0.0",
    "category": "Warehouse",
    "description": """

    """,
    "website": "https://ecosoft.co.th/",
    "author": "Kitti U.",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock",
    ],
    "data": [
        "data/stock_request_sequence.xml",
        "security/ir.model.access.csv",
        "views/stock_request_view.xml",
        "views/stock_view.xml",
    ],
}
