# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - WH/LOC Config",
    "summary": "Configure Warehouse and Location",
    "version": "1.0",
    "category": "Uncategorized",
    "description": """

Load 3 data: Warehouses, Locations, Picking Types

Note:

* This module will be used only with no Demo data (it conflicts)
* Currently this module is marked as uninstallable

    """,
    "website": "https://nstda.or.th/",
    "author": "Kitit U.,",
    "license": "AGPL-3",
    "application": False,
    "installable": False,  # conflict with demo database
    "depends": [
        "purchase",
        "stock",
        "stock_operating_unit",
        "pabi_base",
    ],
    "data": [
        "data/ir.sequence.csv",
        "data/stock.warehouse.csv",
        "data/stock.location.csv",
        "data/stock.picking.type.csv",
        "data/procurement.rule.csv",
        "data2/stock.warehouse.csv",
        "data2/delete.xml",
    ],
}
