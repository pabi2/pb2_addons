# -*- coding: utf-8 -*-
{
    "name": "Migration Scripts",
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
        'pabi_purchase_invoice_plan',
        'purchase_request',
        'pabi_asset_management',
        'pabi_budget_plan',
        'pabi_purchase_billing',
        'pabi_invest_construction',
        'pabi_sale_invoice_plan',
        'pabi_loan_receivable',
        'pabi_loan_installment',
        'stock_account',
    ],
    "data": [
        'views/purchase_view.xml',
        'views/sale_view.xml',
        'views/stock_view.xml',
    ]
}
