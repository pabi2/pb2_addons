# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Stock",
    "summary": "Pabi2 Stock",
    "version": "8.0.1.0.0",
    "category": "Warehouse",
    "description": """

PABI2 - Stock Module
====================

  * Add fields for PABI2 stock processes.
  * Fix some functions from processes interaction


    """,
    "website": "https://nstda.or.th/",
    "author": "Ecosoft",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'stock',
        'stock_asset',
        "stock_operating_unit",
    ],
    "data": [
        "views/stock_view.xml",
    ],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
