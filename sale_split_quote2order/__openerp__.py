# -*- coding: utf-8 -*-

{
    'name': 'Sales - Separate Quote and Order',
    'version': '1.0',
    'author': 'Ecosoft',
    'category': 'Sales',
    'description': """

This module separate quotation and sales order
by adding type (quotation, sale_order) in sale.order.

Quotation will reduce to have only 2 state, Draft and Done.
Sales Order will also has a Force Done option.

    """,
    'website': 'http://ecosoft.co.th',
    'depends': ['sale',
                'sale_stock',
                ],
    'data': [
        "sale_sequence.xml",
        "sale_workflow.xml",
        "sale_view.xml",
        "res_partner_view.xml",
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
