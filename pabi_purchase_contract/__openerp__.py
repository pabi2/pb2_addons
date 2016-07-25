# -*- coding: utf-8 -*-
{
    'name': "PABI Purchase Contract",
    'description': """NSTDA PO Contract
     - Design Class/View
    """,
    'author': 'Jakkrich.cha',
    'category': 'NSTDA',
    'depends': ['base',
                'mail',
                'nstdaperm',
                'nstdamas',
                ],
    'data': [
            'security/ir.model.access.csv',
            'data/purchase.contract.collateral.csv',
            'data/purchase.contract.type.csv',
            'data/nstdamas.org.csv',
            'wizard/purchase_contract_reason.xml',
            'views/purchase_contract.xml',
            'views/purchase_contract_type.xml',
            'views/purchase_contract_menu_item.xml',
            'views/purchase_contract_view.xml'],
    'qweb': [],
    'css': [],
    'js': [],
    'installable': True,
}
