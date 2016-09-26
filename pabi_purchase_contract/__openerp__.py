# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - Purchase Contract",
    "summary": "Pabi2 Purchase Contract",
    "version": "8.0.1.0.0",
    "category": "Purchase",
    "description": """

PABI2 - Purchase Contract Module
==================================


    """,
    "website": "https://nstda.or.th/",
    "author": "Jakkrich.Cha",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        'base',
        'mail',
        'purchase_requisition',
    ],
    "data": [
        'security/module_data.xml',
        'security/purchase_contract_security.xml',
        'security/ir.model.access.csv',
        'data/purchase.contract.collateral.csv',
        'data/purchase.contract.type.csv',
        'wizard/purchase_contract_reason.xml',
        'views/purchase_contract.xml',
        'views/purchase_contract_type.xml',
        'views/purchase_contract_menu_item.xml',
        'views/purchase_contract_view.xml',
        'views/purchase_requisition_view.xml',
    ],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
