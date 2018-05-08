# -*- coding: utf-8 -*-

{
    'name': "Purchase - Split Call for Bids Line",
    'summary': "Allow splitting call for bids line to multiple lines",
    'author': "Ecosoft",
    'website': "http://ecosoft.co.th",
    'category': 'Purchase',
    "license": "AGPL-3",
    "version": "8.0.1.0.0",
    'depends': [
        'purchase_request_to_requisition',
    ],
    'data': [
        'wizard/purchase_requisition_line_split_view.xml',
        'views/purchase_requisition_view.xml',
    ],
    "application": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
