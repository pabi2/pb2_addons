# -*- coding: utf-8 -*-
{
    'name': 'Asynchronous Actions',
    'version': '8.0.1.0.0',
    'author': 'Kitti U. (Ecosoft)',
    'license': 'AGPL-3',
    'category': 'Generic Modules',
    'depends': [
        'connector',
        'purchase_invoice_plan',
        'pabi_procurement',
        'pabi_th_tax_report',
    ],
    'data': [
        'views/my_queue_job_view.xml',
        'action_purchase_create_inovice/create_invoice_view.xml',
        'report_tax_report/tax_report_wizard.xml',
    ],
    'installable': True,
    'application': False,
}
