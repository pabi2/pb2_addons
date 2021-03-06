# -*- coding: utf-8 -*-
{
    "name": "NSTDA :: PABI2 - PO Contract",
    "summary": "Pabi2 PO Contract",
    "version": "8.0.1.0.0",
    "category": "Purchase",
    "description": """

PABI2 - PO Contract Module
==================================

1) Purchase User -> Creator of document, see own OU
2) Finance User -> Readonly on most field, can edit only some field **
   (may need OCA access addon?)

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
        'security/security_group.xml',
        'security/security_rule.xml',
        'security/ir.model.access.csv',
        'data/purchase.contract.collateral.csv',
        'data/purchase.contract.type.csv',
        'wizard/purchase_contract_reason.xml',
        'views/purchase_contract_view.xml',
        'views/purchase_requisition_view.xml',
    ],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
