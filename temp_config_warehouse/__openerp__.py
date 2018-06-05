# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: Temp Config Warehouse",
    "summary": "",
    "version": "8.0.1.0.0",
    "category": "Uncategorized",
    "description": """
    """,
    "website": "https://nstda.or.th/",
    "author": "Kitit U.,",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'account',
        'stock_account_operating_unit',
        'pabi_pos',
    ],
    "data": [

        "warehouse/data/ir_sequence.xml",
        "warehouse/data/stock.warehouse.csv",
        "warehouse/data2/delete_default_location.xml",
        "warehouse/data/stock.location.csv",
        "warehouse/data/stock.picking.type.csv",
        "warehouse/data/procurement.rule.csv",
        "warehouse/data2/stock.warehouse.csv",
        "warehouse/data2/delete.xml",
        "warehouse/data2/update_warehouse.xml",

    ]
}
