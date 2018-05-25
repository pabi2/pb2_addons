# -*- coding: utf-8 -*-

{
    'name': 'NSTDA :: PABI2 - Purchase Invoice Plan',
    'version': '8.0.1.0.0',
    'author': 'Ecosoft',
    'website': 'http://ecosoft.co.th',
    'depends': [
        'purchase',
        'purchase_invoice_plan',
        'purchase_action_invoice_create_hook',
        'pabi_chartfield',
        'pabi_asset_management',
        'pabi_purchase_work_acceptance',
    ],
    "description": """
    Purchase invoice plan by fiscal year
    """,
    'data': [
        'views/purchase_view.xml',
        'views/account_config.xml',
        'wizard/purchase_create_invoice_plan_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
