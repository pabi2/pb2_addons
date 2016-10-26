# -*- coding: utf-8 -*-
{
    'name': 'Purchase Invoice Plan Retention',
    'version': '1.0',
    'author': 'Ecosoft',
    'category': 'Sales',
    'description': """

This module is based on Purchase Invoice Plan. It allows user to add retention
amount into each invoice being created.

The retention amount will then be deducted from the Total after tax amount of
an invoice.

3 Retention Type available,
===========================

1) Before VAT (%)
2) After VAT (%)
3) Fixed Amount

    """,
    'website': 'www.ecosoft.co.th',
    'depends': ['purchase_invoice_plan', 'l10n_th_account'],
    'data': [
        "wizard/purchase_create_invoice_plan_view.xml",
        "views/purchase_view.xml",
        "views/account_invoice_view.xml",
    ],
    'qweb': [
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
