# -*- coding: utf-8 -*-
{
    'name': 'NSTDA :: PABI2 Readonly Groups',
    'summary': """
Readonly for following models,

- Expense
- Sales Order
- Purchase Request
- Purchase Requisition
- Purchase order
- Invoice
- Payment
- Budget Plan (all 5 structure)
- Budget Control

    """,
    'author': 'Kitti U.',
    'website': 'http://ecosoft.co.th',
    'category': 'Tools',
    'version': '8.0.1.0.0',
    'depends': [
        'sale',
        'purchase',
        'purchase_request',
        'purchase_requisition',
        'account',
        'account_voucher',
        'hr_expense',
        'account_budget_activity',
        'pabi_budget_plan',
        'pabi_purchase_billing',
        'pabi_purchase_work_acceptance',
    ],
    'data': [
        'security/readonly_group.xml',
    ],
    'demo': [
    ],
    'installable': True,
}
